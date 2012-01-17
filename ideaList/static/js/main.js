////////////////////////////////////////////////////
// The JS code for ideaList's main view
////////////////////////////////////////////////////

///////////// GENERAL HELPER FUNCTIONS /////////////

function array_diff(a, b) {
  return a.filter(function(i) {return $.inArray(i, b) < 0;});
}
function array_intersect(a, b) {
  return a.filter(function(i) {return $.inArray(i, b) >= 0;});
}
// Make a level-1 clone (shallowish)
function cloneObject(obj) {
  var newObj = {};
  for (var i in obj)
    newObj[i] = obj[i];
  return newObj; 
}
function objectKeys(obj) {
  return $.map(obj, function(x,y) { return y; });
}
// Convert an object to array and sort by position attribute of values
function valuesSortedByPosition(obj) {
  return $.map(obj, function(x){return x;})
    .sort(function(a,b) {return a.position - b.position;});
}
// Convert an object to array and sort by id attribute of values
function valuesSortedById(obj) {
  return $.map(obj, function(x){return x;})
    .sort(function(a,b) {return a.id - b.id;});
}

function debug() {
  //$('#debug').append('<div>'+arguments[0]+'</div>');
  // Set a timeout to work around bugs:
  var origArguments = arguments;
  setTimeout(function(){console.debug.apply(console, origArguments)}, 1);
}

///////////// GENERAL DOM MANIPULATION /////////////

// Make the main view correspond to newState
function mergeState(newState) {
  if (!newState) {
    debug('Tried to merge null/undefined state');
    return false;
  }
  updateSubscriptions(newState);
  updateListMenu(newState);
  state_timestamp = new Date().getTime();
}

function updateSubscriptions(newState) {
  var old_sub_ids = objectKeys(state.subscriptions);
  var new_sub_ids = objectKeys(newState.subscriptions);
  var subs_to_add = array_diff(new_sub_ids, old_sub_ids);
  var subs_to_remove = array_diff(old_sub_ids, new_sub_ids);
  var subs_to_update = array_intersect(old_sub_ids, new_sub_ids);
//  debug("Subs to add/remove/update: "
//    +"("+subs_to_add+")/("+subs_to_remove+")/("+subs_to_update+")");

  for(var i in subs_to_add)
    addSubscription(newState.subscriptions[subs_to_add[i]], initDone);
  for(var i in subs_to_remove)
    removeSubscription(state.subscriptions[subs_to_remove[i]], true);
  for(var i in subs_to_update)
    updateSubscription(newState.subscriptions[subs_to_update[i]]);
}

// To be called as part of mergeState: after subscriptions have been updated
function updateListMenu(newState) {
  var newLists = valuesSortedById(newState.lists);
  if (state && state.lists) {
    // Check if update is necessary (if lists or subscriptions have changed)
    var oldLists = valuesSortedById(state.lists);
    var listsChanged = false;
    if (newLists.length != oldLists.length) {
      listsChanged = true;
    } else {
      for (var i in newLists) {
        var n = newLists[i]; var o = oldLists[i];
        if (n.id != o.id || n.name != o.name
            || subOfList[n.id] != oldSubOfList[n.id]) {
          listsChanged = true;
          break;
        }
      }
    }
    if (!listsChanged)
      return;
  }
  // Generate content for #listmenu
  var listMenu = $('<ul id="listmenu" class="listmenu" />');
  newLists.sort(function(a, b) {
    var an = a.name.toLowerCase(); var bn = b.name.toLowerCase();
    return an < bn ? -1 : (an > bn ? 1 : 0);
  });
  function toggleSubHandler(e) {
    var res = /^(subscribe|unsubscribe)_list_(\d+)$/.exec($(this).attr('id'));
    if (!res || res.length != 3) {
      debug('Called for invalid id');
      return false;
    }
    var url = res[1]=='subscribe' ? 'add_subscription/'
      : 'remove_subscription/';
    $.ajax(url, {dataType: "json", type: "POST", data: {list_id:res[2]}})
      .done(function(data) { mergeState(data.state); })
      .fail(get_ajax_fail_handler('add_subscription'));
  }
  function removeListHandler(e) {
    var res = /^remove_list_(\d+)$/.exec($(this).attr('id'));
    if (!res || res.length != 2) {
      debug('Called for invalid element id');
      return false;
    }
    $.ajax('remove_list/',
        {dataType: "json", type: "POST", data: {list_id:res[1]}})
      .done(function(data) { mergeState(data.state); })
      .fail(get_ajax_fail_handler('add_subscription'));
  }
  for (var i in newLists) {
    var l = newLists[i];
    var toggleSubButton = $('<a class="listaction" href="#" />');
    if (subOfList[l.id] == undefined)
      toggleSubButton.html('+').attr('id', 'subscribe_list_'+l.id);
    else
      toggleSubButton.html('&minus;').attr('id', 'unsubscribe_list_'+l.id);
    toggleSubButton.click(toggleSubHandler);
    var row = $('<li />').append(toggleSubButton).append('&nbsp;'+l.name);
    if (l.owner_id = user_id) {
      var removeButton = $('<a id="remove_list_'+l.id+'"'
            +' class="listaction" title="Delete" href="#">&nbsp;&times;</a>')
            .click(removeListHandler);
      row.append(removeButton);
    }
    listMenu.append(row);
  }
  $("#lists_dropdown").html(listMenu);
  oldSubOfList = cloneObject(subOfList);
  state.lists = newState.lists;
}

function refresh() {
  $.ajax('get_state/', { dataType: "json", type: "GET" })
    .done(function(data) { mergeState(data.state); })
    .fail(get_ajax_fail_handler('refresh'));
}
function refresher() {
  if (autorefresh_freq < 3) {
    debug('Autorefresh switching off, frequency is too low: '+autorefresh_freq);
    return;
  }
  var now = new Date().getTime();
  if (now - state_timestamp > autorefresh_freq*1000) {
    refresh();
    setTimeout(refresher, autorefresh_freq*1000);
  } else {
    // state too fresh, new attempt when data is old enough
    setTimeout(refresher, autorefresh_freq*1000 - (now-state_timestamp));
  }
}

///////////// COMMON HELPERS /////////////

function get_ajax_fail_handler(action) {
  if (!action)
    action = "";
  return function(jqXHR, textStatus, errorThrown) {
    var data = parseErrorThrown(errorThrown);
    debug(action+": error: "+(data && data.msg ? data.msg : textStatus));
    if (data && data.state)
      mergeState(data.state);
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

function moveHandler(e) {
  e.preventDefault();
  var obj_elem = $(this).parent();
  var res = /^move_(item|subscription)_(\d+)_(up|down)$/
    .exec($(this).attr('id'));
  if (!res || res.length != 4)
    return false;
  var obj_type = res[1];
  var obj_id = res[2];
  var direction = res[3];
  var obj_before = null; // Item before which to insert obj_elem
  if (direction == 'up')
    obj_before = obj_elem.prev();
  else
    obj_before = obj_elem.next();
  if (obj_before.length != 1 || !obj_before.hasClass(obj_type)) {
    debug('Not moving; already topmost/bottommost.');
    return false;
  }
  data = {where:direction};
  data[obj_type+'_id'] = obj_id;
  $.ajax('move_'+obj_type+'/', {
    dataType:"json", type:"POST", data:data
  }).done(function(data) {
    mergeState(data.state);
  }).fail(get_ajax_fail_handler('move_'+obj_type));
}

///////////// SUBSCRIPTION RELATED DOM MANIPULATION /////////////

function initAddItemField(field) {
  return field.blur(function() {
    if($(this).val() == "")
      $(this).val(newitemText).addClass("newitem_blur");
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
      if (!res || res.length != 3)
        return false;
      var pos = res[1];
      var list_id = res[2];
      var position = (pos == 'begin' ? 0 : -1);
      $.ajax('add_item/', {
        dataType: "json",
        type: "POST",
        data: {list:list_id, text:val, position:position},
      }).done(function(data) {
        addfield.val("").blur(); // Reset add item field
        mergeState(data.state);
      }).fail(get_ajax_fail_handler('add_item'));
    }
  }).addClass("newitem_blur");
}
function makeAddItemField(subscr, pos) {
  if (pos == null)
    pos = 'end';
  var addItemHtml =
    $('<input id="add_to_'+pos+'_of_list_'+subscr.list.id+'"'
    +' class="newitem" type="text" value="'+newitemText+'"></input>');
  initAddItemField(addItemHtml);
  return addItemHtml;
}
function makeSubscription(s) {
  // TODO: add add item button
  var l = s.list;
  var subscriptionHtml = $('<li id="subscription_'+s.id+'"'
      +' class="subscription"></li>');

  function minimizationHandler(e) {
    var res = /^minmax_subscription_(\d+)$/
      .exec($(this).attr('id'));
    if (!res || res.length != 2)
      return false;
    var s_id = res[1];
    var action = state.subscriptions[s_id].minimized ? 'maximize' : 'minimize';
    $.ajax(action+'_subscription/', {
      dataType: "json", type: "POST", data: {subscription_id:s_id} })
    .done(function(data) { mergeState(data.state); })
    .fail(get_ajax_fail_handler(action+'_subscription'));
  }
  var minimizationButtonHtml = $('<a id="minmax_subscription_'+s.id+'"'
      +' title="minimize/maximize" class="subscriptionaction" href="#">'
      +(s.minimized?'+':'&minus;')+'</a>').click(minimizationHandler);

  var listNameHtml = $('<span id="subscription_'+s.id+'_listname"'
      +' class="list-name">'+l.name+'</span>')
      .editable(editableUrl, editableSettings);
  var moveUpHtml = $('<a id="move_subscription_'+s.id+'_up"'
      +' class="subscriptionaction move_subscription" href="#">&uarr;</a>')
      .click(moveHandler);
  var moveDownHtml = $('<a id="move_subscription_'+s.id+'_down"'
      +' class="subscriptionaction move_subscription" href="#">&darr;</a>')
      .click(moveHandler);
  var itemListHtml = $('<ul class="itemlist"></ul>\n');
  subscriptionHtml
    .append(minimizationButtonHtml)
    .append('&nbsp;').append(listNameHtml)
    .append('&nbsp;').append(moveUpHtml)
    .append('&nbsp;').append(moveDownHtml);
  var items = valuesSortedByPosition(l.items);
  for (var i in items) {
    var itemHtml = makeItem(items[i]);
    itemListHtml.append(itemHtml);
  }
  itemListHtml.append($('<li/>').append(makeAddItemField(s, 'end')));
  if (s.minimized)
    itemListHtml.hide();
  subscriptionHtml.append(itemListHtml);
  return subscriptionHtml;
}
function insertSubscriptionToDOM(s, subscriptionHtml, animate) {
  var cursubs = valuesSortedByPosition(state.subscriptions);
  if (cursubs.length == 0 || s.position == 0) {
    //debug('Inserting sub '+s.id+' to beginning');
    $('#listlist').prepend(subscriptionHtml);
  } else {
    var added = false;
    for (var i in cursubs) {
      if (cursubs[i].id == s.id)
        continue;
      if (cursubs[i].position >= s.position) {
        //debug('Inserting sub '+s.id+' before sub '+cursubs[i].id);
        $("#subscription_"+cursubs[i].id).before(subscriptionHtml);
        added = true;
        break;
      }
    }
    if(!added) {
      //debug('Inserting sub '+s.id+' to end');
      $('#listlist').append(subscriptionHtml);
    }
  }
  if (animate)
    subscriptionHtml.hide().show('blind', {direction:'vertical'}, 1000);
}
function addSubscription(s, animate) {
  debug('Adding subscription '+s.id+' ('+s.list.name+')');
  if ($('#subscription_'+s.id).length != 0) {
    debug('Tried to add subscription '+s.id+', but it already exists');
    return;
  }
  var subscriptionHtml = makeSubscription(s);
  insertSubscriptionToDOM(s, subscriptionHtml, animate)
  state.subscriptions[s.id] = s;
  subOfList[s.list.id] = s.id;
}
function removeSubscription(s, animate) {
  debug('Removing subscription '+s.id+' ('+s.list.name+')');
  // Find list that corresponds to this subscription id
  var sub = $('#subscription_'+s.id);
  if (sub.length == 0)
    debug('Could not remove subscription '+s.id+": not found");
  if (animate)
    $('#subscription_'+s.id).hide(2000, function(){$(this).remove()});
  else
    $('#subscription_'+s.id).remove();
  delete state.subscriptions[s.id];
  delete subOfList[s.list.id]
}
function updateSubscription(s) {
  //debug('Updating subscription '+s.id+' ('+s.list.name+')');
  var old_sub = state.subscriptions[s.id];
  var old_item_ids = objectKeys(old_sub.list.items);
  var new_item_ids = objectKeys(s.list.items);
  var items_to_remove = array_diff(old_item_ids, new_item_ids);
  var items_to_add = array_diff(new_item_ids, old_item_ids);
  var items_to_update = array_intersect(old_item_ids, new_item_ids);
  //debug("Items to add/remove/update: "
  //  +"("+items_to_add+")/("+items_to_remove+")/("+items_to_update+")");
  for(var i in items_to_add)
    addItem(s.list.items[items_to_add[i]], true);
  for(var i in items_to_remove)
    removeItem(old_sub.list.items[items_to_remove[i]], true);
  for(var i in items_to_update)
    updateItem(s.list.items[items_to_update[i]], true);

  var updated = [];
  if(s.list.name != old_sub.list.name) {
    $('#subscription_'+s.id+'_listname').html(s.list.name);
    state.subscriptions[s.id].list.name = s.list.name;
    updated.push('listname');
  }
  if (s.position != old_sub.position) {
    insertSubscriptionToDOM(s, $('#subscription_'+s.id).detach(), true);
    state.subscriptions[s.id].position = s.position;
    updated.push('position');
  }
  if (s.minimized != old_sub.minimized) {
    if (s.minimized) {
      $('#minmax_subscription_'+s.id).html('+');
      $('#subscription_'+s.id+' > .itemlist').slideUp();
    } else {
      $('#minmax_subscription_'+s.id).html('&minus;');
      $('#subscription_'+s.id+' > .itemlist').slideDown();
    }
    state.subscriptions[s.id].minimized = s.minimized;
    updated.push('minimized');
  }
  if (updated.length > 0) {
    if ($.inArray('listname',updated)>=0 && $.inArray('position',updated)<0) {
      $('#subscription_'+s.id+'_listname')
        .effect('highlight', {color:'lightgreen'}, 2000);
    }
    debug('Updated '+updated.join(', ').replace(/, ([^,]+)$/, ' and $1')
      +' of subscription '+s.id+' ('+s.list.name+')');
  }
}

///////////// ITEM RELATED DOM MANIPULATION /////////////

function makeItem(itemdata) {
  function removeItemHandler(e) {
    e.preventDefault();
    var item_elem = $(this).parent();
    var res = /^remove_item_(\d+)$/.exec($(this).attr('id'));
    if (!res || res.length != 2)
      return false;
    var item_id = res[1];
    $.ajax('remove_item/',{dataType:"json",type:"POST",data:{item_id:item_id}})
      .done(function(data) { mergeState(data.state); })
      .fail(get_ajax_fail_handler('remove_item'));
  }
  var item_id = itemdata.id;
  var itemHtml = $('<li id="item_'+item_id+'" class="item"></li>');
  var itemTextHtml = $('<span id="item_'+item_id+'_text" class="item-text">'
      +itemdata.text+'</span>').editable(editableUrl, editableSettings);
  var removeHtml = $('<a id="remove_item_'+item_id
      +'" class="itemaction remove_item" href="#">&times;</a>')
      .click(removeItemHandler);
  var moveUpHtml = $('<a id="move_item_'+item_id+'_up"'
      +' class="itemaction move_item" href="#">&uarr;</a>')
      .click(moveHandler);
  var moveDownHtml = $('<a id="move_item_'+item_id+'_down"'
      +' class="itemaction move_item" href="#">&darr;</a>')
      .click(moveHandler);
  itemHtml
    .append(itemTextHtml)
    .append('&nbsp;').append(removeHtml)
    .append('&nbsp;').append(moveUpHtml)
    .append('&nbsp;').append(moveDownHtml);
  return itemHtml;
}
// Insert an already constructed itemHtml to DOM
function insertItemToDOM(item, itemHtml, animate) {
  sub_id = subOfList[item.list_id];
  var curitems = valuesSortedByPosition(state.subscriptions[sub_id].list.items);
  if (objectKeys(curitems).length == 0 || item.position == 0) {
    //debug('  Adding item to first position');
    $('#subscription_'+sub_id+' > ul').prepend(itemHtml);
  } else {
    var added = false;
    for (var i in curitems) {
      if (curitems[i].id == item.id)
        continue;
      //debug('    Checking idx '+i+': '+curitems[i].text);
      if (curitems[i].position >= item.position) {
        //debug('      Adding before idx '+i);
        $('#item_'+curitems[i].id).before(itemHtml);
        added = true;
        break;
      }
    }
    if (!added) {
      //debug('  Adding item to last position');
      $('#subscription_'+sub_id+' > ul > li.item').last().after(itemHtml);
    }
  }
  if (animate)
    itemHtml.hide().show(1000);
}
function addItem(item, animate) {
  debug('Adding item '+item.id+' ('+item.text+')');
  var list_id = item.list_id;
  sub_id = subOfList[item.list_id];
  if (sub_id === undefined) {
    debug('Tried to add an item to a nonexisting list');
    return false;
  }
  if ($('#item_'+item.id).length != 0) {
    debug('Tried to add item '+item.id+', but it already exists');
    return;
  }
  if ($('#subscription_'+sub_id).length == 0) {
    debug('Tried to add item '+item.id+' to a nonexisting subscription');
    return;
  }
  var itemHtml = makeItem(item);
  insertItemToDOM(item, itemHtml, animate);
  state.subscriptions[sub_id].list.items[item.id] = item;
}
function removeItem(item, animate) {
  debug('Removing item '+item.id+' ('+item.text+')');
  if (animate)
    $('#item_'+item.id).hide(1000, function(){$(this).remove()});
  else
    $('#item_'+item.id).remove();
  delete state.subscriptions[subOfList[item.list_id]].list.items[item.id];
}
function updateItem(newI) {
  curI = state.subscriptions[subOfList[newI.list_id]].list.items[newI.id];
  if (!curI) {
    debug('Tried to update a nonexisting item: '+item.id);
    return
  }
  var updated = [];
  if (newI.text != curI.text) {
    $('#item_'+curI.id+"_text").html(newI.text);
    updated.push('text');
  }
  if (newI.priority != curI.priority) {
    // TODO: update priority when it is implemented
    updated.push('priority');
  }
  if (newI.url != curI.url) {
    // TODO: update url when it is implemented
    updated.push('url');
  }
  if (newI.position != curI.position) {
    insertItemToDOM(newI, $('#item_'+curI.id).detach(), true);
    updated.push('position');
  }
  state.subscriptions[subOfList[curI.list_id]].list.items[curI.id] = newI;
  if (updated.length > 0) {
    // Flash the item if it wasn't moved (to avoid double animation)
    if ($.inArray('position', updated) == -1)
      $('#item_'+curI.id).effect('highlight', {color:'lightgreen'}, 2000);
    debug('Updated '+updated.join(', ').replace(/, ([^,]+)$/, ' and $1')
      +' of item '+curI.id+' ('+curI.text+')');
  }
}

///////////// STATUSLIGHT RELATED STUFF /////////////

var pendingAjaxCalls = 0;
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

///////////// INITIALIZATION /////////////

// Django CSRF protection for AJAX calls
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

$.ajaxSetup({timeout:3000});

// The text that appears in the new item boxes
var newitemText = "New item..."

// Refresh when state is this old (in seconds). Must be at least 3 seconds.
// Set to -1 to disable autorefresh.
var autorefresh_freq = -30;

var editableUrl = 'edit_text/';
var editableSettings = {
    tooltip: "Click to edit",
    style:   "inherit",
    id:      "element_id",
    name:    "text",
    callback: function(value) {
      try {
        var data = $.parseJSON(value);
      } catch(e) {
        debug("Couldn't parse JSON: ", e);
        return;
      }
      mergeState(data.state);
      return data.text;
    }};

function initTopBar() {
  $("#refresh_button").click(function() {refresh();});
  $("#arrows_button").click(function() {
    if ($('.move_item').css('display') == 'none') {
      $('.move_item').add('.move_subscription').fadeIn();
      $('> span', this).html('Arrows off');
    } else {
      $('.move_item').add('.move_subscription').fadeOut();
      $('> span', this).html('Arrows on');
    }
  });
  $("#lists_button").click(function(e) {$('.dropcontent',this).slideToggle()});
  $(".dropcontent").click(function(e) { e.stopPropagation(); });
}

function initCreateList() {
  $('#create_list_name').hide();
  $('#create_list_nameinput').blur(function(e) {
    $('#create_list_name').hide();
    $('#create_list_link').show();
  }).keydown(function(e) {
    if(e.keyCode == 13) {
      var val = $(this).val();
      if (val.length == 0)
        return false;
      $.ajax('add_list/',
        { dataType: "json", type: "POST", data: {name:val, subscribe:true} }
      ).done(function(data) {
        $('#create_list_nameinput').blur(); //Does hide+show
        mergeState(data.state);
      }).fail(get_ajax_fail_handler('add_list'));
    }
  });
  $('#create_list_link').click(function(e) {
    $(this).hide();
    $('#create_list_name').show()
    $('#create_list_nameinput').focus();
  });

}


var initDone = false;
$(document).ready(function() {
  initTopBar();
  initCreateList();
  setStatusLight();
  state = {subscriptions: {}};
  subOfList = {};
  mergeState(init_state);
  refresher();
  initDone = true;
});
