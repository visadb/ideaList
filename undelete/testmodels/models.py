from django.db import models
from undelete.models import Trashable
from positions.fields import PositionField
from django.contrib.auth.models import User

class Apple(Trashable):
    """
    Model for testing Trashable.
    """
    color = models.CharField(max_length=200)

    def __unicode__(self):
        return self.color+" apple"

class Plaque(Trashable):
    """
    Model for testing interaction of Trashable and PositionField
    """
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    position = PositionField(collection='user')

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return self.text

