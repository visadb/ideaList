from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse

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

def additem(request):
    #TODO: get list_id, pos and item text
    return HttpResponse("Hurraa")
