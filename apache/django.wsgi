import os
import sys

path = '/usr/local/wsgi/modules'
paths = ['/srv/http', '/srv/http/puhveli']
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'puhveli.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
