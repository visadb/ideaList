import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'puhveli.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = '/srv/puhveli'
if path not in sys.path:
    sys.path.append(path)
