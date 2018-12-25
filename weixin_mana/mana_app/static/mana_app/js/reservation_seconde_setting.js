$(function(){
    var validator =initValidate(
       $('#manager_modal_form'),
        {
            'date_seconde': {
                required: true,
            },
            'credits': {
                required: true,
            },
            'dec': {
                required:false,
            }
        },
    );
     function queryManager(manager_name){
        data = {
            'sign_name': manager_name,
        }
        $.get('/mana_app/reservation/second/query/', data, function(resp){
            if(resp.success){
                refreshManager(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        manager_name = $('input[name="sign_name"]').val();
        queryManager(manager_name);
    });


    function delManager(manager_id){
        swal({
            title: "删除确认",
            text: "确定删除该行？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'id': $('#id').attr('column_id'),
            });
            alert(data);
            $.post('/mana_app/reservation/second/delete/', data, function(resp){
                if(resp.success){
                    refreshManager(resp.html);
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }

    function addManager(data) {
        $.post('/mana_app/reservation/second/add/', data, function(resp){
            if(resp.success){
                $('#manager_modal').modal('hide');
                refreshManager(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }

    $('#add_manager_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#manager_modal_form')[0].reset();
        $('#manager_modal').find('.modal-title').text('新增签到规则');

        $('#manager_modal_submit').off('click').on('click', function(){
            if(!$('#manager_modal_form').valid()) return false;

            data = $('#manager_modal_form').serializeForm();
            addManager(JSON.stringify(data));
        });
    });

    $('input[name="delete_manager"]').on('click', function(){
        manager_id = $(this).parents('tr').attr('manager_id');
        console.log(manager_id);
        delManager(manager_id);
    });

    function initUpdateManager(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#manager_modal_form')[0].reset();
        var update_btn = $(this);

        var id = update_btn.parents('tr').attr('column_id');
        var day = update_btn.parents('tr').find('td[field="date_seconde"]').text();
        var credits = update_btn.parents('tr').find('td[field="credits"]').text();
        var dec = update_btn.parents('tr').find('td[field="dec"]').text();
        var manager_name =update_btn.parents('tr').find('td[field="manager_name"]');
        var option = new Array();

        $('#manager_modal').find('.modal-title').text('更新字段');
        $('#manager_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        $('#manager_modal_submit').off('click').on('click', function(){
            if(!$('#manager_modal_form').valid()) return false;
            data = $('#manager_modal_form').serializeForm();
            data['id'] = id;
            updateManager(JSON.stringify(data));
        });
        $('#manager_modal').modal('show');
    }
        function updateManager(data){
        $.post('/mana_app/reservation/second/update/', data, function(resp){
            if(resp.success){
                $('#manager_modal').modal('hide');
                refreshManager(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
 $('input[name="update_manager"]').on('click', initUpdateManager);
    function refreshManager(html){
        $('tbody').html(html);
        $('input[name="delete_manager"]').on('click', function(){
            manager_id = $("#id").attr('id');
            delManager(id);
        });
        $('input[name="update_manager"]').on('click', initUpdateManager);
    }

});
