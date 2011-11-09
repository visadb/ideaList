from datetime import datetime
from django.db import models

class NonTrashedManager(models.Manager):
    ''' Query only objects which have not been trashed. '''
    def get_query_set(self):
        query_set = super(NonTrashedManager, self).get_query_set()
        return query_set.filter(trashed_at__isnull=True)
class TrashedManager(models.Manager):
    ''' Query only objects which have been trashed. '''
    def get_query_set(self):
        query_set = super(TrashedManager, self).get_query_set()
        return query_set.filter(trashed_at__isnull=False)

class Trashable(models.Model):
    """
    A mixin that enables undelete.
    """
    trashed_at = models.DateTimeField('Trashed', editable=False, blank=True, null=True)

    objects = NonTrashedManager()
    trash = TrashedManager()

    def delete(self, trash=True, *args, **kwargs):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.now()
            self.save()
        else:
            super(models.Model, self).delete(*args, **kwargs)

    def restore(self):
        if self.trashed_at == None:
            return
        self.trashed_at = None
        # Cannot call .save() because it tries to find current object with the
        # objects manager
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute('UPDATE '+self._meta.db_table
                +' SET trashed_at=NULL WHERE id=%s', [self.id])
        transaction.commit_unless_managed()

    class Meta:
        abstract = True
