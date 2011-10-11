from django.conf.urls.defaults import patterns
#from django.views.generic import ListView
#from ideaList.models import List
from ideaList.views import main

urlpatterns = patterns('',
    (r'^$', main),
)
