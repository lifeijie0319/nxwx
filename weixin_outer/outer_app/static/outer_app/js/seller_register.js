$(function() {
    $('#form').form();

    $('#send_vcode').on('click', function(){
        send_vcode($(this), $('input[name="telephone_no"]'));
    });

    var seller_register_flag = false;
    $('#submit').on('click', function(){
        $('input[name="teller_no"]').removeAttr('required');
        validateRes = false;
        $('#form').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return;
        if(seller_register_flag) return false;
        seller_register_flag = true;
        $.ajax({
            url : url_pre + "/register/seller/",
            type : 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType : 'json',
            success : function(resp){
                seller_register_flag = false;
                //console.log(resp)
                if(resp.success){
                    $.toptips('验证通过', 'success');
                    window.location.href = url_pre + '/register/shop/page/';
                }else{
                    $.toptips(resp.msg);
                    //if(resp.msg == '验证码不匹配'){
                    //    $('input[name="vcode"]').parents('.ys_cell').addClass("color_danger");
                    //}
                }
            },
            error : function(){
                $.toptips('error');
            }
        });
    });
});

