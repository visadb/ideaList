#!/usr/bin/python

import sys
from os import environ as env
from datetime import datetime, timedelta
sys.path.append('/srv/puhveli')
env['DJANGO_SETTINGS_MODULE'] = 'settings'
from ideaList.models import Item, List

items_to_purge = Item.trash.filter(
        trashed_at__lt=datetime.now()-timedelta(days=7))
lists_to_purge = List.trash.filter(
        trashed_at__lt=datetime.now()-timedelta(days=7))

items_to_purge.delete()
lists_to_purge.delete()
