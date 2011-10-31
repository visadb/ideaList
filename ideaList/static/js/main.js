
var newitem_text = "New item..."

function debug(str) {
  $("#debug").append(str+"<br />");
}

$(document).ready(function() {
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
      debug("Enter!");
    }
  }).addClass("newitem_blur");
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
