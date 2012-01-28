import time
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from positions.fields import PositionField
from undelete.models import Trashable
from django.dispatch import receiver
from django.db.models.signals import post_save
#from undelete.signals import pre_trash, pre_restore

#TODO: Replace with a manager
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
            return self.subscriptions.filter(trashed_at__isnull=True,
                    user=user)[0]
        except IndexError:
            return None
    def as_dict(self, include_items=True):
        rep = {'id':self.id, 'name':self.name, 'owner_id':self.owner_id }
        if include_items:
            rep['items'] = dict([(i.id,i.as_dict())
                for i in self.nontrashed_items().order_by()])
        return rep
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

    def is_on_subscribed_list(self, user):
        "Return true iff the item is on a list that the user is subscribed to."
        return self.list.subscription_for(user) != None

    def as_dict(self):
        return {'id':self.id, 'list_id':self.list_id, 'text':self.text,
                'url':self.url, 'priority':self.priority,
                'position':self.position}
    def __unicode__(self):
        val = self.list.name+": "+self.text
        if self.trashed_at:
            val += " (trashed)"
        return val

class ItemFrequencyManager(models.Manager):
    def increment(self, text):
        """Increment the frequency of the given text if it exists or create a
        new ItemFrequency with frequency=1. Returns the ItemFrequency object."""
        text = text.lower().strip()
        try:
            freq = self.get(text=text)
            freq.frequency += 1
            freq.save()
            return freq
        except ItemFrequency.DoesNotExist:
            return self.create(text=text, frequency=1)
    def frequent_list(self, limit=None):
        """ Return the most frequent texts, most frequent first"""
        return list(self.all().order_by('-frequency')[:limit] \
                .values_list('text', flat=True))
class ItemFrequency(models.Model):
    """
    Info about frequency of a certain Item text. Used for item suggestions.
    """
    text = models.CharField(max_length=200, primary_key=True)
    frequency = models.PositiveIntegerField()
    last_changed = models.DateTimeField(auto_now=True)

    objects = ItemFrequencyManager()

    class Meta:
        ordering = ['-frequency']

    def __unicode__(self):
        return '%s: %d' % (self.text, self.frequency)
@receiver(post_save, sender=Item)
def autoincrement_on_item_creation(sender, **kwargs):
    "Detect Item creation and increment its text's frequency."
    if kwargs['created']:
        ItemFrequency.objects.increment(kwargs['instance'].text)

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
    def create_patch(cls, from_time, user):
        changes = cls.objects.newer_than(from_time)
        t = LogEntry.objects.latest().time
        timestamp = time.mktime(t.timetuple()) + t.microsecond/1000000.
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


#@receiver(post_save)
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

#@receiver(pre_trash)
def detect_trash(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    kwargs['instance'].update_is_trash = True

#@receiver(pre_restore)
def detect_restore(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    kwargs['instance'].update_is_restore = True
