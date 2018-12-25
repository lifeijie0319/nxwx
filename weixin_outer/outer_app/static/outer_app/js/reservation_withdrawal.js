$(function () {

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

    $('#form').form();
    var reservation_flag = false;
    $("#submit_btn").on("click", function () {
        validateRes = false;
        $('#form').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;

        branch_id = $('select[name="branch"]').val();
        if(branch_id == '0'){
            $.toptips('网点不能为空');
            return false;
        }

        if(reservation_flag) return false;
        reservation_flag = true;
        $.toptips('申请正在提交，请稍候', 'success');
        $.ajax({
            url: url_pre + "/reservation/withdrawal/submit/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType: 'json',
            success: function(resp){
                //console.log(resp)
                if(resp.success){
                    window.location.href = url_pre + '/staticfile/done/?from=reservation';
                }else{
                    reservation_flag = false;
                    $.toptips(resp.msg);
                }
            },
            error: function(){
                reservation_flag = false;
                $.toptips('服务器错误');
            }
        });
    });

});
