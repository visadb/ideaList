from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ideaList.views',
    url(r'^$', 'main'),
    url(r'^get_state/$', 'get_state'),
    url(r'^add_item/$', 'add_item'),
    url(r'^remove_item/$', 'remove_item'),
    url(r'^move_item/$', 'move_item'),
    url(r'^move_subscription/$', 'move_subscription'),
    url(r'^edit_text/$', 'edit_text'),
)
