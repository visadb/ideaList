from django.urls import include, re_path
from django.views.generic import RedirectView

from django.contrib.auth.views import LoginView, logout_then_login, PasswordChangeView, PasswordChangeDoneView

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = [
    re_path(r'^$',          RedirectView.as_view(url='/ideaList')),
    re_path(r'^ideaList/',  include('ideaList.urls')),
    re_path(r'^login/$',    LoginView.as_view(), name='login'),
    re_path(r'^logout/$',   logout_then_login),
    re_path(r'^passwd/$',   PasswordChangeView.as_view()),
    re_path(r'^passwd_done/$', PasswordChangeDoneView.as_view()),
    #re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #re_path(r'^admin/',     include(admin.site.urls)),
]
