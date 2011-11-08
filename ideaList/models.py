from datetime import datetime
from django.db import models
from positions.fields import PositionField
from django.contrib.auth.models import User
from managers import TrashedManager, NonTrashedManager

class List(models.Model):
    """
    A list of items (:model:`ideaList.Item`).
    """
    name = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, related_name='lists_owned')
    subscribers = models.ManyToManyField(User,
            related_name='subscribed_lists', through='Subscription')
    def __unicode__(self):
        return self.name
    def n_items(self):
        return self.items.count()
    n_items.short_description = u'# of items'

class Item(models.Model):
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
    trashed_at = models.DateTimeField('Trashed', editable=False, blank=True, null=True)
    last_changed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = NonTrashedManager()
    trash = TrashedManager()

    class Meta:
        ordering = ['position']

    def delete(self, trash=True, *args, **kwargs):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.now()
            self.save()
        else:
            super(models.Model, self).delete(*args, **kwargs)

    def restore(self):
        from django.db import connection, transaction
        self.trashed_at = None
        cursor = connection.cursor()
        cursor.execute('UPDATE idealist_item SET trashed_at=NULL WHERE id=%s',
                [self.id])
        transaction.commit_unless_managed()

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

#class ChangeLog(models.Model):
#    """
#    Keeps track of changes to data.
#    """
