from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from positions.fields import PositionField
from undelete.models import Trashable

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
    def __unicode__(self):
        val = self.name
        if self.trashed_at:
            val += " (trashed)"
        return val
    n_items.short_description = u'# of items'

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

    def __unicode__(self):
        val = self.list.name+": "+self.text
        if self.trashed_at:
            val += " (trashed)"
        return val

class Subscription(models.Model):
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

    def __unicode__(self):
        return self.user.first_name+": "+self.list.name

@receiver(post_save)
def change_detect(sender, **kwargs):
    if sender not in (List, Item, Subscription):
        return
    print "saved: "+str(sender)

class ChangeLog(models.Model):
    """
    Keeps track of changes to ideaList data.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    CHANGE_TYPE_CHOICES = (
            (u'DE',u'Delete'),
            (u'AD',u'Add'),
            (u'ED',u'Edit'), #Should this include move?
    )
    change_type = models.CharField(max_length=2, choices=CHANGE_TYPE_CHOICES)
    time = models.DateTimeField(db_index=True)
    user = models.ForeignKey(User, related_name='changes')
