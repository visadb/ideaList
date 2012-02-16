#!/usr/bin/python

import sys
from os import environ as env
from datetime import datetime, timedelta
sys.path.append('/srv/puhveli')
env['DJANGO_SETTINGS_MODULE'] = 'settings'
from ideaList.models import Item, List, ItemFrequency

# Purge old deleted Lists and Items

items_to_purge = Item.trash.filter(
        trashed_at__lt=datetime.now()-timedelta(days=7))
lists_to_purge = List.trash.filter(
        trashed_at__lt=datetime.now()-timedelta(days=7))

items_to_purge.delete()
lists_to_purge.delete()

# Purge old infrequent ItemFrequencies

age_treshold = 365 # in days
min_itemfreqs_per_list = 200 # How many to leave on list even if old
max_itemfreqs_per_list = 500 # Absolute maximum on list
for l in List.objects.all():
    def get_itemfreqs():
        return ItemFrequency.objects.filter(list=l).order_by(
                '-frequency','-last_changed')
    # Gather old infrequent items to delete
    delete = []
    count = ItemFrequency.objects.filter(list=l).count()
    if count > min_itemfreqs_per_list:
        age_limit = datetime.now()-timedelta(days=age_treshold)
        for i in get_itemfreqs()[min_itemfreqs_per_list:]:
            if i.frequency == 1 and i.last_changed < age_limit:
                delete.append(i.id)

    # If the count still exceeds maximum, remove infrequent old items until
    # maximum is no longer exceeded
    if count - len(delete) > max_itemfreqs_per_list:
        for i in get_itemfreqs()[(max_itemfreqs_per_list+len(delete)):]:
            delete.append(i.id)

    #Actual delete:
    if len(delete) > 0:
        ItemFrequency.objects.filter(id__in=delete).delete()
