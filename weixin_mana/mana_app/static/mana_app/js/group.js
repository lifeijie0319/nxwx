$(function () {

    var validator = initValidate(
        $('#group_modal_form'),
        {
            'group_name': {
                required: true,
                format_check: /^[a-zA-Z][a-zA-Z0-9_]{2,15}$/,
            }
        },
    );

    function addGroup(group_name) {
        var data = JSON.stringify({
            'group_name': group_name,
        });
        $.post('/mana_app/group/add/', data, function(resp){
            if(resp.success){
                $('#group_modal').modal('hide');
                refreshGroup(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_group_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#group_modal_form')[0].reset();
        $('#group_modal').find('.modal-title').text('新增用户组');
        $('#group_modal_submit').on('click', function(){
            if(!$('#group_modal_form').valid()) return false;
            group_name = $('input[name="group_name"]').val();
            addGroup(group_name);
        });
    });

    function delGroup(group_id){
        swal({
            title: "删除确认",
            text: "确定删除该用户组？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'group_id': group_id,
            });
            $.post('/mana_app/group/delete/', data, function(resp){
                if(resp.success){
                    refreshGroup(resp.html);
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }
    $('input[name="delete_group"]').on('click', function(){
        group_id = $(this).parents('tr').attr('group_id');
        console.log(group_id);
        delGroup(group_id);
    });

    function updateGroup(data){
        $.post('/mana_app/group/update/', data, function(resp){
            if(resp.success){
                $('#group_modal').modal('hide');
                refreshGroup(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function initUpdateGroup(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#group_modal_form')[0].reset();

        var update_btn = $(this);
        var group_id = update_btn.parents('tr').attr('group_id');
        var group_name = update_btn.parents('tr').find('td[field="name"]').text();
        $('#group_modal').find('.modal-title').text('更新用户组');
        $('#group_modal').find('input[name="group_name"]').val(group_name);

        $('#group_modal_submit').off('click').on('click', function(){
            if(!$('#group_modal_form').valid()) return false;
            data = $('#group_modal_form').serializeForm();
            data['group_id'] = group_id;
            updateGroup(JSON.stringify(data));
        });
        $('#group_modal').modal('show');
    }
    $('input[name="update_group"]').on('click', initUpdateGroup);

    function queryGroup(group_name){
        data = {
            'group_name': group_name,
        }
        $.get('/mana_app/group/query/', data, function(resp){
            if(resp.success){
                refreshGroup(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_group_btn').on('click', function(){
        group_name = $('input[name="query_group_name"]').val();
        queryGroup(group_name);
    });

    function refreshGroup(html){
        $('tbody').html(html);
        $('input[name="delete_group"]').on('click', function(){
            group_id = $(this).parents('tr').attr('group_id');
            delGroup(group_id);
        });
        $('input[name="update_group"]').on('click', initUpdateGroup);
        $('input[name="group_menu"]').on('click', function(){
            group_id = $(this).parents('tr').attr('group_id');
            group_name = $(this).parents('tr').find('td[field="name"]').text();
            getGroupMenu(group_id, group_name);
        });
    }

    function getGroupMenu(group_id, group_name){
        $("#group_menu_modal_data").parent().html('<div id="group_menu_modal_data"></div>');
        $('#group_menu_modal_name').text(group_name).attr('group_id', group_id);
        var post_data = JSON.stringify({
            'group_id': group_id,
        });
        $.post('/mana_app/group/menu/', post_data, function(resp){
            console.log(resp.data);
            $('#group_menu_modal_data').jstree({
                'core': {
                    'data': resp.data,
                },
                'checkbox': {
                    'keep_selected_style': false
                },
                'plugins': ['checkbox', 'wholerow']
            });
        });
        $('#group_menu_modal').modal('show');
    }
    $('input[name="group_menu"]').on('click', function(){
        group_id = $(this).parents('tr').attr('group_id');
        console.log(group_id);
        group_name = $(this).parents('tr').find('td[field="name"]').text();
        getGroupMenu(group_id, group_name);
    });

    function get_all_checked(jstree_node){
        var tmp = new Array;
        $.each(jstree_node._model.data, function(key, value){
            console.log(key, value);
            if(value.id != '#' && jstree_node.is_undetermined(value) || jstree_node.is_checked(value)){
                var id = value.id.slice(4);
                tmp.push(id);
            }
        });
        return tmp;
    }
    $('#group_menu_modal_submit').on('click', function(){
        var root = $("#group_menu_modal_data").jstree(true);
        nodes = get_all_checked(root);
        console.log(nodes);
        data = JSON.stringify({
            'group_id': $('#group_menu_modal_name').attr('group_id'),
            'menu': nodes,
        });
        $.post('/mana_app/group/menu/update/', data, function(resp){
            console.log(resp);
            $('#group_menu_modal').modal('hide');
            if(resp.success){
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    });

});
