$(function () {

    $.get(url_pre + "/activity/check", {activity_id: get_url_args('activity_id')}, function (resp) {
        if(resp.msg) {
            console.log(resp.data);
            $('input[name="col1"]').val(resp.data.col1);
            $('input[name="col2"]').val(resp.data.col2);
            $('input[name="col3"]').val(resp.data.col3);
            $.alert(resp.msg);
        }
    });

    $('#form').form();
    let flag = false;
    $("#submit_btn").on("click", function () {
        let validateRes = false;
        let form = $('#form');
        form.validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;

        if(flag) return false;
        flag = true;
        $.toptips('申请正在提交，请稍候', 'success');
        let data = JSON.parse(form.serializeForm());
        data.activity_id = get_url_args('activity_id');
        $.ajax({
            url: url_pre + "/activity/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (resp) {
                //console.log(resp)
                if (resp.success) {
                    window.location.href = url_pre + '/staticfile/done/?from=activity';
                } else {
                    flag = false;
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                flag = false;
                $.toptips('服务器错误');
            }
        });
    });

});
