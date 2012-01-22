import re
import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from ideaList.models import List, Item, Subscription
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

def csrf_failure(req, reason=""):
    return HttpResponse('Security error: '+reason)

@login_required
def main(req):
    m = req.META
    agent = 'HTTP_USER_AGENT' in m and m['HTTP_USER_AGENT'] or None
    if 'dumb' in req.REQUEST or agent and ("SymbianOS/9.1" in agent or "NokiaN73" in agent):
        msg = 'msg' in req.REQUEST and req.REQUEST['msg'] or ''
        return render_to_response('ideaList/main_nojs.html',
                {'subscriptions': req.user.nontrash_subscriptions(), 'msg':msg},
                RequestContext(req));
    else:
        return render_to_response('ideaList/main.html',
                {'init_state': json.dumps(make_state(req.user))},
                RequestContext(req));

@login_required
def get_state(req):
    return state_response(req)


########## COMMON STUFF: ##########

def state_response(request, code=200, msg=''):
    return HttpResponse(status=code, content_type="application/json",
            content=json.dumps({'state': make_state(request.user), 'msg':msg}))

# Return all state that is used in client's main view
def make_state(user):
    subscriptions = dict([(s.id,s.as_dict())
        for s in user.nontrash_subscriptions().order_by()])
    lists = dict([(l.id, l.as_dict(include_items=False))
        for l in List.nontrash.all()])
    return {'subscriptions':subscriptions, 'lists':lists}

# A generic view-template for moving objects with positions
def move(req, cls):
    if 'position' not in dir(cls):
        raise ValueError("Provided class doesn't have a position field")
    cls_name = cls.__name__.lower()
    obj_id_name = cls_name+'_id'

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

    if obj_id_name not in req.POST:
        return state_response(req, code=400, msg=obj_id_name+' not provided')
    try:
        obj = cls.objects.get(pk=req.POST[obj_id_name])
    except ValueError:
        return state_response(req, code=400, msg='invalid '+obj_id_name)
    except cls.DoesNotExist:
        return state_response(req, code=404, msg='No such '+cls_name)

    # Calculate new position
    if where == 'up':
        oldpos = obj.position
        followers = cls.nontrash.filter(
                position__lt=oldpos).order_by('-position')
        if 'user' in dir(cls):
            followers = followers.filter(user=req.user)
        if isinstance(obj, Item):
            followers = followers.filter(list=obj.list)
        elif isinstance(obj, Subscription):
            followers = followers.filter(list__trashed_at__isnull=True)
        if oldpos == 0 or followers.count() == 0:
            return state_response(req, msg='Could not raise: was on top')
        else:
            newpos = followers[0].position
    elif where == 'down':
        oldpos = obj.position
        followers = cls.nontrash.filter(position__gt=oldpos)
        if 'user' in dir(cls):
            followers = followers.filter(user=req.user)
        if isinstance(obj, Item):
            followers = followers.filter(list=obj.list)
        elif isinstance(obj, Subscription):
            followers = followers.filter(list__trashed_at__isnull=True)
        if oldpos == cls.objects.count()-1 or followers.count() == 0:
            return state_response(req, msg='Could not lower: was on bottom')
        else:
            newpos = followers[0].position
    else:
        newpos = where

    obj.position = newpos
    obj.save()
    return state_response(req, msg=cls_name+" "+str(obj.id)
            +" moved to index "+str(obj.position))

@login_required
def edit_text(request):
    """
    View to use with jeditable for editing the text of items and name of lists.
    Request must have POST entries 'element_id' of form 'item_<item_id>_text' or
    'subscription_<subscription_id>_listname' and 'text'. Will return a JSON
    object with the input text in key 'text' and the usual state info in key
    'status'. Won't send the state on error since jeditable won't handle it.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('{"msg": "Only POST supported"}')
    if 'element_id' not in request.POST or 'text' not in request.POST:
        return HttpResponseBadRequest(
                '{"msg":"param element_id or text not provided"}')
    match = re.match('^item_(\d+)_text$', request.POST['element_id'])
    if match:
        try:
            i = Item.objects.get(pk=match.group(1))
        except Item.DoesNotExist:
            return HttpResponseNotFound('{"msg": "No such item"}')
        text = request.POST['text']
        if i.text != text:
            i.text = text
            i.save()
        content = json.dumps({'state':make_state(request.user),
                              'msg':"Item "+str(i.id)+"'s text updated",
                              'text':text})
        return HttpResponse(content_type="application/json", content=content)

    match = re.match('^subscription_(\d+)_listname$',request.POST['element_id'])
    if match:
        try:
            s = Subscription.objects.get(pk=match.group(1))
        except Subscription.DoesNotExist:
            return HttpResponseNotFound('{"msg": "No such subscription"}')
        text = request.POST['text']
        l = s.list
        if l.name != text:
            l.name = text
            l.save()
        msg = "List "+str(l.id)+"'s name updated (sub "+str(s.id)+")"
        content = json.dumps({'state':make_state(request.user),
                              'msg':msg, 'text':text})
        return HttpResponse(content_type="application/json", content=content)

    # Neither regex matched to element_id
    return HttpResponseBadRequest('{"msg": "param element_id invalid"}')


########## SUBSCRIPTION MANIPULATION VIEWS: ##########

@login_required
def add_subscription(req):
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'list_id' not in req.POST:
        return state_response(req, code=400, msg='list_id not provided')
    # Get list
    try:
        l = List.objects.get(pk=req.POST['list_id'])
    except ValueError:
        return state_response(req, code=400, msg='invalid list_id')
    except List.DoesNotExist:
        return state_response(req, code=404, msg='No such list')
    # See if non-trashed subscription already exists
    try:
        s = Subscription.nontrash.get(list=l, user=req.user)
        return state_response(req, code=200, msg='Already subscribed')
    except Subscription.DoesNotExist:
        # See if a trashed subscription already exists
        try:
            s = Subscription.trash.get(list=l, user=req.user)
            s.restore()
            return state_response(req, code=200, msg='Subscription restored')
        except Subscription.DoesNotExist:
            s = Subscription.objects.create(list=l, user=req.user)
            return state_response(req, code=200, msg='Subscription created')

@login_required
def remove_subscription(req):
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'list_id' not in req.POST:
        return state_response(req, code=400, msg='list_id not provided')
    # Get list
    try:
        l = List.objects.get(pk=req.POST['list_id'])
    except ValueError:
        return state_response(req, code=400, msg='invalid list_id')
    except List.DoesNotExist:
        return state_response(req, code=404, msg='No such list')
    # See if non-trashed subscription exists
    try:
        s = Subscription.nontrash.get(list=l, user=req.user)
        s.delete()
        return state_response(req, code=200, msg='Subscription removed')
    except Subscription.DoesNotExist:
        return state_response(req, code=404, msg='No such subscription')

@login_required
def move_subscription(req):
    """
    Request must have POST keys 'subscription_id' and 'where'. 'where' is either
    up/down or subscription's new position as an integer.
    """
    return move(req, Subscription)

@login_required
def minimize_subscription(req):
    return set_subscription_minimization(req, minimized=True)

@login_required
def maximize_subscription(req):
    return set_subscription_minimization(req, minimized=False)

def set_subscription_minimization(req, minimized):
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'subscription_id' not in req.POST:
        return state_response(req, code=400, msg='subscription_id not provided')
    try:
        s = Subscription.nontrash.get(pk=req.POST['subscription_id'])
        if s.user != req.user:
            return state_response(req, code=400, msg='not your subscription')
        action = minimized and 'minimized' or 'maximized'
        if s.minimized != minimized:
            s.minimized = minimized
            s.save()
            return state_response(req, code=200, msg='Subscription '+action)
        else:
            return state_response(req, code=200, msg='Already '+action)
    except ValueError:
        return state_response(req, code=400, msg='invalid subscription_id')
    except Subscription.DoesNotExist:
        return state_response(req, code=404, msg='No such subscription')


########## ITEM MANIPULATION VIEWS: ##########

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('list', 'text', 'position')

@login_required
def add_item(req):
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
@csrf_exempt
def remove_items(req):
    def my_response(code=200, msg=''):
        if req.is_ajax():
            return state_response(req, code=code, msg=msg)
        else:
            return HttpResponseRedirect(
                    reverse('ideaList.views.main')+'?msg='+msg)
    if req.method != 'POST':
        return my_response(code=400, msg='Only POST supported')
    if 'item_ids' not in req.POST:
        return my_response(code=200, msg='Nothing removed')
    item_ids = req.POST.getlist('item_ids')
    items = []
    for item_id in item_ids:
        try:
            i = Item.objects.get(pk=item_id)
        except ValueError:
            return my_response(code=400, msg='invalid item_id '+item_id)
        except Item.DoesNotExist:
            return my_response(code=404, msg='No such item: '+item_id)
        if i.list.subscription_for(req.user) is None:
            return my_response(code=403, msg='not your item: '+item_id)
        items.append(i)
    for i in items:
        if i.trashed_at == None:
            i.delete()
    return my_response(code=200, msg='Items '+(','.join(item_ids))+' removed')

@login_required
def move_item(req):
    """
    Request must have POST keys 'item_id' and 'where'. 'where' is either up/down
    or item_id's new position as an integer.
    """
    return move(req, Item)


########## LIST MANIPULATION VIEWS: ##########

@login_required
def add_list(req):
    """
    Request must have POST key 'name'. Request may also have POST key
    'subscribe'. If POST['subscribe'] == 'true', req.user is subscribed to the
    created list.
    """
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'name' not in req.POST:
        return state_response(req, code=400, msg='name not provided')
    elif len(req.POST['name']) == 0:
        return state_response(req, code=400, msg='empty name')
    l = List.objects.create(name=req.POST['name'], owner=req.user)
    if 'subscribe' in req.POST and req.POST['subscribe'] == 'true':
        Subscription.objects.create(user=req.user, list=l);
        return state_response(req, msg='List created and subscribed')
    return state_response(req, msg='List created')

@login_required
def remove_list(req):
    if req.method != 'POST':
        return state_response(req, code=400, msg='Only POST supported')
    if 'list_id' not in req.POST:
        return state_response(req, code=400, msg='list_id not provided')
    try:
        l = List.objects.get(pk=req.POST['list_id'])
    except ValueError:
        return state_response(req, code=400, msg='invalid list_id')
    except List.DoesNotExist:
        return state_response(req, code=404, msg='No such list')
    l.delete()
    return state_response(req, msg='List '+req.POST['list_id']+' removed')
