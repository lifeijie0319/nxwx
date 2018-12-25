$(function () {
    //输入框悬浮效果
    $('.form-material.floating > .form-control').each(function () {
        var $input = jQuery(this);
        var $parent = $input.parent('.form-material');
        if ($input.val()) {
            $parent.addClass('open');
        }
        $input.on('change', function () {
            if ($input.val()) {
                $parent.addClass('open');
            } else {
                $parent.removeClass('open');
            }
        });
    });

    $('#binding_form input').addClass('color_disabled').prop('disabled', true);
    $('a.modify').on('click', function(){
        if($(this).hasClass('open-popup')) return;
        if($(this).text() == '修改'){
            console.log($(this).siblings('input'));
            $(this).text('保存');
            $(this).siblings('input').removeClass('color_disabled').prop('disabled', false);
        }else{
            $(this).text('修改');
            $(this).siblings('input').addClass('color_disabled').prop('disabled', true);
        }
    });

    if(localStorage.getItem('refresh') == 'true'){
        //console.log(e.peristed);
        localStorage['refresh'] = 'false';
        $.toptips('绑定完成，正在跳转...', 'success');
        //alert(localStorage.getItem('refresh'));
        setTimeout(function(){
            window.location.reload();
        }, 1000);
    }

    //初始化表单
    $('#telno_modify_form').form();
    //发送验证码函数绑定
    $('#send_vcode').on('click', function () {
        send_vcode($(this), $('input[name="telephone_no"]'));
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
                $('#user_tel').val($('input[name="telephone_no"]').val());
            }else{
                $.toptips('验证码错误');
            }
        }).error(function(){
            console.log('服务器错误')
        });
    });

    //下一步
    var bind_flag = false;
    $('#binding').on('click', function () {
        if(bind_flag) return false;
        bind_flag = true;
        user_name = $('input[name="user_name"]').val();
        user_id = $('input[name="user_id"]').val();
        user_tel = $('input[name="user_tel"]').val();
        $.toptips('正在绑定，请稍候...', 'success');
        $.ajax({
            url: url_pre + "/user/binding/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'user_name': user_name,
                'user_id': user_id,
                'user_tel': user_tel,
                'update_flag': 'no',
            }),
            dataType: 'json',
            success: function (resp) {
                bind_flag = false;
                console.log(resp)
                if (resp.success) {
                    $.toptips('绑定成功，正在跳转', 'success');
                    next = get_url_args('next');
                    if(next){
                        window.location.href = next;
                    }else{
                        window.location.href = url_pre + '/user/info/page/';
                    }
                }else if(resp.msg.length > 10){
                    $.alert(resp.msg);
                }else{
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                $.toptips('error');
            }
        });
    });
});
