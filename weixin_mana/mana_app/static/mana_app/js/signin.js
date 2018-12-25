$(function(){
    var validator =initValidate(
       $('#signin_rule_modal_form'),
        {
            'day': {
                required: true,
                format_check: /^\d{1,2}$/,
            },
            'credits': {
                required: true,
                format_check: /^\d{1,6}$/,
            },
            'dec': {
                required:false,
            }
        },
    );
    /*function querySignRule(signin_rule_name){
        data = {
            'sign_name': signin_rule_name,
        }
        $.get('/mana_app/signin_rule/query/', data, function(resp){
            if(resp.success){
                refreshSignRule(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        signin_rule_name = $('input[name="sign_name"]').val();
        querySignRule(signin_rule_name);
    });*/


    function delSignRule(signin_rule_id){
        swal({
            title: "删除确认",
            text: "确定删除该规则？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'signin_rule_id': signin_rule_id,
            });
            $.post('/mana_app/signin_rule/delete/', data, function(resp){
                if(resp.success){
                    refreshSignRule(resp.html);
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }

    function addSignRule(data) {
        $.post('/mana_app/signin_rule/add/', data, function(resp){
            if(resp.success){
                $('#signin_rule_modal').modal('hide');
                refreshSignRule(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }

    $('#add_signin_rule_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#signin_rule_modal_form')[0].reset();
        $('#signin_rule_modal').find('.modal-title').text('新增签到规则');
        $('#signin_rule_modal_submit').off('click').on('click', function(){
            if(!$('#signin_rule_modal_form').valid()) return false;
            data = $('#signin_rule_modal_form').serializeForm();
            addSignRule(JSON.stringify(data));
        });
    });

    $('input[name="delete_signin_rule"]').on('click', function(){
        signin_rule_id = $(this).parents('tr').attr('signin_rule_id');
        delSignRule(signin_rule_id);
    });

    function initUpdateSignRule(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#signin_rule_modal_form')[0].reset();
        var update_btn = $(this);
        
        var signin_rule_id = update_btn.parents('tr').attr('signin_rule_id');
        $('#signin_rule_modal').find('.modal-title').text('更新签到规则');
        $('#signin_rule_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        var remark = update_btn.parents('tr').find('td[field="dec"]').text()
        $('#signin_rule_modal textarea[name="dec"]').val(remark);
        $('#signin_rule_modal_submit').off('click').on('click', function(){
            if(!$('#signin_rule_modal_form').valid()) return false;
            data = $('#signin_rule_modal_form').serializeForm();
            data['signin_rule_id'] = signin_rule_id;
            updateSignRule(JSON.stringify(data));
        });
        $('#signin_rule_modal').modal('show');
    }
    function updateSignRule(data){
        $.post('/mana_app/signin_rule/update/', data, function(resp){
            if(resp.success){
                $('#signin_rule_modal').modal('hide');
                refreshSignRule(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_signin_rule"]').on('click', initUpdateSignRule);
    function refreshSignRule(html){
        $('tbody').html(html);
        $('input[name="delete_signin_rule"]').on('click', function(){
            signin_rule_id = $(this).parents('tr').attr('signin_rule_id');
            delSignRule(signin_rule_id);
        });
        $('input[name="update_signin_rule"]').on('click', initUpdateSignRule);
    }

});
