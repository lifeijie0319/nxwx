$(function () {

    var validator = initValidate(
        $('#manager_modal_form'),
        {
            'manager_account': {
                required: true,
                maxlength: 18,
                format_check: /^[a-zA-Z0-9_]{6,15}$/
            },
            'manager_name': {
                required: false,
                format_check:  /^[\u4e00-\u9fa5]{2,8}$/
            },
            'manager_idcardno': {
                required: true,
                format_check: /(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
            },
            'manager_telno': {
                format_check: /^[0-9]{11}$/,
            },
        },
    );
    //console.log(validator);
    function addManager(data) {
        $.post('/mana_app/manager/add/', data, function(resp){
            if(resp.success){
                $('#manager_modal').modal('hide');
                $('#query_manager_btn').trigger('click');
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
        $('#manager_modal').find('input[name="manager_account"]').prop('disabled', false);
        $('#manager_modal').find('.modal-title').text('新增用户');
        $('#manager_modal_submit').off('click').on('click', function(){
            if(!$('#manager_modal_form').valid()) return false;
            data = $('#manager_modal_form').serializeForm();
            console.log(data);
            addManager(JSON.stringify(data));
        });
    });

    /*function delManager(manager_id){
        swal({
            title: "删除确认",
            text: "确定删除该用户？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'manager_id': manager_id,
            });
            $.post('/mana_app/manager/delete/', data, function(resp){
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
    $('input[name="delete_manager"]').on('click', function(){
        manager_id = $(this).parents('tr').attr('manager_id');
        console.log(manager_id);
        delManager(manager_id);
    });*/

    function updateManager(data){
        $.post('/mana_app/manager/update/', data, function(resp){
            if(resp.success){
                $('#manager_modal').modal('hide');
                $('#query_manager_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function initUpdateManager(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#manager_modal_form')[0].reset();
        $('#manager_modal').find('input[name="manager_account"]').prop('disabled', true);

        var update_btn = $(this);
        var manager_id = update_btn.parents('tr').attr('manager_id');
        var group_names = update_btn.parents('tr').find('td[field="manager_group"]').text().split('|');
        var real_group_names = new Array();
        $.each(group_names, function(index, value, array){
            real_value = value.replace(/\s*/g, '');
            if(real_value){
                real_group_names.push(real_value);
            }
        });
        console.log(real_group_names);
        $('#manager_modal').find('.modal-title').text('更新用户');
        $('#manager_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        singleSelection('manager_modal', update_btn, 'manager_bankbranch');
        singleSelection('manager_modal', update_btn, 'manager_role');
        singleSelection('manager_modal', update_btn, 'manager_subrole');
        singleSelection('manager_modal', update_btn, 'manager_status');
        $('#manager_modal').find('select[name="manager_groups"] > option').each(function(idx, ele){
            if($.inArray($(ele).text(), real_group_names) != -1){
                $(ele).prop('selected', true);
            }
        });
        $('#manager_modal_submit').off('click').on('click', function(){
            if(!$('#manager_modal_form').valid()) return false;
            data = $('#manager_modal_form').serializeForm();
            data['manager_id'] = manager_id;
            console.log(data);
            updateManager(JSON.stringify(data));
        });
        $('#manager_modal').modal('show');
    }
    $('input[name="update_manager"]').on('click', initUpdateManager);

    function queryManager(params){
        $.get('/mana_app/manager/query/', params, function(resp){
            if(resp.success){
                refreshManager(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_manager_btn').on('click', function(){
        page_dom = $('ul.pager li[name="current_page"]');
        params = {
            'manager_account': $('input[name="query_manager_account"]').val(),
            'manager_name': $('input[name="query_manager_name"]').val(),
            'page': page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, '')),
        }
        queryManager(params);
    });

    function ResetPassword(){
        manager_id = $(this).parents('tr').attr('manager_id');
        $.post('/mana_app/manager/reset_password/', {manager_id: manager_id}, function(resp){
            if(resp.success){
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="reset_password"]').on('click', ResetPassword);

    function refreshManager(html){
        $('#table_area').html(html);
        //$('input[name="delete_manager"]').on('click', function(){
        //    manager_id = $(this).parents('tr').attr('manager_id');
        //    delManager(manager_id);
        //});
        $('input[name="update_manager"]').on('click', initUpdateManager);
        $('input[name="reset_password"]').on('click', ResetPassword);
        $('ul.pager a').on('click', function(){
            managers = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            managers.page = changePage(action);
            queryManager(managers);
        });
    }

});
