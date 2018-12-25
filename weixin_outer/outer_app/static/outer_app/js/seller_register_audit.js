$(function(){
    role = $('input:hidden').val();
    console.log(role);

    var allocate_flag = false;
    $('a[name="allocate"]').on('click', function(){
        apply_id = $(this).parents('div[name="apply_block"]').attr('apply_id');
        if(role == '总行管理员'){
            branch_id = $(this).parents('div[name="apply_block"]').find('select').val();
            data = {
                'apply_id': apply_id,
                'branch_id': branch_id,
            }
            if(allocate_flag) return false;
            allocate_flag = true;
            $.post(url_pre + '/register/seller/audit/head_admin/', data, function(resp){
                allocate_flag = false;
                console.log(resp);
                if(resp.success){
                    window.location.reload();
                }else{
                    $.toptips(resp.msg);
                }
            }).error(function(){
                $.toptips('服务器错误');
            });
        }else if(role == '支行管理员'){
            client_manager_id = $(this).parents('div[name="apply_block"]').find('select').val();
            data = {
                'apply_id': apply_id,
                'client_manager_id': client_manager_id,
            }
            if(allocate_flag) return false;
            allocate_flag = true;
            $.post(url_pre + '/register/seller/audit/branch_admin/', data, function(resp){
                allocate_flag = false;
                if(resp.success){
                    window.location.reload();
                }else{
                    $.toptips(resp.msg);
                }
            }).error(function(){
                $.toptips('服务器错误');
            });
        }else{
            $.toptips('不合法的管理员角色');
        }
    });

    var pass_flag = false;
    $('a[name="pass"]').on('click', function(){
        if(pass_flag) return false;
        pass_flag = true;
        apply_id = $(this).parents('div[name="apply_block"]').attr('apply_id');
        data = {
            'apply_id': apply_id,
            'operation': 'pass'
        }
        $.post(url_pre + '/register/seller/audit/client_manager/', data, function(resp){
            pass_flag = false;
            if(resp.success){
                window.location.reload();
            }else{
                $.toptips(resp.msg);
            }
        }).error(function(){
            $.toptips('服务器错误');
        });
    });

    var reject_flag = false;
    $('a[name="reject"]').on('click', function(){
        if(reject_flag) return false;
        reject_flag = true;
        apply_id = $(this).parents('div[name="apply_block"]').attr('apply_id');
        data = {
            'apply_id': apply_id,
            'operation': 'reject'
        }
        $.post(url_pre + '/register/seller/audit/client_manager/', data, function(resp){
            reject_flag = false;
            if(resp.success){
                window.location.reload();
            }else{
                $.toptips(resp.msg);
            }
        }).error(function(){
            $.toptips('服务器错误');
        });
    });
});
