$(function(){
    var validator =initValidate(
       $('#date_setting_modal_form'),
        {
            'date': {
                required: true,
            },
            'dec': {
                required:false,
            }
        },
    );
    function queryDateSetting(data){
        $.get('/mana_app/reservation/date/query/', data, function(resp){
            if(resp.success){
                refreshDateSetting(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        queryDateSetting(data);
    });


    function delDateSetting(date_setting_id){
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
            $.post('/mana_app/reservation/date/delete/', data, function(resp){
                if(resp.success){
                    swal('成功', resp.msg, 'success');
                    $('#query_btn').trigger('click');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }
    $('input[name="delete_date_setting"]').on('click', function(){
        date_setting_id = $(this).parents('tr').attr('date_setting_id');
        console.log(date_setting_id);
        delDateSetting(date_setting_id);
    });


    function addDateSetting(data) {
        $.post('/mana_app/reservation/date/add/', data, function(resp){
            if(resp.success){
                $('#date_setting_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_date_setting_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#date_setting_modal_form')[0].reset();
        $('#date_setting_modal').find('.modal-title').text('新增预约假期');

        $('#date_setting_modal_submit').off('click').on('click', function(){
            if(!$('#date_setting_modal_form').valid()) return false;

            data = $('#date_setting_modal_form').serializeForm();
            addDateSetting(JSON.stringify(data));
        });
    });

    function initUpdateDateSetting(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#date_setting_modal_form')[0].reset();
        var update_btn = $(this);

        var id = update_btn.parents('tr').attr('column_id');
        var day = update_btn.parents('tr').find('td[field="date_seconde"]').text();
        var credits = update_btn.parents('tr').find('td[field="credits"]').text();
        var dec = update_btn.parents('tr').find('td[field="dec"]').text();
        var date_setting_name =update_btn.parents('tr').find('td[field="date_setting_name"]');
        var option = new Array();

        $('#date_setting_modal').find('.modal-title').text('更新字段');
        $('#date_setting_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        $('#date_setting_modal_submit').off('click').on('click', function(){
            if(!$('#date_setting_modal_form').valid()) return false;
            data = $('#date_setting_modal_form').serializeForm();
            data['id'] = id;
            updateDateSetting(JSON.stringify(data));
        });
        $('#date_setting_modal').modal('show');
    }

    function updateDateSetting(data){
        $.post('/mana_app/reservation/date/update/', data, function(resp){
            if(resp.success){
                $('#date_setting_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_date_setting"]').on('click', initUpdateDateSetting);

    function refreshDateSetting(html){
        $('#table_area').html(html);
        $('input[name="delete_date_setting"]').on('click', function(){
            date_setting_id = $("#id").attr('id');
            delDateSetting(id);
        });
        $('input[name="update_date_setting"]').on('click', initUpdateDateSetting);
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryDateSetting(params);
        });
    }

});
