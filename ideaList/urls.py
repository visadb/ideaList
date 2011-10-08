from django.conf.urls.defaults import patterns
from django.views.generic import ListView
from ideaList.models import List

urlpatterns = patterns('',
    (r'^$', 
        ListView.as_view(
            # TODO: List of logged in user's subscribed lists
            queryset=List.objects.order_by('name'),
            template_name='ideaList/main.html')),
)
