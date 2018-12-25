var url_pre = '/mana_app'

function toptips(msg, type){
    $.notify({
        icon: '',
        message: msg,
        url: '',
    },
    {
        element: 'body',
        type: type,
        allow_dismiss: true,
        newest_on_top: true,
        showProgressbar: false,
        placement: {
            from: 'top',
            align: 'center',
        },
        offset: 20,
        spacing: 10,
        z_index: 1033,
        delay: 1000,
        timer: 100,
        animate: {
            enter: 'animated fadeIn',
            exit: 'animated fadeOutDown'
        }
    });
}

$.extend($.validator.messages, {  
    required: "这是必填字段",  
    remote: "请修正此字段",  
    email: "请输入有效的电子邮件地址",  
    url: "请输入有效的网址",  
    date: "请输入有效的日期",  
    dateISO: "请输入有效的日期 (YYYY-MM-DD)",  
    number: "请输入有效的数字",  
    digits: "只能输入数字",  
    creditcard: "请输入有效的信用卡号码",  
    equalTo: "你的输入不相同",  
    extension: "请输入有效的后缀",  
    maxlength: $.validator.format("最多可以输入 {0} 个字符"),  
    minlength: $.validator.format("最少要输入 {0} 个字符"),  
    rangelength: $.validator.format("请输入长度在 {0} 到 {1} 之间的字符串"),  
    range: $.validator.format("请输入范围在 {0} 到 {1} 之间的数值"),  
    max: $.validator.format("请输入不大于 {0} 的数值"),  
    min: $.validator.format("请输入不小于 {0} 的数值")  
});
function initValidate(form, rules={}, messages={}){
    validator = form.validate({
        ignore: [],
        errorClass: 'help-block animated fadeInDown',
        errorElement: 'div',
        errorPlacement: function(error, e) {
            jQuery(e).parents('.form-group > div').append(error);
        },
        highlight: function(e) {
            var elem = jQuery(e);
            elem.closest('.form-group').addClass('has-error');
        },
        success: function(e) {
            var elem = jQuery(e);
            elem.closest('.form-group').removeClass('has-error');
            elem.closest('.help-block').remove();
        },
        rules: rules,
        messages: messages,
    });
    return validator;
}

//serialize form
+ function($) {
    $.fn.serializeForm = function(){
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
        //console.log(o);
        return o;//JSON.stringify(o);
    }
}($);

//菜单自动展开
$(function(){
    //console.log(window.location.pathname.indexOf('index') != -1);
    if(window.location.pathname.indexOf('index') == -1){
        active_menu_id = localStorage.getItem('active_menu_id');
        active_menu_dom = $('a.frame-link[menu_id="' + active_menu_id + '"]').addClass('active');
        menu_level2_dom = active_menu_dom.parents('li[menu_level="2"]').addClass('open');
        $('h1.page-heading').text(menu_level2_dom.children('a.nav-submenu').text());
        $('h3.block-title').text(active_menu_dom.text());
    }
    $("a.frame-link").on('click',function(e){
        localStorage['active_menu_id'] = $(this).attr('menu_id');
    });
});

function toQueryString(obj) {
    var ret = [];
    for(var key in obj){
        var value = obj[key];
        if(value){
            ret.push(key + '=' + value)
        }
    }
    return '?' + ret.join('&');
}

function getCurrentDate(){
    var now = new Date();
    var year = now.getFullYear();       //年
    var month = now.getMonth() + 1;     //月
    var day = now.getDate();            //日
    var cur_date = year + '-'
    if(month < 10) cur_date += '0';
    cur_date += month + '-';
    if(day < 10) cur_date += '0';
    cur_date += day
    return cur_date
}

function changePage(action){
    current_page = parseInt($('ul.pager li[name="current_page"]').text().replace(/\D/g, ''));
    total_page = parseInt($('ul.pager li[name="total_page"]').text().replace(/\D/g, ''));
    switch(action){
        case 'prev':
            page = current_page - 1;
            break;
        case 'next':
            page = current_page + 1;
            break;
        case 'last':
            page = total_page;
            break;
        default:
            page = 1;
    }
    return page;
}

function singleSelection(model_name, update_btn, element_name){
    element_value = update_btn.parents('tr').find('td[field="' + element_name + '"]').text();
    $('#' + model_name).find('select[name="' + element_name + '"] > option').each(function(idx, ele){
        if($(ele).text() == element_value){
            $(ele).prop('selected', true);
        }
    });
}
