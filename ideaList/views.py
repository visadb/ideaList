import re
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from ideaList.models import Item
from django.forms import ModelForm

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

# Return all state that is used in client's main view
def make_state(user):
    subscriptions = [s.as_dict() for s in user.nontrash_subscriptions()]
    return {'subscriptions':subscriptions}

@login_required
@render_to('ideaList/main.html')
def main(request):
    return {'init_state': json.dumps(make_state(request.user))}

def state_response(request, code=200, msg=''):
    return HttpResponse(status=code, content_type="application/json",
            content=json.dumps({'state': make_state(request.user), 'msg':msg}))

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
            # Success:
            form.save()
            return state_response(request)
        elif request.is_ajax():
            return state_response(request, code=400, msg='invalid args')
    else:
        form = ItemForm(instance=i)

    return render_to_response('ideaList/additem.html', {'form':form},
            RequestContext(request))

@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def removeitem(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('{"msg": "Only POST supported"}')
    if 'item_id' not in request.POST:
        return HttpResponseBadRequest('{"msg": "item_id not provided"}')
    try:
        i = Item.objects.get(pk=request.POST['item_id'])
    except ValueError:
        return HttpResponseBadRequest('{"msg": "invalid item_id"}')
    except Item.DoesNotExist:
        return HttpResponseNotFound('{"msg": "No such item"}')
    i.delete()
    return HttpResponse('{"msg": "Item deleted"}');

@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def moveitem(request):
    """ 
    Request must have POST keys 'item_id' and 'where'. 'where' is either up/down
    or item_id's new position as an integer.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('{"msg": "Only POST supported"}')
    if 'where' not in request.POST:
        return HttpResponseBadRequest('{"msg": "param where not provided"}')
    where = request.POST['where']
    if where not in ('up', 'down'):
        try:
            where = int(where)
        except ValueError:
            return HttpResponseBadRequest('{"msg": "param where invalid"}')

    if 'item_id' not in request.POST:
        return HttpResponseBadRequest('{"msg": "param item_id not provided"}')
    try:
        i = Item.objects.get(pk=request.POST['item_id'])
    except ValueError:
        return HttpResponseBadRequest('{"msg": "invalid item_id"}')
    except Item.DoesNotExist:
        return HttpResponseNotFound('{"msg": "No such item"}')

    # Calculate new position
    if where == 'up':
        oldpos = i.position
        if oldpos > 0:
            newpos = oldpos - 1
        else:
            return HttpResponse('{"msg": "Could not raise: was on top"}');
    elif where == 'down':
        oldpos = i.position
        if oldpos < Item.objects.count()-1:
            newpos = oldpos + 1
        else:
            return HttpResponse('{"msg": "Could not lower: was on bottom"}');
    else:
        newpos = where

    i.position = newpos
    i.save()
    return HttpResponse('{"msg": "Item moved to index '+str(i.position)+'"}');


@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def edittext(request):
    """
    View to use with jeditable for editing the text of items. Request must have
    POST entries 'element_id' of form 'item_<item_id>_text' and 'text'. Will set the
    text of element item_id to the value of 'text'.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('{"msg": "Only POST supported"}')
    if 'element_id' not in request.POST:
        return HttpResponseBadRequest('{"msg": "param element_id not provided"}')
    match = re.match('^item_(\d+)_text$', request.POST['element_id'])
    if not match:
        return HttpResponseBadRequest('{"msg": "param element_id invalid"}')
    try:
        i = Item.objects.get(pk=match.group(1))
    except Item.DoesNotExist:
        return HttpResponseNotFound('{"msg": "No such item"}')

    text = request.POST['text']
    if i.text != text:
        i.text = text
        i.save()
    return HttpResponse(text);
