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
  var removeHtml = $('<a id="remove_item_'+item_id+'" class="itemaction removeitem" href="#">&#10005;</a>').click(removeitemHandler);
  var moveUpHtml = $('<a id="move_item_'+item_id+'_up" class="itemaction moveitem" href="#">&uarr;</a>').click(moveitemHandler);
  var moveDownHtml = $('<a id="move_item_'+item_id+'_down" class="itemaction moveitem" href="#">&darr;</a>').click(moveitemHandler);
  var itemHtml = $('<li id="item_'+item_id+'" class="item">'+text+'</li>')
    .data('itemdata', itemdata);
  itemHtml
    .append('&nbsp;').append(removeHtml)
    .append('&nbsp;').append(moveUpHtml)
    .append('&nbsp;').append(moveDownHtml);
  return itemHtml;
}

//TODO: function addSubscription(subscriptiondata)

function addItem(itemdata) {
  var list_id = itemdata['list_id'];
  var pos = itemdata['position'];
  var curitems = $('#list_'+list_id+' > ul > li.item');
  var newhtml = makeItem(itemdata)
  // TODO: Remove true once we have proper dynamic loading of content
  if(true || curitems.length == 0 || pos == 0) {
    $('#list_'+list_id+' > ul').prepend(newhtml);
  } else {
    curitems.each(function(index, elem) {
      // if elem's position smaller than pos, insert before elem
    });
    // curitems.filter(':eq('+(pos-1)+')').after(newhtml);
  }
}

function initAdditemFields() {
  $(".newitem").blur(function() {
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
  }).filter('[value="'+newitemText+'"]').addClass("newitem_blur");
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



$(document).ready(function() {
  setStatusLight();
  initAdditemFields();
  $('.removeitem').click(removeitemHandler);
  $('.moveitem').click(moveitemHandler);
  $('.item-text').editable(editableUrl, editableSettings);
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
