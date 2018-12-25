$(function(){
    $('form').form();

    $('#submit').on('click', function(){
        validateRes = false;
        $('form').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;
        old_password = $('input[name="old_password"]').val();
        new_password = $('input[name="new_password"]').val();
        new_password_reply = $('input[name="new_password_reply"]').val();
        if(new_password == old_password){
            $.toptips('您的新密码与旧密码一致');
            return false;
        }
        if(new_password != new_password_reply){
            $.toptips('您第二次输入的密码与第一次输入的不符!');
            return false;
        }
        $.toptips('设置密码进行中...', 'success');
        $.post(url_pre + '/user/modify/payment_password/', {old_password: old_password, new_password: new_password}, function(resp){
            if(resp.success){
                $.toptips('设置密码成功，正在跳转...', 'success');
                setTimeout(function(){
                    window.history.go(-1);
                }, 1000);
            }else{
                $.toptips('原密码输入错误');
            }
        });
    });

});
