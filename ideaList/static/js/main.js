
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
      if (val.length == 0)
        return true;
      res = /^add_to_(end|begin)_of_(\d+)$/.exec($(this).attr('id'))
      if (res.length != 3)
        return true;
      pos = res[1];
      list_id = res[2];
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
        var newhtml = '<li id="item_'+item['pk']+'" class="item">'+text+'</li>';
        //debug("Success: "+list_id+" "+text+" "+pos);
        if(curitems.length == 0 || pos == 0) {
          $('#list_'+list_id).prepend(newhtml);
        } else {
          curitems.filter(':eq('+(pos-1)+')').after(newhtml);
        }
        // TODO: Reset input box
      }).fail(function(jqXHR, textStatus) {
          debug("Error: "+textStatus);
      });
    }
  }).filter('[value="'+newitem_text+'"]').addClass("newitem_blur");
}
function init_removeitem_links() {
  $('.removeitem').click(function(e) {
    e.preventDefault();
    debug("Item "+$(this).attr('id')+" removed");
  });
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
