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
def additem(req):
    i = Item(priority='NO')
    if req.method == 'POST':
        form = ItemForm(req.POST, instance=i)
        if form.is_valid():
            # Success:
            form.save()
            return state_response(req, msg='item '+str(i.id)+' added')
        elif req.is_ajax():
            return state_response(req, code=400, msg='invalid args')
    else:
        form = ItemForm(instance=i)

    return render_to_response('ideaList/additem.html', {'form':form},
            RequestContext(req))

@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def removeitem(req):
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'item_id' not in req.POST:
        return state_response(req, code=400, msg='item_id not provided')
    try:
        i = Item.objects.get(pk=req.POST['item_id'])
    except ValueError:
        return state_response(req, code=400, msg='invalid item_id')
    except Item.DoesNotExist:
        return state_response(req, code=404, msg='No such item')
    i.delete()
    return state_response(req, msg='Item '+req.POST['item_id']+' removed')

@login_required
@csrf_protect # Unnecessary, handled by the csrf middleware
def moveitem(req):
    """ 
    Request must have POST keys 'item_id' and 'where'. 'where' is either up/down
    or item_id's new position as an integer.
    """
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'where' not in req.POST:
        return state_response(req, code=400, msg='param where not provided')
    where = req.POST['where']
    if where not in ('up', 'down'):
        try:
            where = int(where)
        except ValueError:
            return state_response(req, code=400, msg='param where invalid')

    if 'item_id' not in req.POST:
        return state_response(req, code=400, msg='param item_id not provided')
    try:
        i = Item.objects.get(pk=req.POST['item_id'])
    except ValueError:
        return state_response(req, code=400, msg='invalid item_id')
    except Item.DoesNotExist:
        return state_response(req, code=404, msg='No such item')

    # Calculate new position
    if where == 'up':
        oldpos = i.position
        followers = Item.nontrash.filter(
                position__lt=oldpos).order_by('-position')
        if oldpos == 0 or followers.count() == 0:
            return state_response(req, msg='Could not raise: was on top')
        else:
            newpos = followers[0].position
    elif where == 'down':
        oldpos = i.position
        followers = Item.nontrash.filter(position__gt=oldpos)
        if oldpos == Item.objects.count()-1 or followers.count() == 0:
            return state_response(req, msg='Could not lower: was on bottom')
        else:
            newpos = followers[0].position
    else:
        newpos = where

    i.position = newpos
    i.save()
    return state_response(req, msg="Item "+str(i.id)
            +" moved to index "+str(i.position))


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
