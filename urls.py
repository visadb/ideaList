from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',          RedirectView.as_view(url='/ideaList')),
    url(r'^ideaList/',  include('ideaList.urls')),
    url(r'^login/$',    'django.contrib.auth.views.login'),
    url(r'^logout/$',   'django.contrib.auth.views.logout_then_login'),
    url(r'^passwd/$',   'django.contrib.auth.views.password_change'),
    url(r'^passwd_done/$', 'django.contrib.auth.views.password_change_done'),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/',     include(admin.site.urls)),
)
