from django.conf.urls import url

from ideaList.views import *

urlpatterns = [
    url(r'^$', main, name="main"),
    url(r'^basic/$', basic, name="basic"),
    url(r'^get_state/$', get_state),
    url(r'^add_item/$', add_item_login_required),
    url(r'^alexa/AEKA5AEFAHHEEJA6HEI7/add_item/$', add_item_alexa),
    url(r'^move_item/$', move_item),
    url(r'^remove_items/$', remove_items, name="remove_items"),
    url(r'^set_item_importances/$', set_item_importances),
    url(r'^set_item_url/$', set_item_url),
    url(r'^add_subscription/$', add_subscription),
    url(r'^remove_subscription/$', remove_subscription),
    url(r'^move_subscription/$', move_subscription),
    url(r'^add_list/$', add_list),
    url(r'^remove_list/$', remove_list),
    url(r'^edit_text/$', edit_text),
    url(r'^undelete/$', undelete, name='undelete'),
    url(r'^get_frequents/$', get_frequents),
]
