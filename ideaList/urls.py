from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ideaList.views',
    url(r'^$', 'main'),
    url(r'^additem/$', 'additem'),
)
