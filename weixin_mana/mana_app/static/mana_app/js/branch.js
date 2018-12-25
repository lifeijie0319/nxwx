$(function(){
    $('.table-responsive').responsiveTable({
        addFocusBtn: false,
        i18n:{
            focus:"聚焦",
            display:"选择显示",
            displayAll:"显示全部"
        }
    });
    var validator =initValidate(
       $('#branch_modal_form'),
        {
            'deptno': {
                required: true,
                format_check: /^\d{1,8}$/,
            },
            'name': {
                required: true,
            },
            'address': {
                required:true,
            },
            'latitude': {
                required:true,
                format_check: /^\d{1,2}\.\d{6}$/,
            },
            'longitude': {
                required:true,
                format_check: /^\d{1,3}\.\d{6}$/,
            },
        },
    );
    function queryBranch(data){
        $.get('/mana_app/branch/query/', data, function(resp){
            if(resp.success){
                refreshBranch(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        page_dom = $('ul.pager li[name="current_page"]');
        data = {
            'branch_name': $('#query_form').find('input[name="branch_name"]').val(),
            'page': page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, '')),
        }
        queryBranch(data);
    });

    function delBranch(branch_id){
        swal({
            title: "删除确认",
            text: "确定删除该行？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'branch_id': branch_id,
            });
            //alert(data);
            $.post('/mana_app/branch/delete/', data, function(resp){
                if(resp.success){
                    $('#query_btn').trigger('click');
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }
    $('input[name="delete_branch"]').on('click', function(){
        branch_id = $(this).parents('tr').attr('branch_id');
        console.log(branch_id);
        delBranch(branch_id);
    });


    function addBranch(data) {
        $.post('/mana_app/branch/add/', data, function(resp){
            if(resp.success){
                $('#branch_modal').modal('hide');
                $('#query_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }

    $('#add_branch_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#branch_modal_form')[0].reset();
        $('#branch_modal').find('.modal-title').text('新增银行网点');

        $('#branch_modal_submit').off('click').on('click', function(){
            if(!$('#branch_modal_form').valid()) return false;

            data = $('#branch_modal_form').serializeForm();
            addBranch(JSON.stringify(data));
        });
    });

    function initUpdateBranch(){
        function set_optional(update_btn, field){
            var name = update_btn.parents('tr').find('td[field="' + field + '"]').text();
            $('#branch_modal').find('select[name="' + field + '"] > option').each(function(idx, ele){
                console.log(name, $(ele).text(), $(ele).text() == name);
                if($(ele).text() == name){
                    $(ele).prop('selected', true);
                }
            });
        }
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#branch_modal_form')[0].reset();
        var update_btn = $(this);

        $('#branch_modal').find('.modal-title').text('更新银行网点');
        $('#branch_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        set_optional(update_btn, 'is_map');
        set_optional(update_btn, 'is_loan');
        set_optional(update_btn, 'is_etc');
        set_optional(update_btn, 'is_oppen_account');
        set_optional(update_btn, 'is_withdrawal');
        set_optional(update_btn, 'is_dgkh');
        set_optional(update_btn, 'parent');
        set_optional(update_btn, 'level');
        $('#branch_modal_submit').off('click').on('click', function(){
            if(!$('#branch_modal_form').valid()) return false;
            data = $('#branch_modal_form').serializeForm();
            data['branch_id'] = update_btn.parents('tr').attr('branch_id');
            updateBranch(JSON.stringify(data));
        });
        $('#branch_modal').modal('show');
    }
    function updateBranch(data){
        $.post('/mana_app/branch/update/', data, function(resp){
            if(resp.success){
                $('#branch_modal').modal('hide');
                $('#query_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_branch"]').on('click', initUpdateBranch);
    function refreshBranch(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="delete_branch"]').on('click', function(){
            branch_id = $(this).parents('tr').attr('branch_id');
            delBranch(branch_id);
        });
        $('input[name="update_branch"]').on('click', initUpdateBranch);
        $('ul.pager a').on('click', function(){
            branches = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            branches.page = changePage(action);
            queryBranch(branches);
        });
    }

});
