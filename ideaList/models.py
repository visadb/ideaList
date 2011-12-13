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
#from django.utils import unittest
from django import test

def _subscriptions_of_nontrashed_lists(self):
    return self.subscriptions.filter(list__trashed_at__isnull=True)
User.subscriptions_of_nontrashed_lists = _subscriptions_of_nontrashed_lists

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
    def as_dict(self):
        return {'id':self.id, 'name':self.name, 'owner_id':self.owner_id,
                'items': [i.as_dict() for i in self.nontrashed_items()]}
    def __unicode__(self):
        val = self.name
        if self.trashed_at:
            val += " (trashed)"
        return val
class ListTest(test.TestCase):
    def setUp(self):
        self.u = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u)
    def test_fields(self):
        self.assertTrue(List.objects.count() >= 1)
        l = List.objects.all()[0]
        self.assertEqual(l.name, 'List1')
        self.assertEqual(l.owner, self.u)
        self.assertEqual(l.subscribers.count(), 0)
    def test_nontrashed_items(self):
        self.assertEqual(self.l1.nontrashed_items().count(), 0)
        i = Item.objects.create(list=self.l1, text="testitem")
        self.assertEqual(self.l1.nontrashed_items().count(), 1)
        self.assertEqual(self.l1.nontrashed_items()[0].text, 'testitem')
        i.delete()
        self.assertEqual(self.l1.nontrashed_items().count(), 0)

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
class ItemTest(test.TestCase):
    def setUp(self):
        self.u = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u)
        self.i1 = Item.objects.create(list=self.l1, text='testitem')
    def test_fields(self):
        self.assertTrue(Item.objects.count() >= 1)
        i = Item.objects.all()[0]
        self.assertEqual(i.list, self.l1)
        self.assertEqual(i.text, 'testitem')
        self.assertEqual(i.url, '')
        self.assertEqual(i.priority, u'NO')
        self.assertEqual(i.position, 0)

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
        return self.user.first_name+": "+self.list.name
class SubscriptionTest(test.TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s = Subscription.objects.create(user=self.u1,list=self.l1)
    def test_fields(self):
        self.assertTrue(Subscription.objects.count() >= 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.user, self.u1)
        self.assertEqual(s.list, self.l1)
        self.assertEqual(s.minimized, False)
        self.assertEqual(s.position, 0)

### Change log stuff: ###

@receiver(post_save)
def detect_add_and_update(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    if kwargs['created']:
        change_type = ADD
    elif hasattr(kwargs['instance'], 'update_is_trash'):
        change_type = DELETE
        delattr(kwargs['instance'], 'update_is_trash')
    elif hasattr(kwargs['instance'], 'update_is_restore'):
        change_type = UNDELETE
        delattr(kwargs['instance'], 'update_is_restore')
    else:
        change_type = UPDATE
    c = LogEntry(content_object=kwargs['instance'],
                  change_type=change_type,
                  time=datetime.now())
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

ADD = 1
UPDATE = 2
DELETE = 3
UNDELETE = 4

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
    time = models.DateTimeField(db_index=True)
    class Meta:
        ordering = ['time']
    #user = models.ForeignKey(User, related_name='changes', null=True)
    def __unicode__(self):
        return dict(self.CHANGE_TYPE_CHOICES)[self.change_type]+" "+\
                self.content_type.name+": "+self.content_object.__unicode__()

class LogTest(test.TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.setup_time = datetime.now()
    def test_newer_than(self):
        self.assertEqual(LogEntry.objects.newer_than(self.setup_time).count(),0)
        self.l = List.objects.create(name='List1', owner=User.objects.all()[0])
        d2 = datetime.now()
        self.assertEqual(LogEntry.objects.newer_than(self.setup_time).count(),1)
        self.assertEqual(LogEntry.objects.newer_than(d2).count(),0)

class ListLogTest(test.TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.setup_time = datetime.now()
        super(ListLogTest, self).setUp()
        self.assertEqual(LogEntry.objects.count(), 0)
        self.l = List.objects.create(name='List1', owner=User.objects.all()[0])
        self.assertEqual(LogEntry.objects.count(), 1)
    def test_list_add(self):
        cl = LogEntry.objects.all()[0]
        self.assertIs(List, cl.content_type.model_class())
        self.assertEqual(self.l, cl.content_object)
        self.assertEqual(cl.change_type, ADD)
        self.assertTrue(cl.time >= self.setup_time)
    def test_list_update(self):
        self.l.name = 'List2'
        self.l.save()
        self.assertEqual(LogEntry.objects.count(), 2)
        updates = LogEntry.objects.filter(change_type=UPDATE)
        self.assertEqual(updates.count(), 1)
        cl = updates[0]
        self.assertIs(List, cl.content_type.model_class())
        self.assertEqual(self.l, cl.content_object)
        self.assertEqual(cl.change_type, UPDATE)
        self.assertTrue(cl.time >= self.setup_time)
    def test_list_delete(self):
        self.l.delete()
        self.assertEqual(LogEntry.objects.count(), 2)
        deletes = LogEntry.objects.filter(change_type=DELETE)
        self.assertEqual(deletes.count(), 1)
        cl = deletes[0]
        self.assertIs(List, cl.content_type.model_class())
        self.assertEqual(self.l, cl.content_object)
        self.assertEqual(cl.change_type, DELETE)
        self.assertTrue(cl.time >= self.setup_time)
    def test_list_undelete(self):
        self.l.delete()
        self.assertEqual(LogEntry.objects.count(), 2)
        self.l.restore()
        self.assertEqual(LogEntry.objects.count(), 3)
        undeletes = LogEntry.objects.filter(change_type=UNDELETE)
        self.assertEqual(undeletes.count(), 1)
        cl = undeletes[0]
        self.assertIs(List, cl.content_type.model_class())
        self.assertEqual(self.l, cl.content_object)
        self.assertEqual(cl.change_type, UNDELETE)
        self.assertTrue(cl.time >= self.setup_time)
