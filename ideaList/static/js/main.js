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
