+function ($) {
  "use strict";

  var ITEM_ON = "nav_active";

  var showTab = function(a) {
    var $a = $(a);
    if($a.hasClass(ITEM_ON)) return;
    var href = $a.attr("href");

    if(!/^#/.test(href)) return ;

    $a.parent().find("."+ITEM_ON).removeClass(ITEM_ON);
    $a.addClass(ITEM_ON);

    var bd = $a.parents(".container").find(".ys_tab");

    bd.find(".tab_active").removeClass("tab_active");

    $(href).addClass("tab_active");
  }

  $.showTab = showTab;

  $(document).on("click", ".ys_navbar_item, .weui-tabbar__item", function(e) {
    var $a = $(e.currentTarget);
    var href = $a.attr("href");
    if($a.hasClass(ITEM_ON)) return;
    if(!/^#/.test(href)) return;

    e.preventDefault();

    showTab($a);
  });

}($);