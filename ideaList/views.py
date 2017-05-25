import re
import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from ideaList.models import List, Item, ItemFrequency, Subscription
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

#################################
########## User Views: ##########
#################################

def csrf_failure(req, reason=""):
    return HttpResponse('Security error: '+reason)

@login_required
@render_to('ideaList/main.html')
def main(req):
    m = req.META
    agent = 'HTTP_USER_AGENT' in m and m['HTTP_USER_AGENT'] or None
    if agent and ("SymbianOS/9.1" in agent or "NokiaN73" in agent):
        return HttpResponseRedirect(reverse('ideaList.views.basic'))
    return {'init_state': json.dumps(make_state(req.user)),
            'suggestions_per_row': 3,
            'suggestions_per_col': 7}

@login_required
@render_to('ideaList/main_nojs.html')
def basic(req):
    msg = 'msg' in req.REQUEST and req.REQUEST['msg'] or ''
    return {'subscriptions': req.user.nontrash_subscriptions.all(), 'msg':msg}

@login_required
@csrf_exempt
@render_to('ideaList/undelete.html')
def undelete(req):
    "Undelete given item_ids and list_ids. Will ignore any invalid ids."
    def make_ctx(msg):
        items = Item.trash.filter(
            list__in=[s.list for s in req.user.nontrash_subscriptions.all()]) \
                    .order_by('-trashed_at')
        lists = List.trash.filter(
                pk__in=req.user.subscribed_lists.all()).order_by('-trashed_at')
        return {'msg':msg,'trashed_items':items,'trashed_lists':lists}

    if req.method == 'POST':
        undelete = 'undelete' in req.POST
        purge = 'purge' in req.POST
        if not undelete and not purge:
            return make_ctx('Error: neither undelete or purge specified')
        if undelete and purge:
            return make_ctx('Error: both undelete and purge specified')

        if 'item_ids' not in req.POST:
            item_ids = []
        else:
            item_ids = req.POST.getlist('item_ids')

        valid_items = get_valid_items(item_ids,user=req.user,manager=Item.trash)

        if 'list_ids' not in req.POST:
            list_ids = []
        else:
            list_ids = req.POST.getlist('list_ids')
        valid_lists = []

        for list_id in list_ids:
            try:
                l = List.trash.get(pk=list_id)
            except ValueError: continue # Invalid list id
            except List.DoesNotExist: continue # No such trashed list
            if l.subscription_for(req.user) == None: continue #!subscribed
            valid_lists.append(l)

        for x in valid_items + valid_lists:
            if purge:
                x.delete()
            else:
                x.restore()

        msg = "%s %d items and %d lists." % (purge and "Purged" or "Undeleted",
                len(valid_items), len(valid_lists))
        return make_ctx(msg)
    return make_ctx('')


#################################
########## AJAX Views: ##########
#################################

@login_required
def get_state(req):
    return state_response(req)

@login_required
def get_frequents(req):
    frequents = ItemFrequency.objects.frequents_by_list(req.user)
    return HttpResponse(status=200, content_type="application/json",
            content=json.dumps(frequents))

########## COMMON STUFF: ##########

def state_response(request, code=200, msg=''):
    return HttpResponse(status=code, content_type="application/json",
            content=json.dumps({'state': make_state(request.user), 'msg':msg}))

# Return all state that is used in client's main view
def make_state(user):
    # This function is messy to minimize number of SQL queries

    subs = user.nontrash_subscriptions.all().order_by()
    # Get all lists now to avoid select_related in above subs query. These are
    # needed in the list dictionary generation anyway.
    lsts = dict([(l.id, l) for l in List.nontrash.all()])

    # Get all interesting items in one query
    list_ids = [s.list_id for s in subs]
    itms = Item.nontrash.filter(list__in=list_ids).order_by()

    # Generate subscriptions dictionary
    items_by_sub = dict([(s.id,
        filter(lambda i:i.list_id==s.list_id, itms)) for s in subs])
    subscriptions = dict([(s.id, s.as_dict(
        lst=lsts[s.list_id].as_dict(items=items_by_sub[s.id]))) for s in subs])

    # Generate list dictionary
    lists = dict([(l.id, l.as_dict(include_items=False))
        for l in lsts.itervalues()])
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

    if cls is Item and 'list_id' in req.POST:
        if where in ('up', 'down'):
            return state_response(req, code=400, msg='up/down with list_id')
        try:
            l = List.objects.get(pk=req.POST['list_id'])
        except ValueError:
            return state_response(req, code=400, msg='invalid list_id')
        except List.DoesNotExist:
            return state_response(req, code=400, msg='list_id does not exist')
        obj.list = l

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


########## ITEM MANIPULATION VIEWS: ##########

def get_valid_items(item_ids, user=None, manager=Item.objects):
    """Filters invalid item ids out. If user is given, he/she must be subscribed
    to the item's list."""
    valid_items = []
    for item_id in item_ids:
        try:
            i = manager.get(pk=item_id)
        except ValueError: continue # Invalid item id
        except Item.DoesNotExist: continue # No such trashed item id
        if user is not None and not i.is_on_subscribed_list(user):
            continue # Not subscribed
        valid_items.append(i)
    return valid_items

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('list', 'text', 'position')

@login_required
def add_item(req):
    i = Item()
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

@csrf_exempt
def add_item_ifttt(req):
    return add_item(req)


@login_required
@csrf_exempt
def remove_items(req):
    "Trash given item_ids. If any of the item_ids are invalid, do nothing."
    def my_response(code=200, msg=''):
        if req.is_ajax():
            return state_response(req, code=code, msg=msg)
        else:
            return HttpResponseRedirect(
                    reverse('ideaList.views.basic')+'?msg='+msg)
    if req.method != 'POST':
        return my_response(code=400, msg='Only POST supported')
    if 'item_ids' not in req.POST:
        return my_response(code=200, msg='Nothing removed')
    item_ids = req.POST.getlist('item_ids')
    items = get_valid_items(item_ids, user=req.user)
    if len(items) != len(item_ids):
        return my_response(code=400, msg='at least one invalid item_id')
    for i in items:
        if i.trashed_at == None:
            i.delete()
    return my_response(code=200, msg='Items '+(','.join(item_ids))+' removed')

@login_required
def move_item(req):
    """
    Request must have POST keys 'item_id' and 'where'. 'where' is either up/down
    or item_id's new position as an integer. For moving items across lists,
    request may also contain the POST key 'list_id' - in this case 'where' must
    be an integer.
    """
    return move(req, Item)

@login_required
def set_item_importances(req):
    """
    Request may have POST keys 'important_item_ids' and 'unimportant_item_ids'.
    Will set their importance accordingly. Ignore invalid ids. If sets are not
    disjoint, important_item_ids wins.
    """
    if req.method != 'POST':
        return state_response(code=400, msg='Only POST supported')
    if 'important_item_ids' in req.POST:
        important_item_ids = req.POST.getlist('important_item_ids')
    else:
        important_item_ids = []
    important_items = get_valid_items(important_item_ids, user=req.user)

    if 'unimportant_item_ids' in req.POST:
        unimportant_item_ids = req.POST.getlist('unimportant_item_ids')
    else:
        unimportant_item_ids = []
    unimportant_items = get_valid_items(unimportant_item_ids, user=req.user)

    # Unimportant first, so if sets aren't disjoint, important wins
    for i in unimportant_items:
        if i.important:
            i.important = False
            i.save()
    for i in important_items:
        if not i.important:
            i.important = True
            i.save()
 
    total_items = len(important_item_ids) + len(unimportant_item_ids)
    updated_items = len(important_items) + len(unimportant_items)
    return state_response(req, code=200, msg='Item priorities of %d/%d items updated' % (updated_items, total_items))

@login_required
def set_item_url(req):
    """
    Request must have POST keys 'item_id' and 'url'.
    """
    if req.method != 'POST':
        return state_response(code=400, msg='Only POST supported')
    if 'item_id' not in req.POST:
        return state_response(req, code=400, msg='item_id missing')
    if 'url' not in req.POST:
        return state_response(req, code=400, msg='url missing')

    try:
        i = Item.objects.get(pk=req.POST['item_id'])
    except ValueError:
        return state_response(req, code=400, msg='Invalid item_id')
    except Item.DoesNotExist:
        return state_response(req, code=404, msg='item_id doesn\'t exist')
    if req.user is not None and not i.is_on_subscribed_list(req.user):
        return state_response(req, code=403, msg='Not subscribed')

    if len(req.POST['url']) != 0:
        validate = URLValidator()
        try:
            validate(req.POST['url'])
        except ValidationError:
            return state_response(req, code=400, msg='invalid url')

    i.url = req.POST['url']
    i.save()
    return state_response(req, code=200,
            msg='Item %s\'s url updated' % req.POST['item_id'])


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
    import django.db
    try:
        l = List.objects.create(name=req.POST['name'], owner=req.user)
    except django.db.IntegrityError, e:
        # state_response fails here for some reason...
        return HttpResponse(status=400, content_type="application/json",\
                content=json.dumps({'msg':'DB Integrity error: %s' % e}))
    except:
        return state_response(req, code=400, msg='Error creating list')
    if 'subscribe' in req.POST and req.POST['subscribe'] == 'true':
        try:
            Subscription.objects.create(user=req.user, list=l);
        except Exception, e:
            return state_response(req, code=400, msg='Error creating subscription: %s' % e)
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
