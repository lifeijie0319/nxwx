$(function() {
    $('#shop_form').hide();
    $('#query_form').form();
    $('#query_btn').on('click', function(){
        validateRes = false;
        $('#query_form').validate(function(error){
            if(error){
                dom_name = error.$dom.attr('name');
                console.log(dom_name, ($.inArray(dom_name, ['bankcard_no', 'telephone_no'])), error.msg);
                if($.inArray(dom_name, ['bankcard_no', 'telephone_no']) != -1 && error.msg == 'empty') return true;
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return;
        $.ajax({
            url : url_pre + "/shop/seller_replace_query/",
            type : 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#query_form').serializeForm(),
            dataType : 'json',
            success : function(resp) { 
                console.log(resp)
                if(resp.success){
                    $.toptips('查询成功', 'success');
                    $('#shop_form').show().form();
                    $('input[name="shop_name"]').val(resp.shop.name);
                    $('input[name="seller_name"]').val(resp.shop.seller_name);
                    $('input[name="seller_telno"]').val(resp.shop.seller_telno);
                }else{
                    $.toptips(resp.msg);
                }
            },
            error : function(){
                $.toptips('error')
            }
        });
    });

    //初始化表单
    $('#telno_modify_form').form();
    $('a.open-popup').on('click', function(){
        $('#telno_modify_form')[0].reset();
    });
    //发送验证码函数绑定
    $('#send_vcode').on('click', function () {
        send_vcode($(this), $('input[name="new_telno"]'));
    });
    $('#telno_modify_submit').on('click', function(){
        validateRes = false;
        $('#telno_modify_form').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;
        $.toptips('正在验证，请稍后', 'success');
        data = JSON.stringify({
            'vcode': $('input[name="vcode"]').val(),
        });
        $.post(url_pre + '/common/check_vcode/', data, function(resp){
            if(resp.success){
                $.toptips('手机号验证通过', 'success');
                $.closePopup();
                $('input[name="new_telno_show"]').val($('input[name="new_telno"]').val());
                $('#new_telno_div').show();
            }else{
                $.toptips('验证码错误');
            }
        }).error(function(){
            console.log('服务器错误')
        });
    });

    var rebind_flag = false;
    $('#rebind_btn').on('click', function(){
        validateRes = false;
        $('#shop_form').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return;
        data = {
            shop_name: $('input[name="shop_name"]').val(),
            new_telno_show: $('input[name="new_telno_show"]').val(),
        }
        console.log(data);
        if(rebind_flag) return false;
        rebind_flag = true;
        $.post(url_pre + '/shop/seller_replace_apply/', data, function(resp){
            console.log(resp);
            rebind_flag = false;
            if(resp.success){
                $.toptips('申请提交成功', 'success');
                window.location.href = url_pre + '/staticfile/done/?from=seller_replace_auditing';
            }else{
                $.toptips(resp.msg);
            }
        }).error(function(){
            console.log('服务器错误');
        });
    });
});
