
var newitem_text = "New item..."

function debug(str) {
  $("#debug").append(str+"<br />");
}

function init_additem_fields() {
  $(".newitem").blur(function() {
    if($(this).val() == "") {
      $(this).val(newitem_text)
        .addClass("newitem_blur");
    }
  }).focus(function() {
    $(this).removeClass("newitem_blur");
    if($(this).val() == newitem_text)
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
        var item = data[0];
        var list_id = item['fields']['list'];
        var text = item['fields']['text'];
        var pos = item['fields']['position'];
        var curitems = $('#list_'+list_id+' > ul > li.item');
        var newhtml = '<li id="item_'+item['pk']+'" class="item">'+text
          +' <a id="remove_item_'+item['pk']+'" class="removeitem"'
          +' href="#">del</a></li>';
        //debug("Success: "+list_id+" "+text+" "+pos);
        if(curitems.length == 0 || pos == 0) {
          $('#list_'+list_id+' > ul').prepend(newhtml);
        } else {
          curitems.filter(':eq('+(pos-1)+')').after(newhtml);
        }
        $('#remove_item_'+item['pk']).click(removeitem_handler);
        addfield.val("").blur(); // Reset additem field
      }).fail(function(jqXHR, textStatus) {
        debug("Error in add item: "+textStatus);
      });
    }
  }).filter('[value="'+newitem_text+'"]').addClass("newitem_blur");
}

function removeitem_handler(e) {
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
      // There was no such item: make it disappear
      item_elem.remove()
      return;
    }
    debug("Error in remove item: "+textStatus);
  });
}

function init_removeitem_links() {
  $('.removeitem').click(removeitem_handler);
}

$(document).ready(function() {
  init_additem_fields();
  init_removeitem_links();
});

// TODO: maintain ideaList state on client-side and update by polling/push
// TODO: Design an object that holds the whole state
// Send current state and ask for instructions to update it

$.ajaxSetup({timeout:3000});

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
