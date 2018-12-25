$(function () {

    if(localStorage.getItem('refresh') == 'true'){
        //console.log(e.peristed);
        localStorage['refresh'] = 'false';
        $.toptips('注册完成，正在跳转...', 'success');
        //alert(localStorage.getItem('refresh'));
        setTimeout(function(){
            window.location.reload();
        }, 1000);
    }

    /*获取协议文本
    $.get(url_pre + '/register/protocol/', function(resp){
        //console.log(resp.protocol);
        $('#protocol').html('<pre>' + resp.protocol + '</pre>');
    });
    $('.ys_agree_clause').on('click', function(){
        $('.ys_fixed_footer').addClass('clause_btn_visible');
    });
    $('.ys_fixed_footer').on('click', function(){
        $(this).removeClass('clause_btn_visible');
    });*/
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

    //初始化表单
    $('#form').form();
    //发送验证码函数绑定
    $('#send_vcode').on('click', function () {
        send_vcode($(this), $('input[name="user_tel"]'));
    });

    //下一步
    $('#submit').on('click', function () {
        validateRes = false;
        $('#form').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;
        user_name = $('input[name="user_name"]').val();
        user_id = $('input[name="user_id"]').val();
        user_tel = $('input[name="user_tel"]').val();
        user_vcode = $('input[name="user_vcode"]').val();
        $.toptips('正在注册，请稍候...', 'success');
        $.ajax({
            url: url_pre + "/register/user/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'user_name': user_name,
                'user_id': user_id,
                'user_tel': user_tel,
                'new_cus': 'no',
                'update_flag': 'no',
                'user_vcode': user_vcode,
            }),
            dataType: 'json',
            success: function (resp) {
                console.log(resp)
                if (resp.success) {
                    window.location.href = url_pre + '/staticfile/done/?from=register&isNew=false';
                } else if(resp.msg == '用户不存在'){
                    register_as_new(user_name, user_id, user_tel, user_vcode);
                }else if(resp.msg == '身份证号已存在'){
                    user_update(user_name, user_id, user_tel, user_vcode);
                }else if(resp.msg.length > 10){
                    $.alert(resp.msg);
                }else{
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                $.toptips('服务器错误')
            }
        });
    });
});

function register_as_new(user_name, user_id, user_tel, user_vcode){
    $.confirm('<div class="info_check">\
        您当前注册的证件号码未在我行办理业务。请核对您的信息：<br><br>\
        用户名：' + user_name + '<br>\
        身份证号码：' + user_id + '<br>\
        手机号码：' + user_tel + '<br>\
        如信息无误，请点击确定按钮以新客户身份进行注册。<br>\
        如需更改，请点击取消按钮进行信息编辑。</div>',
        '新客户注册确认',
        function(){
            $.ajax({
                url: url_pre + "/register/user/",
                type: 'post',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    'user_name': user_name,
                    'user_id': user_id,
                    'user_tel': user_tel,
                    'new_cus': 'yes',
                    'update_flag': 'no',
                    'user_vcode': user_vcode,
                }),
                dataType: 'json',
                success: function (resp) {
                    console.log(resp)
                    if (resp.success) {
                        window.location.href = url_pre + '/staticfile/done/?from=register&isNew=true';
                    }else if(resp.msg.length > 10){
                        $.alert(resp.msg);
                    }else{
                        $.toptips(resp.msg);
                    }
                },
                error: function(){
                    $.toptips('服务器错误');
                },
            });
        },
        function(){}
    );
}


function user_update(user_name, user_id, user_tel, user_vcode){
    $.confirm('您的身份证号已存在，微银系统只能绑定一个身份证号，是否更新相关信息？',
        '微信号更换确认',
        function(){
            $.ajax({
                url: url_pre + "/register/user/",
                type: 'post',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    'user_name': user_name,
                    'user_id': user_id,
                    'user_tel': user_tel,
                    'new_cus': 'no',
                    'update_flag': 'yes',
                    'user_vcode': user_vcode,
                }),
                dataType: 'json',
                success: function (resp) {
                    console.log(resp)
                    if (resp.success) {
                        window.location.href = url_pre + '/staticfile/done/?from=register&isNew=false';
                    }else if(resp.msg.length > 10){
                        $.alert(resp.msg);
                    }else{
                        $.toptips(resp.msg);
                    }
                },
                error: function(){
                    $.toptips('error');
                },
            });
        },
        function(){}
    );
}
