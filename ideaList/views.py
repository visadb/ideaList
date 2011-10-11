from django.views.generic import ListView
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
#from ideaList.models import List

class MainListView(ListView):
    pass

@login_required
def main(request):
    lists = [request.user.subscribed_lists.get(pk=i)
             for i in request.user.get_subscription_order()]
    return render_to_response('ideaList/main.html', {'lists':lists})
