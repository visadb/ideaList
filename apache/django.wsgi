import os
import sys

sys.path.append('/srv')
sys.path.append('/srv/puhveli')

os.environ['DJANGO_SETTINGS_MODULE'] = 'puhveli.settings_production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
