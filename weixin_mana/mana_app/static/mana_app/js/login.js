$(document).ready(function(){
    App.initHelpers('select2');
    $('body').keydown(function(){
        if(event.keyCode=="13"){
            $('#form_submit').click();
        }
    });

    $("#manager_account").change(function() {
        var manager_account = $(this).val();
        var input_dom = $(this)
        $.ajax({
            url: '/mana_app/login/is_manager_exist/',
            type: "POST",
            data: {
                'manager_account': manager_account,
                "csrfmiddlewaretoken": $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) {
                if (data.exist_flag) {
                    input_dom.parents('.form-group > div').removeClass("has-error");
                    input_dom.parents('.form-group').removeClass("has-error");
                    $("#manager_account-error").remove()
                } else {
                    //若第二次输错，移除第一次的错误
                    input_dom.parents('.form-group > div').removeClass("has-error");
                    input_dom.parents('.form-group').removeClass("has-error");
                    $("#manager_account-error").remove()

                    //报错
                    input_dom.parents('.form-group > div').addClass("has-error");
                    input_dom.parents('.form-group').addClass("has-error");
                    input_dom.attr("aria-describedby","manager_account-error")
                    $("#manager_div").append('<div id="manager_account-error" class="help-block text-right animated fadeInDown has-error">账号不存在</div>');
                }
            }
        });
    });

    $("#form_submit").click(function(){
        var manager_account = $("input[name='manager_account']").val();
        var password = $("input[name='password']").val();
        var input_dom = $("#password")
        $.ajax({
            url: '',
            type: "POST",
            data: {
                'manager_account': manager_account,
                'password': password,
                "csrfmiddlewaretoken": $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) {
                if (data.success) {
                     window.location.href = data.url
                } else {
                    //若第二次输错，移除第一次的错误
                    $("#password").parents('.form-group > div').removeClass("has-error");
                    $("#password").parents('.form-group').removeClass("has-error");
                    $("#password-error").remove()

                    //报错
                    $("#password").parents('.form-group > div').addClass("has-error");
                    $("#password").parents('.form-group').addClass("has-error");
                    $("#password").attr("aria-describedby","manager_account-error")
                    $("#password_div").append('<div id="password-error" class="help-block text-right animated fadeInDown has-error">密码不正确</div>');
                }
            }
        });
    });
});
