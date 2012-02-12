/**
 * The JS code for ideaList's main view
 * Copyright (c) 2012 Visa Putkinen
 *
 * License: GPLv3: http://www.gnu.org/licenses/gpl.html
 */

///////////// INLINED PLUGINS /////////////

/**
 * jQuery Cookie plugin - https://github.com/carhartl/jquery-cookie
 *
 * Copyright (c) 2010 Klaus Hartl, @carhartl
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */
(function($) {
  $.cookie = function(key, value, options) {
    if (arguments.length > 1 && (!/Object/.test(Object.prototype.toString.call(value)) || value === null || value === undefined)) {
      options = $.extend({}, options);
      if (value === null || value === undefined)
        options.expires = -1;
      if (typeof options.expires === 'number') {
        var days = options.expires, t = options.expires = new Date();
        t.setDate(t.getDate() + days);
      }
      value = String(value);
      return (document.cookie = [
        encodeURIComponent(key), '=', options.raw ? value : encodeURIComponent(value),
        options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
        options.path    ? '; path=' + options.path : '',
        options.domain  ? '; domain=' + options.domain : '',
        options.secure  ? '; secure' : ''
      ].join(''));
    }
    options = value || {};
    var decode = options.raw ? function(s) { return s; } : decodeURIComponent;
    var pairs = document.cookie.split('; ');
    for (var i = 0, pair; pair = pairs[i] && pairs[i].split('='); i++) {
      if (decode(pair[0]) === key) return decode(pair[1] || ''); // IE saves cookies with empty string as "c; ", e.g. without "=" as opposed to EOMB, thus pair[1] may be undefined
    }
    return null;
  };
})(jQuery);

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
  var origArguments = arguments;
  if (initDone)
    console.debug.apply(console, origArguments);
  else
    setTimeout(function(){console.debug.apply(console, origArguments)}, 1);
}

///////////// FLASH MESSAGES /////////////

function flashMessage(msg, type, duration) {
  var flash = $('<div class="message"></div>').html(msg).addClass(type)
    .delay(duration).hide(1000);
  $('#messages').append(flash);
}
function flashSuccess(msg) {
  flashMessage(msg, 'success', 1500);
}
function flashError(msg) {
  flashMessage(msg, 'error', 5000);
}

///////////// GENERAL DOM MANIPULATION /////////////

// Make the main view correspond to newState
function mergeState(newState) {
  if (!newState) {
    debug('Tried to merge null/undefined state');
    return false;
  }
  updateSubscriptions(newState);
  updateListMenu(newState); // must come after updateSubscriptions
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

  for(var i in subs_to_remove)
    removeSubscription(state.subscriptions[subs_to_remove[i]], true);
  for(var i in subs_to_add)
    addSubscription(newState.subscriptions[subs_to_add[i]], initDone);
  updateChangedSubscriptions(
    $.map(subs_to_update, function(i){return newState.subscriptions[i];}));
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
      .done(function(data) {
        flashSuccess('list '
          +state.lists[res[2]].name+' '+res[1]+'d');
        mergeState(data.state);
      }).fail(getAjaxFailHandler('toggle subscription'));
  }
  function removeListHandler(e) {
    var res = /^remove_list_(\d+)$/.exec($(this).attr('id'));
    if (!res || res.length != 2) {
      debug('Called for invalid element id');
      return false;
    }
    $.ajax('remove_list/',
        {dataType: "json", type: "POST", data: {list_id:res[1]}})
      .done(function(data) {
        flashSuccess('list '
         +state.subscriptions[subOfList[res[1]]].list.name+' removed');
        mergeState(data.state);
      }).fail(getAjaxFailHandler('remove list'));
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
  $("#listmenu_listlist").html(listMenu);
  oldSubOfList = cloneObject(subOfList);
  state.lists = newState.lists;
}

function refresh(flashOnSuccess) {
  $.ajax('get_state/', { dataType: "json", type: "GET" })
    .done(function(data) {
      if (flashOnSuccess)
        flashSuccess('refreshed');
      mergeState(data.state);
    }).fail(getAjaxFailHandler('refresh'));
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

function getAjaxFailHandler(action) {
  if (!action)
    action = "";
  return function(jqXHR, textStatus, errorThrown) {
    var data = parseErrorThrown(errorThrown);
    console.error(action+" failed: "+(data && data.msg ? data.msg:textStatus));
    flashError(action+" failed");
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
  var res = /^move_(item|subscription)_(\d+)_(up|down)$/
    .exec($(this).attr('id'));
  if (!res || res.length != 4)
    return false;
  var obj_type = res[1];
  var obj_id = res[2];
  var direction = res[3];
  var obj_elem = $(this).parents('.'+obj_type);
  var obj_before = null; // Item before which to insert obj_elem
  if (direction == 'up')
    obj_before = obj_elem.prev();
  else
    obj_before = obj_elem.next();
  if (obj_before.length != 1) {
    debug('Not moving; already topmost/bottommost.');
    return false;
  }
  data = {where:direction};
  data[obj_type+'_id'] = obj_id;
  $.ajax('move_'+obj_type+'/', {
    dataType:"json", type:"POST", data:data
  }).done(function(data) {
    flashSuccess(obj_type+' moved');
    mergeState(data.state);
  }).fail(getAjaxFailHandler('move '+obj_type));
}

///////////// SUBSCRIPTION RELATED DOM MANIPULATION /////////////

function makeAddItemRow(list_id, pos) {
  if (pos == null)
    pos = 'end';
  var addItemHtml = $('<li class="additemrow" />');
  var addItemField = $('<input id="add_to_'+pos+'_of_list_'+list_id+'"'
    +' class="additem" type="text"></input>').keyup(function(e) {
      if(e.keyCode == 13) {
        $('#suggestion_box').hide();
        var addField = $(this); //For resetting later...
        var val = addField.val();
        if (val.length == 0)
          return false;
        var res = /^add_to_(end|begin|\d+)_of_list_(\d+)$/.exec(addField.attr('id'));
        if (!res || res.length != 3) {
          debug('addItemHandler called with for invalid element id');
          return false;
        }
        var pos = res[1];
        var list_id = res[2];
        var position = pos=='begin' ? 0 : (pos=='end' ? -1 : pos);
        $.ajax('add_item/', {
          dataType: "json",
          type: "POST",
          data: {list:list_id, text:val, position:position},
        }).done(function(data) {
          flashSuccess('item '+val+' added');
          if (!e.ctrlKey)
            addItemHtml.hide(500, function(){addItemHtml.remove()});
          else
            addField.val('');
          mergeState(data.state);
        }).fail(getAjaxFailHandler('add item'));
      } else {
        setSuggestionBoxItems(freqtreeGetItems($(this).val()));
      }
    });
  var cancelHtml = $('<a href="#" title="cancel" class="itemaction">&times;</a>')
    .click(function(e) {
      $('#suggestion_box').hide();
      addItemHtml.remove();
    });
  return addItemHtml.append(addItemField).append(cancelHtml);
}
function updateItemcount(sub_id, increment) {
  var itemCount = $('#itemcount_subscription_'+sub_id+' > span.count');
  var oldVal = parseInt(itemCount.html());
  var newVal = oldVal+increment;
  itemCount.html(newVal);
  if (oldVal != 1 && newVal == 1)
    $('#itemcount_subscription_'+sub_id+' > span.title').html('item');
  else if (oldVal == 1 && newVal != 1)
    $('#itemcount_subscription_'+sub_id+' > span.title').html('items');
}
function isSubscriptionMinimizedInCookie(sub_id) {
  var minimized = $.cookie('minimized');
  if (minimized == null)
    return false;
  return minimized.split(',').indexOf(''+sub_id) != -1;
}
function setSubscriptionMinimization(sub_id, minimize) {
  var itemlist = $('#subscription_'+sub_id+' > .itemlist');
  if (itemlist.length == 0)
    return;
  var minimized = $.cookie('minimized');
  if (minimized == null)
    minimized = '';
  var ids = minimized.split(',');
  if (minimize) {
    $('#minmax_subscription_'+sub_id).html('&#x25b6;');
    $('#subscription_'+sub_id+' > .itemlist').slideUp(500);
    $('#itemcount_subscription_'+sub_id).show();
    if (ids.indexOf(''+sub_id) == -1) {
      ids.push(sub_id);
      $.cookie('minimized', ids.join(','), {expires:365});
    }
  } else {
    $('#minmax_subscription_'+sub_id).html('&#x25bc;');
    $('#subscription_'+sub_id+' > .itemlist').slideDown(500);
    $('#itemcount_subscription_'+sub_id).hide();
    var idx = ids.indexOf(''+sub_id);
    if (idx != -1) {
      ids.splice(idx, 1);
      $.cookie('minimized', ids.join(','), {expires:365});
    }
  }
}
function minimizeSubscription(sub_id) {
  setSubscriptionMinimization(sub_id, true);
}
function maximizeSubscription(sub_id) {
  setSubscriptionMinimization(sub_id, false);
}
function makeSubscription(s) {
  var l = s.list;
  var subscriptionHtml = $('<li id="subscription_'+s.id+'"'
      +' class="subscription"></li>').data('id', s.id);
  var subscriptionTitleHtml = $('<span class="subscription-title"></span>');
  var itemListHtml = $('<ul class="itemlist"></ul>\n');
  // Workaround for bug in Android 1.5 browser: $.offset() crashes for invisible
  setTimeout(function() {
    itemListHtml.sortable({
      connectWith: '.itemlist',
      axis: 'y',
      cancel: '.additemrow',
      distance:10,
      start: function(e, ui) {
        old_prev_item = ui.item.prev('.item'); // For revert on AJAX fail
        old_sub_id = ui.item.parents('.subscription').data('id'); // ditto
        old_list_id = state.subscriptions[old_sub_id].list.id;
      },
      update: function(e, ui) {
        if (ui.sender != null)
          return; // prevent double ajax: this call is for the destination list
        var prev = ui.item.prev();
        var subscriptionElem = ui.item.parents('.subscription');
        var list_id = state.subscriptions[subscriptionElem.data('id')].list.id;
        var where = null;
        if (prev.length == 0) {
          where = 0;
        } else {
          where = state.subscriptions[subscriptionElem.data('id')]
            .list.items[prev.data('id')].position;
          if (ui.position.top<ui.originalPosition.top || list_id != old_list_id)
            where++; //If moving up or b/w lists, must be 1 greater than prev's
        }
        var data = {item_id:ui.item.data('id'), where:where}
        if (list_id != old_list_id)
          data.list_id = list_id;
        $.ajax('move_item/', { dataType:"json", type:"POST", data:data })
          .done(function(data) {
            flashSuccess('item moved (drag)');
            mergeState(data.state);
          }).fail(function(jqXHR, textStatus, errorThrown) {
            if (old_prev_item.length == 0)
              $('#subscription_'+old_sub_id+' > .itemlist').prepend(ui.item);
            else
              old_prev_item.after(ui.item);
            getAjaxFailHandler('drag item')(jqXHR, textStatus, errorThrown);
          });
      }
    });
  }, 1);

  function minimizationHandler(e) {
    var res = /^minmax_subscription_(\d+)$/
      .exec($(this).attr('id'));
    if (!res || res.length != 2)
      return false;
    var s_id = res[1];
    if ($('#subscription_'+s_id+' > .itemlist').is(':hidden'))
      maximizeSubscription(s_id);
    else
      minimizeSubscription(s_id);
  }
  function subscriptionAddItemHandler(e) {
    $('.additemrow').remove();
    var addItemField = makeAddItemRow(l.id, 'begin');
    itemListHtml.prepend(addItemField);
    $('.additem', addItemField).focus();
    showAndResetSuggestionBox();
  }
  var minimizationButtonHtml = $('<a id="minmax_subscription_'+s.id+'"'
      +' title="minimize/maximize" class="subscriptionaction minmax" href="#">'
      +(isSubscriptionMinimizedInCookie(s.id)?'&#x25b6;':'&#x25bc;')+'</a>')
      .click(minimizationHandler);

  var listNameHtml = $('<span id="subscription_'+s.id+'_listname"'
      +' class="list-name">'+l.name+'</span>')
      .editable(editableUrl, editableSettings);
  var addItemHtml = $('<a id="additem_list_'+l.id+'" title="Add item"'
      +' class="subscriptionaction" href="#">+</a>')
      .click(subscriptionAddItemHandler);
  var moveUpHtml = $('<a id="move_subscription_'+s.id+'_up" title="Move up"'
      +' class="subscriptionaction move_subscription" href="#">&uarr;</a>')
      .click(moveHandler);
  var moveDownHtml=$('<a id="move_subscription_'+s.id+'_down" title="Move down"'
      +' class="subscriptionaction move_subscription" href="#">&darr;</a>')
      .click(moveHandler);
  var nrOfItems = $.map(s.list.items, function(x){return 0;}).length;
  var itemCountHtml=$('<span id="itemcount_subscription_'+s.id+'"'
      +' title="Item count" class="itemcount">'
      +'(<span class="count">'+nrOfItems+'</span>'
      +' <span class="title">'+(nrOfItems==1?'item':'items')+'</span>)</span>')
      .css('display','none');
  subscriptionTitleHtml
    .append(minimizationButtonHtml)
    .append(listNameHtml)
    .append(itemCountHtml)
    .append(addItemHtml)
    .append(moveUpHtml)
    .append(moveDownHtml);

  if (!arrows_on) {
    moveUpHtml.hide();
    moveDownHtml.hide();
  }

  var items = valuesSortedByPosition(l.items);
  for (var i in items) {
    var itemHtml = makeItem(items[i]);
    itemListHtml.append(itemHtml);
  }
  if (isSubscriptionMinimizedInCookie(s.id)) {
    itemListHtml.hide();
    itemCountHtml.show();
  }

  subscriptionHtml.append(subscriptionTitleHtml).append(itemListHtml);
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
    subscriptionHtml.hide().show(500);
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
function updateChangedSubscriptions(subs) {
  var subsWhosePositionChanged = [];
  for (var i in subs) {
    var s = subs[i];
    //debug('Updating subscription '+s.id+' ('+s.list.name+')');
    var old_sub = state.subscriptions[s.id];
    var old_item_ids = objectKeys(old_sub.list.items);
    var new_item_ids = objectKeys(s.list.items);
    var items_to_remove = array_diff(old_item_ids, new_item_ids);
    var items_to_add = array_diff(new_item_ids, old_item_ids);
    var items_to_update = array_intersect(old_item_ids, new_item_ids);
    //debug("Items to add/remove/update: "
    //  +"("+items_to_add+")/("+items_to_remove+")/("+items_to_update+")");
    for(var j in items_to_add)
      addItem(s.list.items[items_to_add[j]], true);
    for(var j in items_to_remove)
      removeItem(old_sub.list.items[items_to_remove[j]], true);
    updateChangedItems(
      $.map(items_to_update, function(j){return s.list.items[j];}));

    var updated = [];
    if(s.list.name != old_sub.list.name) {
      $('#subscription_'+s.id+'_listname').html(s.list.name);
      state.subscriptions[s.id].list.name = s.list.name;
      updated.push('listname');
    }
    if (s.position != old_sub.position) {
      // Delay DOM update until all positions are updated
      subsWhosePositionChanged.push(s);
      state.subscriptions[s.id].position = s.position;
      updated.push('position');
    }
    if (s.minimized != old_sub.minimized) {
      if (s.minimized) {
        $('#minmax_subscription_'+s.id).html('&#x25b6;');
        $('#subscription_'+s.id+' > .itemlist').slideUp(500);
        $('#itemcount_subscription_'+s.id).show();
      } else {
        $('#minmax_subscription_'+s.id).html('&#x25bc;');
        $('#subscription_'+s.id+' > .itemlist').slideDown(500);
        $('#itemcount_subscription_'+s.id).hide();
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
  for (var i in subsWhosePositionChanged) {
    var s = subsWhosePositionChanged[i];
    insertSubscriptionToDOM(s, $('#subscription_'+s.id).detach(), false);
  }
}

///////////// ITEM RELATED DOM MANIPULATION /////////////


function makeItem(item) {
  function itemAddItemHandler(e) {
    $('.additemrow', addItemField).remove();
    var itemElem = $(this).parents('.item');
    var subscriptionElem = $(this).parents('.subscription');
    var subscription = state.subscriptions[subscriptionElem.data('id')];
    var addItemField = makeAddItemRow(subscription.list.id,
      subscription.list.items[itemElem.data('id')].position+1);
    itemElem.after(addItemField);
    $('.additem', addItemField).focus();
    showAndResetSuggestionBox();
  }
  var itemHtml = $('<li id="item_'+item.id+'" class="item"></li>')
    .data('id', item.id);
  var itemTextHtml = $('<span id="item_'+item.id+'_text" class="item-text">'
      +item.text+'</span>').editable(editableUrl, editableSettings);
  var linkHtml = $('<a id="item_'+item.id+'_link" class="itemlink"></a>')
    .attr('href', item.url);
  var checkHtml = $('<input type="checkbox" class="itemcheck"'
      +' value="'+item.id+'" />').change(updateNavbarItemactions);
  var addItemHtml = $('<a class="itemaction" title="Add item"'
      +' href="#">+</a>').click(itemAddItemHandler);
  var moveUpHtml = $('<a id="move_item_'+item.id+'_up" title="Move up"'
      +' class="itemaction move_item" href="#">&uarr;</a>')
      .click(moveHandler);
  var moveDownHtml = $('<a id="move_item_'+item.id+'_down" title="Move down"'
      +' class="itemaction move_item" href="#">&darr;</a>')
      .click(moveHandler);
  itemHtml
    .append(checkHtml)
    .append(itemTextHtml)
    .append(linkHtml)
    .append(addItemHtml)
    .append(moveUpHtml)
    .append(moveDownHtml);

  if (item.important)
    itemHtml.addClass('important');
  if (!arrows_on) {
    moveUpHtml.hide();
    moveDownHtml.hide();
  }
  if (item.url.length == 0)
    linkHtml.hide();

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
      $('#subscription_'+sub_id+' > ul').append(itemHtml);
    }
  }
  if (animate)
    itemHtml.hide().show(500);
}
function addItem(item, animate) {
  debug('Adding item '+item.id+' ('+item.text+')');
  var list_id = item.list_id;
  sub_id = subOfList[item.list_id];
  if (sub_id === undefined) {
    debug('Tried to add an item to a nonexisting list');
    return false;
  }
  if ($('#subscription_'+sub_id).length == 0) {
    debug('Tried to add item '+item.id+' to a nonexisting subscription');
    return;
  }
  var itemHtml = makeItem(item);
  insertItemToDOM(item, itemHtml, animate);
  state.subscriptions[sub_id].list.items[item.id] = item;
  updateItemcount(sub_id, +1);
}
function removeItem(item, animate) {
  debug('Removing item '+item.id+' ('+item.text+')');
  if (animate) {
    $('#item_'+item.id).hide(500, function(){
      $(this).remove();
      updateNavbarItemactions();
    });
  } else {
    $('#item_'+item.id).remove();
    updateNavbarItemactions();
  }
  delete state.subscriptions[subOfList[item.list_id]].list.items[item.id];
  updateItemcount(subOfList[item.list_id], -1);
}
function updateChangedItems(items) {
  var itemsWhosePositionChanged = [];
  for (var i in items) {
    var newI = items[i];
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
    if (newI.important != curI.important) {
      if (newI.important)
        $('#item_'+curI.id).addClass('important');
      else
        $('#item_'+curI.id).removeClass('important');
      updated.push('important');
    }
    if (newI.url != curI.url) {
      var link = $('#item_'+curI.id+'_link');
      link.attr('href', newI.url);
      if (newI.url == '')
        link.hide();
      else if (curI.url == '')
        link.show();
      updated.push('url');
    }
    if (newI.position != curI.position) {
      // Delay DOM update until all positions are updated
      itemsWhosePositionChanged.push(newI);
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
  for (var i in itemsWhosePositionChanged) {
    var item = itemsWhosePositionChanged[i];
    insertItemToDOM(item, $('#item_'+item.id).detach(), false);
  }
}

///////////// STATUSLIGHT RELATED STUFF /////////////

var pendingAjaxCalls = 0;
function setStatusLight() {
  if (pendingAjaxCalls > 0) {
    $('#status-light').attr('class', 'yellow');
    $('html').addClass('yellow-bg');
  } else {
    $('#status-light').attr('class', 'green');
    $('html').removeClass('yellow-bg');
  }
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
  $('html').effect('highlight', {color:'red'}, 3000);
  setTimeout('setStatusLight()', 10000);
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

$.ajaxSetup({timeout:10000});

// The text that appears in the new item boxes
var newitemText = "New item..."

// Refresh when state is this old (in seconds). Must be at least 3 seconds.
// Set to -1 to disable autorefresh.
var autorefresh_freq = 300;

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

function getCheckedItemIds() {
  var checked_items = [];
  $('.itemcheck:checked').each(function(){checked_items.push($(this).val())});
  return checked_items;
}
function getItem(item_id) {
  for (var i in state.subscriptions) {
    if (state.subscriptions[i].list.items[item_id] !== undefined)
      return state.subscriptions[i].list.items[item_id]
  }
  return null;
}
function updateNavbarItemactions() {
  if ($('.itemcheck:checked').length == 0)
    $('.topnav_itembutton').hide();
  else
    $('.topnav_itembutton').show();
  if ($('.itemcheck:checked').length == 1) {
    $('.topnav_linkbutton').show();
  } else {
    $('.topnav_linkbutton').hide();
    $('#url_input_container').hide();
  }
}
function initTopBar() {
  $("#refresh_button").click(function() {refresh(true);});
  $('#remove_button').click(function(e) {
    var checked_item_ids = getCheckedItemIds();
    if (checked_item_ids.length == 0)
      return;
    // Hide the removed items immediately - reshow them in case of ajax fail
    var items = $();
    for (var i in checked_item_ids)
      items = items.add('#item_'+checked_item_ids[i]);
    items.attr('checked', false).hide()
      .children('.itemcheck').attr('checked',false);
    $.ajax('remove_items/', {dataType:"json", type:"POST", traditional:true,
        data:{item_ids:checked_item_ids}})
      .done(function(data) {
          flashSuccess('items removed');
          updateNavbarItemactions();
          mergeState(data.state);
        })
      .fail(function(a,b,c) {
        items.show().children('.itemcheck').attr('checked', true);
        getAjaxFailHandler('remove item')(a,b,c);
      });
  });
  $('#important_button').click(function(e) {
    var checked_items = getCheckedItemIds();
    if (checked_items.length == 0)
      return;
    var important_items = [], unimportant_items = [];
    for (var i in checked_items) {
      var item = getItem(checked_items[i]);
      if (item.important)
        unimportant_items.push(checked_items[i]);
      else
        important_items.push(checked_items[i]);
      $('#item_'+checked_items[i]).toggleClass('important');
    }
    $.ajax('set_item_importances/', { dataType:"json", type:"POST",
        traditional:true, data:{important_item_ids:important_items,
                                unimportant_item_ids:unimportant_items}})
      .done(function(data) {
          flashSuccess('item importance(s) set');
          $('.itemcheck:checked').attr('checked', false);
          updateNavbarItemactions();
          mergeState(data.state);
      }).fail(function(a,b,c) {
        for (var i in checked_items)
          $('#item_'+checked_items[i]).toggleClass('important');
        getAjaxFailHandler('set item importances')(a,b,c);
      });
  });
  $('#link_button').click(function(e) {
    var checked_items = getCheckedItemIds();
    if (checked_items.length != 1)
      return;
    var item_id = checked_items[0];
    var item = getItem(item_id);
    $('#url_input_container').show();
    $('#url_input').val(item.url).focus();
  });
  function submitUrl() {
    var checked_items = getCheckedItemIds();
    if (checked_items.length != 1)
      return;
    var item_id = checked_items[0];
    var url = $('#url_input').val();
    if (url.length != 0 && !urlRegex.test(url)) {
      debug('Invalid url!');
      return;
    }

    $.ajax('set_item_url/', { dataType:"json", type:"POST",
        data:{item_id:item_id, url:url}})
      .done(function(data) {
          flashSuccess('item url set');
          $('.itemcheck:checked').attr('checked', false);
          updateNavbarItemactions();
          $('#url_input_container').hide();
          mergeState(data.state);
        })
      .fail(getAjaxFailHandler('set item url'));
  }
  $('#url_input').keydown(
    function(e) { if(e.keyCode == 13) submitUrl(); });
  $('#url_submit').click(function(e) { submitUrl(); });
  $("#arrows_button").click(function() {
    if (arrows_on) {
      $('.move_item, .move_subscription').fadeOut();
    } else {
      $('.move_item, .move_subscription').fadeIn();
    }
    arrows_on = !arrows_on;
    $("#actions_button .dropcontent").slideUp(500);
  });
  $(".dropdown").click(function(e) {
    $('.dropcontent',this).slideToggle();
    e.stopPropagation();
  });
  $(".dropcontent").click(function(e) { e.stopPropagation(); });
  $('#background-underlay').add('body')
    .click(function(e) {$('.dropcontent').slideUp(500);});
  $('#create_list_nameinput').keyup(function(e) {
    if(e.keyCode == 13) {
      var val = $(this).val();
      if (val.length == 0)
        return false;
      $.ajax('add_list/',
        { dataType: "json", type: "POST", data: {name:val, subscribe:true} }
      ).done(function(data) {
        flashSuccess('list '+val+' created');
        $('#create_list_nameinput').val('');
        mergeState(data.state);
      }).fail(getAjaxFailHandler('add list'));
    }
  });
}

function initSubscriptionDragAndDrop() {
  $('#listlist').sortable({
    distance:30,
    axis:'y',
    start: function(e, ui) {
      old_prev_sub = ui.item.prev('.subscription'); // For revert on AJAX fail
    },
    update: function(e, ui) {
      var prev = ui.item.prev();
      var where = null;
      if (prev.length == 0) {
        where = 0;
      } else {
        where = state.subscriptions[prev.data('id')].position;
        if (ui.position.top < ui.originalPosition.top)
          where++; //If moving up, position must be one greater than prev's
      }
      $.ajax('move_subscription/', {
        dataType:"json", type:"POST",
        data:{subscription_id:ui.item.data('id'), where:where}
      }).done(function(data) {
        flashSuccess('subscription moved (drag)');
        mergeState(data.state);
      }).fail(function(jqXHR, textStatus, errorThrown) {
          if (old_prev_sub.length == 0)
            $('#listlist').prepend(ui.item);
          else
            old_prev_sub.after(ui.item);
          getAjaxFailHandler('drag subscription')(jqXHR, textStatus, errorThrown);
        });
    }});
}

prevItems = null;
function setSuggestionBoxItems(items) {
  if (items == prevItems)
    return;
  var columnsInUse = (items.length+suggestionsPerCol-1)/suggestionsPerCol;
  var wordLimit = 50/columnsInUse;
  for (var i=0; i<nrOfSuggestions; i++) {
    var sug = $('#suggestion_'+i)
    if (i < items.length) {
      if (items[i].length > wordLimit) {
        var words = items[i].split(/ +/);
        var newWords = [];
        for (var j in words) {
          var word = words[j];
          if (word.length > wordLimit)
            newWords.push(word.substr(0,wordLimit-1)+'&hellip;');
          else
            newWords.push(word);
        }
        var label = newWords.join(' ');
        if (label.length > wordLimit*3)
          sug.html(label.substr(0,wordLimit*3-1)+'&hellip;');
        else
          sug.html(label);
      } else {
        sug.html(items[i]);
      }
      sug.attr('title', items[i]);
      sug.parent().removeClass('empty');
    } else {
      sug.html('');
      sug.parent().addClass('empty');
    }
  }
  prevItems = items;
}
function freqtreeGetItems(prefix) {
  prefix = $.trim(prefix.toLowerCase());
  function getItemsHelper(tree, i) {
    if (i == prefix.length)
      return tree.items.sort();
    if (tree[prefix[i]] == undefined)
      return [];
    else
      return getItemsHelper(tree[prefix[i]], i+1);
  }
  return getItemsHelper(freqtree, 0);
}
function showAndResetSuggestionBox() {
  $('#suggestion_box').show();
  setSuggestionBoxItems(freqtreeGetItems(''));
}
function initSuggestionBox(nrOfInitials) {
  function freqtreeInsert(tree, text, i) {
    if (tree.items.length < nrOfSuggestions)
      tree.items.push(text);
    if (i >= Math.min(text.length, nrOfInitials))
      return;
    var c = text[i];
    if (tree[c] == undefined)
      tree[c] = {items: []};
    freqtreeInsert(tree[c], text, i+1)
  }
  freqtree = {items: []};
  for (var i in frequents) {
    var text = frequents[i];
    freqtreeInsert(freqtree, text, 0);
  }
  $('.suggestion').click(function(e) {
    e.preventDefault();
    // Trigger enter press in field:
    var e2 = jQuery.Event("keyup");
    e2.keyCode = 13;
    if (e.ctrlKey)
      e2.ctrlKey = true;
    $('.additem').val($(this).attr('title')).trigger(e2);
  });
}

var urlRegex = /^([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i;

var initDone = false;
$(document).ready(function() {
  arrows_on = false;
  setTimeout(function(){initSuggestionBox(10);}, 1); //Init later
  initTopBar();
  setStatusLight();
  state = {subscriptions: {}};
  subOfList = {};
  mergeState(init_state);
  initSubscriptionDragAndDrop();
  refresher();
  initDone = true;
});
