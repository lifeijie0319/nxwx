//toptips
+function ($) {
    "use strict";
    var timeout;
    $.toptips = function (text, duration, type) {
        if (!text) return;
        if (typeof duration === typeof "a") {
            type = duration;
            duration = undefined;
        }
        var duration = duration || 2000;
        var className = type ? 'bgcolor_' + type : 'bgcolor_danger';
        var $t = $('.ys_toptips').remove();
        $t = $('<div class="ys_toptips"></div>').appendTo(document.body);
        $t.html(text);
        $t[0].className = 'ys_toptips ' + className
        clearTimeout(timeout);
        if (!$t.hasClass('ys_toptips_visible')) {
            $t.show().width();
            $t.addClass('ys_toptips_visible');
        }
        timeout = setTimeout(function () {
            $t.removeClass('ys_toptips_visible');
            setTimeout(function () {
                $t.remove();
            }, 300);
        }, duration);
    }
}($);
//from validate
(function ($) {
    $.cell_validate = _validate;

    function _validate($input) {
        //console.log($input);
        var input = $input[0],
            val = $input.val();
        if (!input.getAttribute("emptyTips") && !$input.val().length) {
            return null;
        }
        //console.log('val', val);
        if (input.tagName == "INPUT" || input.tagName == "TEXTAREA") {
            var reg = input.getAttribute("required") || input.getAttribute("pattern") || "";
            if (input.getAttribute("type") == "checkbox" || input.getAttribute("type") == "radio") {
                return input.checked ? null : "empty";
            } else if (!$input.val().length) {
                return "empty";
            } else if (input.getAttribute('type') == 'date') {
                min_date = input.getAttribute('min');
                max_date = input.getAttribute('max');
                if (min_date && max_date) {
                    return val >= min_date && val <= max_date ? null : 'beyond';
                } else if (min_date) {
                    return val >= min_date ? null : 'beyond';
                } else if (max_date) {
                    return val <= max_date ? null : 'beyond';
                } else {
                    return null;
                }
            } else if (reg) {
                return new RegExp(reg).test(val) ? null : "notMatch";
            } else {
                return null;
            }
        } else if (val.length) {
            return null;
        } else {
            return "empty";
        }
    }

    function _showErrorMsg(error) {
        if (error) {
            var $dom = error.$dom,
                msg = error.msg,
                tips = $dom.attr(msg + "Tips") || $dom.attr("tips") || $dom.attr("placeholder");
            if (tips) $.toptips(tips);
            $dom.parents(".ys_cell").addClass("color_danger");
            $dom.parents(".form-material").addClass("color_danger");
        }
    }

    var oldFnForm = $.fn.form;
    $.fn.form = function () {
        return this.each(function (index, ele) {
            var $form = $(ele);
            //console.log($form.find("[required]").attr('placeholder'))
            $form.find("[required]").on("blur", function () {
                var $this = $(this),
                    errorMsg;
                if ($this.val().length < 1) return;
                errorMsg = _validate($this);
                if (errorMsg) {
                    _showErrorMsg({
                        $dom: $this,
                        msg: errorMsg
                    });
                }
            }).on("focus", function () {
                var $this = $(this);
                $this.parents(".ys_cell").removeClass("color_danger");
                $this.parents(".form-material").removeClass("color_danger");
            });
        });
    };
    $.fn.form.noConflict = function () {
        return oldFnForm;
    };
    var oldFnValidate = $.fn.validate;
    $.fn.validate = function (callback) {
        return this.each(function () {
            var $requireds = $(this).find("[required]");
            if (typeof callback != "function") callback = _showErrorMsg;
            for (var i = 0, len = $requireds.length; i < len; ++i) {
                var $dom = $requireds.eq(i),
                    errorMsg = _validate($dom),
                    error = {
                        $dom: $dom,
                        msg: errorMsg
                    };
                console.log(errorMsg);
                if (errorMsg) {
                    //if (!callback(error)) _showErrorMsg(error);
                    //return;
                    if (!callback(error)) {
                        _showErrorMsg(error);
                        return;
                    } else {
                        continue;
                    }
                }
            }
            callback(null);
        });
    };
    $.fn.validate.noConflict = function () {
        return oldFnValidate;
    };
})($);
//serialize form
+ function($) {
    $.fn.serializeForm= function(){
        var o = {};
        var a = this.serializeArray();
        //console.log(a);
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return JSON.stringify(o);
    }
}($);
