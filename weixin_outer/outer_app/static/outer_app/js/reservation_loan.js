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

    //获取协议文本
    $.get('/static/outer_app/doc/protocol.txt', function(resp){
        //console.log(resp);
        $('#protocol').html('<pre>' + resp + '</pre>');
    });     
    $('.ys_agree_clause').on('click', function(){
        $('.ys_fixed_footer').addClass('clause_btn_visible');
    });
    $('.ys_fixed_footer').on('click', function(){
        $(this).removeClass('clause_btn_visible');
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
            url: url_pre + "/reservation/loan/submit/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType: 'json',
            success: function (resp) {
                //console.log(resp)
                if (resp.success) {
                    window.location.href = url_pre + '/staticfile/done/?from=reservation';
                } else {
                    reservation_flag = false;
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                reservation_flag = false;
                $.toptips('服务器错误');
            }
        });
    });
//此处做限制当输入的额度值大于某个值的时候进行清空。

});
