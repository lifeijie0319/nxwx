$(function() {
    $('#form').form();
    $('#send_vcode').on('click', function(){
        send_vcode($(this), $('input[name="telephone_no"]'));
    });
    $('#submit').on('click', function(){
        validateRes = false;
        $('#form').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return;
        $.ajax({
            url : url_pre + "/seller/account_modify/",
            type : 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType : 'json',
            success : function(resp) { 
                //console.log(resp)
                if(resp.success){
                    $.toptips('验证通过', 'success');
                    //window.location.href = '/shop/page/';
                    //localStorage['refresh'] = 'true';
                    window.history.go(-1);
                }else{
                    $.toptips(resp.msg);
                    if(resp.msg == '验证码不匹配'){
                        $('input[name="vcode"]').parents('.ys_cell').addClass("color_danger");
                    }
                }
            },
            error : function(){
                $.toptips('error')
            }
        });
    });
});

