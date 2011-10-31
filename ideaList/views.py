from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

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

@csrf_protect # Unnecessary, handled by the csrf middleware
def additem(request):
    #TODO: get list_id, pos and item text
    return HttpResponse("Hurraa")
