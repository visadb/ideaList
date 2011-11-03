from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ideaList.views',
    url(r'^$', 'main'),
    url(r'^additem/$', 'additem'),
    url(r'^removeitem/$', 'removeitem'),
    url(r'^moveitem/$', 'moveitem'),
    url(r'^edittext/$', 'edittext'),
)
