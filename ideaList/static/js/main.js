var newitemText = "New item..."
var pendingAjaxCalls = 0;

var editableUrl = '/ideaList/edittext/';
var editableSettings = {
    tooltip: "Click to edit",
    style:   "inherit",
    id:      "element_id",
    name:    "text",
  };

function debug(str) {
  var item = $('<div>'+str+'<br /></div>');
  $("#debug").prepend(item);
  //item.delay(5000).hide(1000, function(){item.remove()});
}

function makeItem(itemdata) {
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
  var list_id = itemdata['list_id'];
  var pos = itemdata['position'];
  var curitems = $('#list_'+list_id+' > ul > li.item');
  var itemHtml = makeItem(itemdata)
  if(curitems.length == 0 || pos == 0) {
    $('#list_'+list_id+' > ul').prepend(itemHtml);
  } else {
    var lastitem = curitems.last();
    curitems.each(function(index) {
      if ($(this)[0] === lastitem[0]) {
        lastitem.after(itemHtml);
        return false;
      } else if ($(this).data()['position'] > pos) {
        elem.before(itemHtml);
        return false;
      }
    });
  }
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
      var res = /^add_to_(end|begin)_of_(\d+)$/.exec($(this).attr('id'));
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
        // Will receive an array containing the item.
        addItem(data)
        addfield.val("").blur(); // Reset additem field
      }).fail(function(jqXHR, textStatus) {
        debug("Error in add item: "+textStatus);
      });
    }
  }).addClass("newitem_blur");
}
function makeAddItemField(list_id, pos) {
  if (pos == null)
    pos = 'end';
  var addItemHtml = $('<input id="add_to_'+pos+'_of_'+list_id+'"'
    +' class="newitem" type="text" value="'+newitemText+'"></input>');
  initAddItemField(addItemHtml);
  return addItemHtml;
}

function makeList(subscriptiondata) {
  var l = subscriptiondata['list'];
  var listHtml = $('<li id="list_'+l['id']+'" class="list">'+l['name']+'</li>\n')
    .data(subscriptiondata);
  var itemListHtml = $('<ul class="itemlist"></ul>\n');
  for (var i in l['items']) {
    var itemHtml = makeItem(l['items'][i]);
    itemListHtml.append(itemHtml);
  }
  itemListHtml.append($('<li></li>').append(makeAddItemField(l['id'], 'end')));
  listHtml.append(itemListHtml);
  return listHtml;
}

function addSubscription(subscriptiondata) {
  var listHtml = makeList(subscriptiondata);
  $('#listlist').append(listHtml);
}


function removeitemHandler(e) {
  e.preventDefault();
  var item_elem = $(this).parent();
  var res = /^remove_item_(\d+)$/.exec($(this).attr('id'));
  if (res.length != 2)
    return false;
  var item_id = res[1];
  //debug("Item "+item_id+" removed");
  $.ajax('/ideaList/removeitem/', {
    dataType: "text",
    type: "POST",
    data: {item_id:item_id},
  }).done(function() {
    item_elem.remove()
  }).fail(function(jqXHR, textStatus) {
    if (jqXHR.status == 404) {
      debug("Item "+item_id+" has disappeared.");
      item_elem.remove();
      return;
    }
    debug("Error in remove item: "+textStatus);
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
    item_before = item_elem.next().next();
  if (item_before.length != 1)
    return false;
  $.ajax('/ideaList/moveitem/', {
    dataType: "text",
    type: "POST",
    data: {
      item_id:item_id,
      where:direction,
    },
  }).done(function() {
    item_before.before(item_elem.detach());
  }).fail(function(jqXHR, textStatus) {
    if (jqXHR.status == 404) {
      // There was no such item: make it disappear
      debug("Item "+item_id+" has disappeared.");
      item_elem.remove();
      return;
    }
    debug("Error in remove item: "+textStatus);
  });
}

function handlePatch(patch) {
  for (inst in patch) {
    if (inst['content_type'] == 'item') {
      switch (inst['action']) {
      case 'add':
        break;
      case 'update':
        break;
      case 'remove':
        break;
      default:
        debug("handlePatch: Uknown action in inst "+inst)
      }
    } else if (inst['content_type'] == 'subscription') {
      switch (inst['action']) {
      case 'add':
        break;
      case 'update':
        break;
      case 'remove':
        break;
      default:
        debug("handlePatch: Uknown action in inst "+inst)
      }
    }
    else {
      debug("handlePatch: Uknown content_type in inst "+inst)
    }
  }
}


$(document).ready(function() {
  setStatusLight();
  for (i in init_subscriptions) {
    addSubscription(init_subscriptions[i]);
  }
});

// TODO: Send current timestamp and ask for instructions to update state

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
