from django.conf.urls import patterns, url

urlpatterns = patterns('ideaList.views',
    url(r'^$', 'main'),
    url(r'^basic/$', 'basic'),
    url(r'^get_state/$', 'get_state'),
    url(r'^add_item/$', 'add_item'),
    url(r'^ifttt/UDPN917QKT11OOCGM7ZN/add_item/$', 'add_item_ifttt'),
    url(r'^move_item/$', 'move_item'),
    url(r'^remove_items/$', 'remove_items'),
    url(r'^set_item_importances/$', 'set_item_importances'),
    url(r'^set_item_url/$', 'set_item_url'),
    url(r'^add_subscription/$', 'add_subscription'),
    url(r'^remove_subscription/$', 'remove_subscription'),
    url(r'^move_subscription/$', 'move_subscription'),
    url(r'^add_list/$', 'add_list'),
    url(r'^remove_list/$', 'remove_list'),
    url(r'^edit_text/$', 'edit_text'),
    url(r'^undelete/$', 'undelete'),
    url(r'^get_frequents/$', 'get_frequents'),
)
