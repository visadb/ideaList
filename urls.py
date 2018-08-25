from django.conf.urls import include, url
from django.views.generic import RedirectView

from django.contrib.auth.views import LoginView, logout_then_login, PasswordChangeView, PasswordChangeDoneView

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = [
    url(r'^$',          RedirectView.as_view(url='/ideaList')),
    url(r'^ideaList/',  include('ideaList.urls')),
    url(r'^login/$',    LoginView.as_view(), name='login'),
    url(r'^logout/$',   logout_then_login),
    url(r'^passwd/$',   PasswordChangeView.as_view()),
    url(r'^passwd_done/$', PasswordChangeDoneView.as_view()),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/',     include(admin.site.urls)),
]
