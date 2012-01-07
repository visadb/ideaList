var newitemText = "New item..."
var pendingAjaxCalls = 0;
var init_done = false;

function array_diff(a, b) {
  return a.filter(function(i) {return b.indexOf(i) < 0;});
};
function array_intersect(a, b) {
  return a.filter(function(i) {return b.indexOf(i) >= 0;});
};

var editableUrl = '/ideaList/edittext/';
var editableSettings = {
    tooltip: "Click to edit",
    style:   "inherit",
    id:      "element_id",
    name:    "text",
  };

function debug(str) {
  if(init_done) {
    console.debug(str);
  } else {
    var item = $('<div>'+str+'<br /></div>')
    $("#debug").append(item);
    item.delay(10000).hide(2000, function(){item.remove()});
  }
}

function parseErrorThrown(errorThrown) {
  try {
    var data = $.parseJSON(errorThrown);
  } catch(e) {
    debug("Couldn't parse errorThrown: "+e);
    return null;
  }
  return data;
}

function makeItem(itemdata) {
  function removeitemHandler(e) {
    e.preventDefault();
    var item_elem = $(this).parent();
    var res = /^remove_item_(\d+)$/.exec($(this).attr('id'));
    if (res.length != 2)
      return false;
    var item_id = res[1];
    $.ajax('/ideaList/removeitem/', {
      dataType: "json",
      type: "POST",
      data: {item_id:item_id},
    }).done(function(data) {
      debug("Item "+item_id+" removed");
      mergeState(data['state']);
    }).fail(function(jqXHR, textStatus, errorThrown) {
      debug("Error in remove item: "+textStatus);
      var data = parseErrorThrown(errorThrown);
      if (data && data['state'])
        mergeState(data['state']);
    });
  }
  function moveitemHandler(e) {
    e.preventDefault();
    var item_elem = $(this).parent();
    var res = /^move_item_(\d+)_(up|down)$/.exec($(this).attr('id'));
    if (res.length != 3)
      return false;
    var item_id = res[1];
    var direction = res[2];
    var item_before = null; // Item before which to insert item_elem
    if (direction == 'up')
      item_before = item_elem.prev();
    else
      item_before = item_elem.next();
    if (item_before.length != 1 || !item_before.hasClass('item'))
      return false;
    $.ajax('/ideaList/moveitem/', {
      dataType: "text",
      type: "POST",
      data: {
        item_id:item_id,
        where:direction,
      },
    }).done(function() {
      mergeState(data['state']);
    }).fail(function(jqXHR, textStatus, errorThrown) {
      debug("Error in remove item: "+textStatus);
      var data = parseErrorThrown(errorThrown);
      if (data && data['state'])
        mergeState(data['state']);
    });
  }
  var item_id = itemdata['id'];
  var text = itemdata['text'];
  var itemTextHtml = $('<span id="item_'+item_id+'_text" class="item-text">'+text+'</span>').editable(editableUrl, editableSettings);;
  var removeHtml = $('<a id="remove_item_'+item_id+'" class="itemaction removeitem" href="#">&#10005;</a>').click(removeitemHandler);
  var moveUpHtml = $('<a id="move_item_'+item_id+'_up" class="itemaction moveitem" href="#">&uarr;</a>').click(moveitemHandler);
  var moveDownHtml = $('<a id="move_item_'+item_id+'_down" class="itemaction moveitem" href="#">&darr;</a>').click(moveitemHandler);
  var itemHtml = $('<li id="item_'+item_id+'" class="item"></li>')
    .data('itemdata', itemdata);
  itemHtml
    .append(itemTextHtml)
    .append('&nbsp;').append(removeHtml)
    .append('&nbsp;').append(moveUpHtml)
    .append('&nbsp;').append(moveDownHtml);
  return itemHtml;
}

function addItem(itemdata) {
  debug('Adding item '+itemdata['id']);
  var list_id = itemdata['list_id'];
  if ($('#item_'+itemdata['id']).length != 0) {
    debug('Tried to add item '+itemdata['id']+', but it already exists');
    return;
  }
  if ($('#list_'+list_id).length == 0) {
    debug('Tried to add item '+itemdata['id']+' to a nonexisting list');
    return;
  }
  var pos = itemdata['position'];
  var curitems = $('#list_'+list_id+' > ul > li.item');
  var itemHtml = makeItem(itemdata)
  if (curitems.length == 0 || pos == 0) {
    $('#list_'+list_id+' > ul').prepend(itemHtml);
  } else {
    items_array = curitems.toArray();
    for (var i in items_array) {
      item = items_array[i];
      if ($(item).data('itemdata')['position'] > pos) {
        $(item).before(itemHtml);
        return;
      }
      curitems.last().after(itemHtml);
    }
  }
}

function removeItem(id,instant) {
  debug('Removing item '+id);
  if (instant)
    $('#item_'+id).remove();
  else
    $('#item_'+id).hide(1000, function(){$(this).remove()});
}

function mergeState(newstate) {
  if (!newstate) {
    debug('Tried to merge null/undefined state');
    return false;
  }
  function make_id_dict(subs) {
    var dict = {};
    for (var i in subs)
      dict[subs[i]['id']] = subs[i];
    return dict;
  }
  if (init_done)
    var oldstate = state;
  else
    var oldstate = {subscriptions: []};
  var old_sub_ids= $.map(oldstate['subscriptions'],function(s){return s['id']});
  var new_sub_ids= $.map(newstate['subscriptions'],function(s){return s['id']});
  var new_subs_by_id = make_id_dict(newstate['subscriptions']);
  var subs_to_delete = array_diff(old_sub_ids, new_sub_ids);
  var subs_to_add = array_diff(new_sub_ids, old_sub_ids);
  var subs_to_update = array_intersect(old_sub_ids, new_sub_ids);
  debug("Subs to delete/add/update: "
    +"("+subs_to_delete+")/("+subs_to_add+")/("+subs_to_update+")");

  for(var i in subs_to_delete)
    removeSubscription(subs_to_delete[i]);
  for(var i in subs_to_add)
    addSubscription(new_subs_by_id[subs_to_add[i]]);
  for(var i in subs_to_update)
    updateSubscription(new_subs_by_id[subs_to_update[i]]);
  state = newstate;
}
function updateSubscription(s) {
  // TODO: make this more like mergeState
  removeSubscription(s['id'], true);
  addSubscription(s);
}

function initAddItemField(field) {
  return field.blur(function() {
    if($(this).val() == "") {
      $(this).val(newitemText)
        .addClass("newitem_blur");
    }
  }).focus(function() {
    $(this).removeClass("newitem_blur");
    if($(this).val() == newitemText)
      $(this).val("");
  }).keydown(function(e) {
    if(e.keyCode == 13) {
      var val = $(this).val();
      var addfield = $(this); //For resetting later...
      if (val.length == 0)
        return false;
      var res = /^add_to_(end|begin)_of_list_(\d+)$/.exec($(this).attr('id'));
      if (res.length != 3)
        return false;
      var pos = res[1];
      var list_id = res[2];
      var position = (pos == 'begin' ? 0 : -1);
      $.ajax('/ideaList/additem/', {
        dataType: "json",
        type: "POST",
        data: {list:list_id, text:val, position:position},
      }).done(function(data) {
        addfield.val("").blur(); // Reset additem field
        mergeState(data['state']);
      }).fail(function(jqXHR, textStatus, errorThrown) {
        msg = textStatus;
        var data = parseErrorThrown(errorThrown);
        if (data) {
          if (data['msg'])
            msg = data['msg'];
          if (data['state'])
            mergeState(data['state']);
        }
        debug("Error in adding item: "+msg);
      });
    }
  }).addClass("newitem_blur");
}
function makeAddItemField(subscr, pos) {
  if (pos == null)
    pos = 'end';
  var addItemHtml =
    $('<input id="add_to_'+pos+'_of_list_'+subscr['list']['id']+'"'
    +' class="newitem" type="text" value="'+newitemText+'"></input>');
  initAddItemField(addItemHtml);
  return addItemHtml;
}

function makeSubscription(s) {
  var l = s['list'];
  var listHtml = $('<li id="subscription_'+s['id']+'" class="list">'+l['name']+'</li>\n')
    .data('subscriptiondata', s);
  var itemListHtml = $('<ul class="itemlist"></ul>\n');
  for (var i in l['items']) {
    var itemHtml = makeItem(l['items'][i]);
    itemListHtml.append(itemHtml);
  }
  itemListHtml.append($('<li></li>').append(makeAddItemField(s, 'end')));
  listHtml.append(itemListHtml);
  return listHtml;
}


function addSubscription(subscriptiondata) {
  debug('Adding subscription '+subscriptiondata['id']);
  var list_id = subscriptiondata['list']['id'];
  if ($('#list_'+list_id).length != 0) {
    debug('Tried to add list '+list_id+', but it already exists');
    return;
  }
  var pos = subscriptiondata['position'];
  var curlists = $('#listlist > li.list');
  var listHtml = makeSubscription(subscriptiondata);
  if (curlists.length == 0 || pos == 0) {
    $('#listlist').prepend(listHtml);
  } else {
    lists_array = curlists.toArray();
    for (var i in lists_array) {
      var list = lists_array[i];
      if ($(list).data('subscriptiondata')['position'] > pos) {
        $(list).before(listHtml);
        return;
      }
      $('#listlist').append(listHtml);
    }
  }
}
function removeList(id,instant) {
  if (instant)
    $('#list_'+id).remove();
  else
    $('#list_'+id).hide(1000, function(){$(this).remove()});
}
function removeSubscription(id, instant) {
  debug('Removing subscription '+id);
  // Find list that corresponds to this subscription id
  var sub = $('#subscription_'+id);
  if (sub.length == 0)
    debug('Could not remove subscription '+id+": not found");
  if (instant)
    $('#subscription_'+id).remove();
  else
    $('#subscription_'+id).hide(1000, function(){$(this).remove()});
}


$(document).ready(function() {
  setStatusLight();
  mergeState(state);
  init_done = true;
});

$.ajaxSetup({timeout:3000});


function setStatusLight() {
  if (pendingAjaxCalls > 0)
    $('#status-light').attr('class', 'yellow');
  else
    $('#status-light').attr('class', 'green');
}

$(document).ajaxSend(function() {
  pendingAjaxCalls++;
  setStatusLight();
});
$(document).ajaxSuccess(function() {
  pendingAjaxCalls--;
  setStatusLight();
});
$(document).ajaxError(function() {
  pendingAjaxCalls--;
  $('#status-light').attr('class', 'red');
  setTimeout('setStatusLight()', 2000);
});


// CSRF protection for AJAX calls
$(document).ajaxSend(function(event, xhr, settings) {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  function safeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  if (!safeMethod(settings.type) && !settings.crossDomain) {
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
  }
});
