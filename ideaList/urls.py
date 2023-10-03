from django.urls import re_path

from ideaList.views import *

urlpatterns = [
    re_path(r'^$', main, name="main"),
    re_path(r'^basic/$', basic, name="basic"),
    re_path(r'^get_state/$', get_state),
    re_path(r'^add_item/$', add_item_login_required),
    re_path(r'^alexa/AEKA5AEFAHHEEJA6HEI7/add_item/$', add_item_alexa),
    re_path(r'^move_item/$', move_item),
    re_path(r'^remove_items/$', remove_items, name="remove_items"),
    re_path(r'^set_item_importances/$', set_item_importances),
    re_path(r'^set_item_url/$', set_item_url),
    re_path(r'^add_subscription/$', add_subscription),
    re_path(r'^remove_subscription/$', remove_subscription),
    re_path(r'^move_subscription/$', move_subscription),
    re_path(r'^add_list/$', add_list),
    re_path(r'^remove_list/$', remove_list),
    re_path(r'^edit_text/$', edit_text),
    re_path(r'^undelete/$', undelete, name='undelete'),
    re_path(r'^get_frequents/$', get_frequents),
]
