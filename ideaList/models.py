from django.db import models
from django.contrib.auth.models import User

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
    last_changed = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        order_with_respect_to = 'list'

    def __unicode__(self):
        return self.list.name+": "+self.text

class Subscription(models.Model):
    """
    A user's (:model:`django.contrib.auth.User`) subscription of a certain List
    (:model:`ideaList.List`)
    """
    user = models.ForeignKey(User, related_name='subscriptions')
    list = models.ForeignKey(List, related_name='subscriptions')
    minimized = models.BooleanField(default=False)

    class Meta:
        order_with_respect_to = 'user'

    def __unicode__(self):
        return self.user.first_name+": "+self.list.name
