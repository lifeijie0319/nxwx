$(function () {
    branches = new Array();
    $.get(url_pre + '/online/num/taking/waitman/', function(resp){
        branches = resp.banks;
        $('select[name="branch"]').html('<option value=""></option>');
        branch_id = parseInt(get_url_args('branch_id'))
        $.each(branches, function(index, value){
            branch = '<option value="' + value.id + '">' + value.name + '</option>';
            $('select[name="branch"]').append(branch);
            //console.log(typeof branch_id, typeof value.id);
            if(branch_id == value.id){
                $('select[name="branch"]').val(branch_id);
                $('#list_count').text(value.waitman);
            }
        });
        console.log(resp);
    }).error(function(){
        $.toptips('服务器错误');
    });
    $('select[name="branch"]').on('change', function(){
        branch_id = $(this).val();
        var branch;
        $.each(branches, function(index, value){
            if(value.id == branch_id){
                branch = value;
                return false;
            }
        });
        $('#list_count').text(branch.waitman);
    });

    var subimit_flag = false;
    $('#submit_btn').on('click', function(){
        branch_id = $('branches').val();
        if(branch_id == '0'){
            $.toptips('网点不能为空');
            return false;
        }
        if(subimit_flag) return false;
        subimit_flag = true;
        $.toptips('正在取号，请稍候', 'success');
        $.ajax({
            url: url_pre + "/online/num/taking/submit/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType: 'json',
            success: function(resp){
                //console.log(resp)
                if(resp.success){
                    window.location.href = url_pre + '/staticfile/done/?from=online_num_taking';
                }else{
                    $.toptips(resp.msg);
                    subimit_flag = false;
                }
            },
            error: function () {
                $.toptips('服务器错误');
                subimit_flag = false;
            }
        });
    });

});
