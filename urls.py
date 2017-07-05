from django.conf.urls import include, url
from django.views.generic import RedirectView

from django.contrib.auth.views import login, logout_then_login, password_change, password_change_done

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = [
    url(r'^$',          RedirectView.as_view(url='/ideaList')),
    url(r'^ideaList/',  include('ideaList.urls')),
    url(r'^login/$',    login, name='login'),
    url(r'^logout/$',   logout_then_login),
    url(r'^passwd/$',   password_change),
    url(r'^passwd_done/$', password_change_done),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/',     include(admin.site.urls)),
]
