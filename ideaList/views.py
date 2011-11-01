from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from ideaList.models import Item, List
from django.forms import ModelForm
from django.core import serializers

# Decorator that adds RequestContext
def render_to(template_name):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(template_name, output,
                    RequestContext(request))
        return wrapper
    return renderer

@login_required
@render_to('ideaList/main.html')
def main(request):
    return {'lists':[s.list for s in request.user.subscriptions.all()]}

def csrf_failure(request, reason=""):
    return HttpResponse("CSRF failure: "+reason)

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('list', 'text', 'position')

@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def additem(request):
    i = Item(priority='NO')
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=i)
        if form.is_valid():
            newitem = form.save()
            json_serializer = serializers.get_serializer("json")()
            return HttpResponse(json_serializer.serialize([newitem],
                ensure_ascii=False))
        else:
            if request.is_ajax():
                return HttpResponseBadRequest('{}')
    else:
        form = ItemForm(instance=i)

    return render_to_response('ideaList/additem.html', {'form':form},
            RequestContext(request))
