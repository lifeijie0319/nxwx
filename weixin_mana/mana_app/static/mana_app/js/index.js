$(function () {
    var validator = initValidate(
        $('#passwd_change_form'),
        {
            'base_old_passwd': {
                required: true,
                rangelength: [6,8],
            },
            'base_new_passwd': {
                required: true,
                rangelength: [6,8],
            },
            'base_new_passwd_confirm': {
                required: true,
                rangelength: [6,8],
                equalTo: '#base_new_passwd',
            },
        },
    );
    //密码修改
    $("#pw_change_button").click(function () {
        if(!$('#passwd_change_form').valid()) return false;
        $.ajax({
            type:'post',
            async : true,
            url : '/mana_app/password_change/',
            dataType : 'json',
            data : $('#passwd_change_form').serialize(),
            success : function(resp){
               if(resp.success){
                   swal('', resp.msg, 'success');
                   $("#PW_Change").modal("hide")
               }else{
                   swal('', resp.msg, 'error');
               }
            },
            error:function(error_msg){
                swal('', "服务器错误!", 'error');
            }
        });
    });
    $("#PW_Change_modal").click(function () {
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#passwd_change_form')[0].reset();
        $("#PW_Change").modal("show")
    });
});
