$(function () {
    validator = initValidate(
        $('#pre_credit_line_modal_form'),
        {
            'cusno': {
                required: true,
                format_check: /(^\d{21}$)|(^\d{20}(\d|X|x)$)/,
            },
            'manager_account': {
                required: true,
                format_check: /^886\d{4}$/,
            },
        },
    );

    function queryPreCreditLine(data){
        $('#loading').show();
        $.get(url_pre + '/pre_credit_line/query/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                refreshPreCreditLine(resp.html);
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
        queryPreCreditLine(data);
    });

    $('#gen_excel_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open(url_pre + '/pre_credit_line/query/' + query_string);
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
            url: url_pre + '/pre_credit_line/upload/',
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
    
    function addPreCreditLine(data) {
        $('#loading').show();
        $.post(url_pre + '/pre_credit_line/add/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#pre_credit_line_modal').modal('hide');
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
        $('#pre_credit_line_modal_form')[0].reset();

        $('#pre_credit_line_modal input[name="cusno"]').attr('readonly', false);
        $('#pre_credit_line_modal').find('.modal-title').text('新增记录');
        $('#pre_credit_line_modal_submit').off('click').on('click', function(){
            if(!$('#pre_credit_line_modal_form').valid()) return false;
            data = $('#pre_credit_line_modal_form').serializeForm();
            addPreCreditLine(JSON.stringify(data));
        });
    });

    function delPreCreditLine(cusno){
        swal({
            title: "删除确认",
            text: "确定删除该记录？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'cusno': cusno,
            });
            $.post(url_pre + '/pre_credit_line/delete/', data, function(resp){
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

    function updatePreCreditLine(data){
        $('#loading').show();
        $.post(url_pre + '/pre_credit_line/update/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#pre_credit_line_modal').modal('hide');
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
    function initUpdatePreCreditLine(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#pre_credit_line_modal_form')[0].reset();

        var update_btn = $(this);

        $('#pre_credit_line_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });

        $('#pre_credit_line_modal input[name="cusno"]').attr('readonly', true);

        $('#pre_credit_line_modal').find('.modal-title').text('更新记录');
        $('#pre_credit_line_modal_submit').off('click').on('click', function(){
            if(!$('#pre_credit_line_modal_form').valid()) return false;
            data = $('#pre_credit_line_modal_form').serializeForm();
            updatePreCreditLine(JSON.stringify(data));
        });
        $('#pre_credit_line_modal').modal('show');
    }

    function refreshPreCreditLine(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            cus_regions = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action); 
            cus_regions.page = changePage(action);
            queryPreCreditLine(cus_regions);
        });
        $('input[name="delete"]').on('click', function(){
            cusno = $(this).parents('tr').find('[field="cusno"]').text();
            console.log(cusno);
            delPreCreditLine(cusno);
        });
        $('input[name="update"]').on('click', initUpdatePreCreditLine);
    }
});
