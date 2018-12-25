$(function () {
    validator = initValidate(
        $('#manager_region_modal_form'),
        {
            'manager_account': {
                required: true,
                format_check: /^886\d{4}$/,
            },
        },
    );

    function queryManagerRegion(data){
        $('#loading').show();
        $.get(url_pre + '/manager_region/query/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                refreshManagerRegion(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        }).error(function(){
            $('#loading').hide();
            toptips('服务器错误', 'danger');
        });
    }
    $('#query_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        //console.log(data);
        queryManagerRegion(data);
    });

    $('#gen_excel_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open(url_pre + '/manager_region/query/' + query_string);
    });

    $('#upload_btn').on('click', function(){
        files = $('#upfile')[0].files;
        if(!files.length){
            toptips('请先选择文件', 'danger');
            return false;
        }
        file = files[0];
        f_name = file.name;
        idx1 = f_name.lastIndexOf('.');
        idx2 = f_name.length;
        suffix = f_name.substring(idx1 + 1, idx2);
        //console.log(suffix);
        if(suffix != 'xls' && suffix != 'xlsx'){
            toptips('上传文件格式不对，只接受excel', 'danger');
            return false;
        }
        var formData = new FormData();
        formData.append('upfile', file);
        $('#loading').show();
        $.ajax({
            url: url_pre + '/manager_region/upload/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(resp){
                $('#loading').hide();
                if(resp.success){
                    $('#query_btn').trigger('click');
                    swal('成功', '导入成功', 'success');
                }else{
                    swal('失败', resp.msg, 'error');
                }
            },
            error: function(resp){
                $('#loading').hide();
                swal('服务器错误', resp.msg, 'error');
            }
        });
    });
    
    function addManagerRegion(data) {
        $('#loading').show();
        $.post(url_pre + '/manager_region/add/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#manager_region_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            $('#loading').hide();
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#manager_region_modal_form')[0].reset();

        $('#manager_region_modal input[name="address_code"]').attr('readonly', false);
        $('#manager_region_modal').find('.modal-title').text('新增记录');
        $('#manager_region_modal_submit').off('click').on('click', function(){
            if(!$('#manager_region_modal_form').valid()) return false;
            data = $('#manager_region_modal_form').serializeForm();
            addManagerRegion(JSON.stringify(data));
        });
    });

    function delManagerRegion(address_code){
        swal({
            title: "删除确认",
            text: "确定删除该记录？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'address_code': address_code,
            });
            $.post(url_pre + '/manager_region/delete/', data, function(resp){
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

    function updateManagerRegion(data){
        $('#loading').show();
        $.post(url_pre + '/manager_region/update/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#manager_region_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            $('#loading').hide();
            swal('错误', '服务器错误', 'error');
        }); 
    }
    function initUpdateManagerRegion(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#manager_region_modal_form')[0].reset();

        var update_btn = $(this);

        $('#manager_region_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });

        $('#manager_region_modal input[name="address_code"]').attr('readonly', true);

        $('#manager_region_modal').find('.modal-title').text('更新记录');
        $('#manager_region_modal_submit').off('click').on('click', function(){
            if(!$('#manager_region_modal_form').valid()) return false;
            data = $('#manager_region_modal_form').serializeForm();
            updateManagerRegion(JSON.stringify(data));
        });
        $('#manager_region_modal').modal('show');
    }

    function refreshManagerRegion(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            manager_regions = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            manager_regions.page = changePage(action);
            queryManagerRegion(manager_regions);
        });
        $('input[name="delete"]').on('click', function(){
            address_code = $(this).parents('tr').find('[field="address_code"]').text();
            console.log(address_code);
            delManagerRegion(address_code);
        });
        $('input[name="update"]').on('click', initUpdateManagerRegion);
    }
});
