from django.db import models
from django.contrib.auth.models import User
from positions.fields import PositionField
from undelete.models import Trashable
from django.dispatch import receiver
from django.db.models.signals import post_save
#from undelete.signals import pre_trash, pre_restore

class List(Trashable):
    """
    A list of items (:model:`ideaList.Item`).
    """
    name = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lists_owned')
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
    def as_dict(self, include_items=True, items=None):
        rep = {'id':self.id, 'name':self.name, 'owner_id':self.owner_id }
        if include_items:
            if items is None:
                items = self.nontrashed_items().order_by()
            rep['items'] = dict([(i.id,i.as_dict()) for i in items])
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
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items')
    text = models.CharField(max_length=200)
    url = models.URLField(blank=True, default="")
    important = models.BooleanField(default=False)
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
                'url':self.url, 'important':self.important,
                'position':self.position}
    def __unicode__(self):
        val = self.list.name+": "+self.text
        if self.trashed_at:
            val += " (trashed)"
        return val

class ItemFrequencyManager(models.Manager):
    def increment(self, list, text):
        """Increment the frequency of the given text if it exists or create a
        new ItemFrequency with frequency=1. Returns the ItemFrequency object."""
        text = text.lower().strip()
        try:
            freq = self.get(list=list, text=text)
            freq.frequency += 1
            freq.save()
            return freq
        except ItemFrequency.DoesNotExist:
            return self.create(list=list, text=text, frequency=1)
    def frequents_by_list(self, user, limit=None):
        """ Return the most frequent texts, most frequent first"""
        relevant_freqs = ItemFrequency.objects.filter(
                list__in=user.subscribed_lists.filter(trashed_at__isnull=True)
                ).order_by('-frequency')[:limit].values_list('list_id','text')
        freqs_by_list = {}
        for l, text in relevant_freqs:
            if l not in freqs_by_list:
                freqs_by_list[l] = [text]
            else:
                freqs_by_list[l].append(text)
        return freqs_by_list
class ItemFrequency(models.Model):
    """
    Info about frequency of a certain Item text on a certain List. Used for item
    suggestions."""
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='itemfrequencies')
    text = models.CharField(max_length=200)
    frequency = models.PositiveIntegerField()
    last_changed = models.DateTimeField(auto_now=True)

    objects = ItemFrequencyManager()

    class Meta:
        ordering = ['-frequency']
        unique_together = (("list","text"),)

    def __unicode__(self):
        return '%s: %s: %d' % (self.list.name, self.text, self.frequency)
@receiver(post_save, sender=Item)
def autoincrement_on_item_creation(sender, **kwargs):
    "Detect Item creation and increment its text's frequency."
    if kwargs['created']:
        i = kwargs['instance']
        ItemFrequency.objects.increment(i.list, i.text)

class Subscription(Trashable):
    """
    A user's (:model:`django.contrib.auth.User`) subscription of a certain List
    (:model:`ideaList.List`)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='subscriptions')
    position = PositionField(collection='user', default=-1)

    class Meta:
        ordering = ['position']
        unique_together = (('user','list'),)

    def as_dict(self, lst=None):
        if lst is None:
            lst = self.list.as_dict()
        return {'id':self.id, 'user_id':self.user_id,
                'list':lst, 'position': self.position}
    def __unicode__(self):
        val = self.user.first_name+": "+self.list.name
        if self.trashed_at:
            val += " (trashed)"
        return val

# Add a nontrash subscriptions manager to User
class NonTrashSubscriptionsDescriptor(User.subscriptions.__class__):
    ''' Query only nontrash subs of nontrash lists. '''
    def __init__(self):
        from django.db.models.fields.related import ForeignObjectRel
        related = ForeignObjectRel(User, Subscription, Subscription.user.field)
        super(NonTrashSubscriptionsDescriptor, self).__init__(related)
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        manager = super(NonTrashSubscriptionsDescriptor,
                self).__get__(instance, instance_type)
        manager.core_filters['trashed_at__isnull'] = True
        manager.core_filters['list__trashed_at__isnull'] = True
        return manager
User.nontrash_subscriptions = NonTrashSubscriptionsDescriptor()
