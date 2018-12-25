$(function () {

    function addParam(data) {
        $.post('/mana_app/param/add/', data, function(resp){
            if(resp.success){
                $('#param_modal').modal('hide');
                refreshParam(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_param_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#param_modal_form')[0].reset();

        $('#param_modal textarea[name="remark"]').attr('readonly', false);
        $('#param_modal input[name="name"]').attr('readonly', false);
        $('#param_modal').find('.modal-title').text('新增参数');
        $('#param_modal_submit').off('click').on('click', function(){
            if(!$('#param_modal_form').valid()) return false;
            data = $('#param_modal_form').serializeForm();
            addParam(JSON.stringify(data));
        });
    });

    function delParam(param_id){
        swal({
            title: "删除确认",
            text: "确定删除该参数？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'param_id': param_id,
            });
            $.post('/mana_app/param/delete/', data, function(resp){
                if(resp.success){
                    refreshParam(resp.html);
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }
    $('input[name="delete_param"]').on('click', function(){
        param_id = $(this).parents('tr').attr('param_id');
        console.log(param_id);
        delParam(param_id);
    });

    function updateParam(data){
        $.post('/mana_app/param/update/', data, function(resp){
            if(resp.success){
                $('#param_modal').modal('hide');
                refreshParam(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function initUpdateParam(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#param_modal_form')[0].reset();

        var update_btn = $(this);
        var param_id = $(this).parents('tr').attr('param_id');

        $('#param_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        var remark = update_btn.parents('tr').find('td[field="remark"]').text()
        $('#param_modal textarea[name="remark"]').val(remark).attr('readonly', true);

        $('#param_modal input[name="name"]').attr('readonly', true);

        $('#param_modal').find('.modal-title').text('更新参数');
        $('#param_modal_submit').off('click').on('click', function(){
            if(!$('#param_modal_form').valid()) return false;
            data = $('#param_modal_form').serializeForm();
            data['param_id'] = param_id;
            updateParam(JSON.stringify(data));
        });
        $('#param_modal').modal('show');
    }
    $('input[name="update_param"]').on('click', initUpdateParam);

    function queryParam(param_name){
        data = {
            'param_name': param_name,
        }
        $.get('/mana_app/param/query/', data, function(resp){
            if(resp.success){
                refreshParam(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_param_btn').on('click', function(){
        param_name = $('input[name="query_param_name"]').val();
        queryParam(param_name);
    });

    function refreshParam(html){
        $('tbody').html(html);
        $('input[name="delete_param"]').on('click', function(){
            param_id = $(this).parents('tr').attr('param_id');
            delParam(param_id);
        });
        $('input[name="update_param"]').on('click', initUpdateParam);
    }
});
