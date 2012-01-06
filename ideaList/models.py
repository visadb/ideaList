from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from positions.fields import PositionField
from undelete.models import Trashable
from undelete.signals import pre_trash, pre_restore

def _nontrash_subscriptions_of_user(self):
    return self.subscriptions.filter(
            trashed_at__isnull=True, list__trashed_at__isnull=True)
User.nontrash_subscriptions = _nontrash_subscriptions_of_user

class List(Trashable):
    """
    A list of items (:model:`ideaList.Item`).
    """
    name = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, related_name='lists_owned')
    subscribers = models.ManyToManyField(User,
            related_name='subscribed_lists', through='Subscription')
    def nontrashed_items(self):
        return self.items.filter(trashed_at__isnull=True)
    def n_items(self):
        return self.items.count()
    n_items.short_description = u'# of items'
    def subscription_for(self, user):
        try:
            return self.subscriptions.filter(user=user)[0]
        except IndexError:
            return None
    def as_dict(self):
        return {'id':self.id, 'name':self.name, 'owner_id':self.owner_id,
                'items': [i.as_dict() for i in self.nontrashed_items()]}
    def __unicode__(self):
        val = self.name
        if self.trashed_at:
            val += " (trashed)"
        return val

class Item(Trashable):
    """
    A list item (:model:`ideaList.List`)
    """
    list = models.ForeignKey(List, related_name='items')
    text = models.CharField(max_length=200)
    url = models.URLField(blank=True, default="")
    PRIORITY_CHOICES = (
            (u'HI',u'High'),
            (u'NO',u'Normal'),
            (u'LO',u'Low'),
    )
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES,
            default=u'NO')
    position = PositionField(collection='list', default=-1)
    last_changed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    def as_dict(self):
        return {'id':self.id, 'list_id':self.list_id, 'text':self.text,
                'url':self.url, 'priority':self.priority,
                'position':self.position}
    def __unicode__(self):
        val = self.list.name+": "+self.text
        if self.trashed_at:
            val += " (trashed)"
        return val

class Subscription(Trashable):
    """
    A user's (:model:`django.contrib.auth.User`) subscription of a certain List
    (:model:`ideaList.List`)
    """
    user = models.ForeignKey(User, related_name='subscriptions')
    list = models.ForeignKey(List, related_name='subscriptions')
    minimized = models.BooleanField(default=False)
    position = PositionField(collection='user', default=-1)

    class Meta:
        ordering = ['position']
        unique_together = (('user','list'),)

    def as_dict(self):
        return {'id':self.id, 'user_id':self.user_id,
                'list':self.list.as_dict(), 'minimized': self.minimized,
                'position': self.position}
    def __unicode__(self):
        val = self.user.first_name+": "+self.list.name
        if self.trashed_at:
            val += " (trashed)"
        return val

### Change log stuff: ###
class LogEntryManager(models.Manager):
    ''' Query only objects which have not been trashed. '''
    def newer_than(self, time):
        if isinstance(time, float) or isinstance(time, int):
            dt = datetime.fromtimestamp(time)
        if isinstance(time, datetime):
            dt = time
        return self.filter(time__gt=dt)

class LogEntry(models.Model):
    """
    Keeps track of changes to ideaList data.
    """
    ADD = 1
    UPDATE = 2
    DELETE = 3
    UNDELETE = 4
    objects = LogEntryManager()
    content_type = models.ForeignKey(ContentType, related_name='log_entries')
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    CHANGE_TYPE_CHOICES = (
            (ADD,u'Add'),
            (UPDATE,u'Update'),
            (DELETE,u'Delete'),
            (UNDELETE,u'Undelete'),
    )
    change_type = models.SmallIntegerField(choices=CHANGE_TYPE_CHOICES)
    time = models.DateTimeField(db_index=True, auto_now_add=True)
    #user = models.ForeignKey(User, related_name='changes', null=True)
    class Meta:
        ordering = ['time']
        get_latest_by = 'time'
    @classmethod
    def create_patch(cls, time, user):
        changes = cls.objects.newer_than(time)
        time = LogEntry.objects.latest().time
        timestamp = time.mktime(time.timetuple()) + time.microsecond/1000000.
        insts = filter(None, [c.client_instruction(user) for c in changes])
        return {'timestamp': timestamp, 'instructions': insts }

    def client_instruction(self, user):
        """
        Returns all information required by the client to display the change.
        Returns None if nothing is required.
        """
        def action_string():
            if self.change_type in (LogEntry.ADD,LogEntry.UNDELETE):
                return 'add'
            elif self.change_type == LogEntry.UPDATE:
                return 'update'
            else:
                return 'remove'
        if self.content_type.name == 'item':
            s = self.content_object.list.subscription_for(user)
            if s is None:
                return None
            return {'content_type':'subscription',
                    'action':'update',
                    'object':s.as_dict()}
        elif self.content_type.name in ('list', 'subscription'):
            if self.content_type.name == 'list':
                if self.change_type == LogEntry.ADD:
                    return None
                s = self.content_object.subscription_for(user)
                if not s:
                    return None
                if self.change_type == LogEntry.DELETE:
                    obj = {'id': s.id}
                else:
                    obj = s.as_dict()
            else: #content_type is subscription
                if self.content_object.user != user:
                    return None
                if self.change_type == LogEntry.DELETE:
                    obj = {'id': self.object_id}
                else:
                    obj = self.content_object.as_dict()
            return {'content_type':'subscription',
                    'action':action_string(),
                    'object':obj}

    def __unicode__(self):
        return self.change_type_string()+" "+\
                self.content_type.name+": "+self.content_object.__unicode__()

    def change_type_string(self):
        return type(self).change_type_to_string(self.change_type)
    @classmethod
    def change_type_to_string(cls, change_type):
        return dict(cls.CHANGE_TYPE_CHOICES)[change_type].lower()


@receiver(post_save)
def detect_change(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    if kwargs['created']:
        change_type = LogEntry.ADD
    elif hasattr(kwargs['instance'], 'update_is_trash'):
        change_type = LogEntry.DELETE
        delattr(kwargs['instance'], 'update_is_trash')
    elif hasattr(kwargs['instance'], 'update_is_restore'):
        change_type = LogEntry.UNDELETE
        delattr(kwargs['instance'], 'update_is_restore')
    else:
        change_type = LogEntry.UPDATE
    c = LogEntry(content_object=kwargs['instance'],
            change_type=change_type)
    c.save()

@receiver(pre_trash)
def detect_trash(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    kwargs['instance'].update_is_trash = True

@receiver(pre_restore)
def detect_restore(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    kwargs['instance'].update_is_restore = True

