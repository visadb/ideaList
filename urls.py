from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',          redirect_to, {'url': '/ideaList/', 'permanent': False}),
    url(r'^ideaList/',  include('ideaList.urls')),
    url(r'^login/$',    'django.contrib.auth.views.login'),
    url(r'^logout/$',   'django.contrib.auth.views.logout_then_login'),
    url(r'^passwd/$',   'django.contrib.auth.views.password_change'),
    url(r'^passwd_done/$', 'django.contrib.auth.views.password_change_done'),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/',     include(admin.site.urls)),
)
