from datetime import datetime
from django.db import models
import signals

class NonTrashedManager(models.Manager):
    ''' Query only objects which have not been trashed. '''
    def get_queryset(self):
        query_set = super(NonTrashedManager, self).get_queryset()
        return query_set.filter(trashed_at__isnull=True)
class TrashedManager(models.Manager):
    ''' Query only objects which have been trashed. '''
    def get_queryset(self):
        query_set = super(TrashedManager, self).get_queryset()
        return query_set.filter(trashed_at__isnull=False)


class Trashable(models.Model):
    """
    A mixin that enables undelete.
    """
    trashed_at = models.DateTimeField('Trashed', editable=False, blank=True, null=True)

    objects = models.Manager()
    nontrash = NonTrashedManager()
    trash = TrashedManager()

    def is_trash(self):
        return self.trashed_at != None

    def delete(self, trash=True, *args, **kwargs):
        if not self.trashed_at and trash:
            signals.pre_trash.send(sender=type(self), instance=self)
            self.trashed_at = datetime.now()
            self.save()
            signals.post_trash.send(sender=type(self), instance=self)
        else:
            super(Trashable, self).delete(*args, **kwargs)

    def restore(self):
        signals.pre_restore.send(sender=type(self), instance=self)
        self.trashed_at = None
        self.save()
        signals.post_restore.send(sender=type(self), instance=self)

    @classmethod
    def empty_trash(cls):
        for i in cls.trash.all():
            i.delete()

    class Meta:
        abstract = True
