$(function () {
    validator = initValidate(
        $('#micro_credit_contract_modal_form'),
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

    function queryMicroCreditContract(data){
        $('#loading').show();
        $.get(url_pre + '/micro_credit_contract/query/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                refreshMicroCreditContract(resp.html);
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
        queryMicroCreditContract(data);
    });

    $('#gen_excel_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open(url_pre + '/micro_credit_contract/query/' + query_string);
    });

    $('#upload_btn').on('click', function(){
        files = $('#upfile')[0].files;
        if(!files.length){
            toptips('请先选择文件', 'danger');
            return false;
        }
        var formData = new FormData();
        //console.log($('#upfile')[0].files[0]);
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
        formData.append('upfile', file);
        $('#loading').show();
        $.ajax({
            url: url_pre + '/micro_credit_contract/upload/',
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
    
    function addMicroCreditContract(data) {
        $('#loading').show();
        $.post(url_pre + '/micro_credit_contract/add/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#micro_credit_contract_modal').modal('hide');
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
        $('#micro_credit_contract_modal_form')[0].reset();

        $('#micro_credit_contract_modal input[name="cusno"]').attr('readonly', false);
        $('#micro_credit_contract_modal').find('.modal-title').text('新增记录');
        $('#micro_credit_contract_modal_submit').off('click').on('click', function(){
            if(!$('#micro_credit_contract_modal_form').valid()) return false;
            data = $('#micro_credit_contract_modal_form').serializeForm();
            addMicroCreditContract(JSON.stringify(data));
        });
    });

    function delMicroCreditContract(cusno){
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
            $.post(url_pre + '/micro_credit_contract/delete/', data, function(resp){
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

    function updateMicroCreditContract(data){
        $('#loading').show();
        $.post(url_pre + '/micro_credit_contract/update/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#micro_credit_contract_modal').modal('hide');
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
    function initUpdateMicroCreditContract(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#micro_credit_contract_modal_form')[0].reset();

        var update_btn = $(this);

        $('#micro_credit_contract_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });

        $('#micro_credit_contract_modal input[name="cusno"]').attr('readonly', true);

        $('#micro_credit_contract_modal').find('.modal-title').text('更新记录');
        $('#micro_credit_contract_modal_submit').off('click').on('click', function(){
            if(!$('#micro_credit_contract_modal_form').valid()) return false;
            data = $('#micro_credit_contract_modal_form').serializeForm();
            updateMicroCreditContract(JSON.stringify(data));
        });
        $('#micro_credit_contract_modal').modal('show');
    }

    function refreshMicroCreditContract(html){
        $('#table_area').html(html);
        current_page = parseInt($('ul.pager li[name="current_page"]').text().replace(/\D/g, ''));
        $('ul.pager a').on('click', function(){
            micro_credit_contracts = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            micro_credit_contracts.page = changePage(action);
            queryMicroCreditContract(micro_credit_contracts);
        });
        $('input[name="delete"]').on('click', function(){
            cusno = $(this).parents('tr').find('[field="cusno"]').text();
            console.log(cusno);
            delMicroCreditContract(cusno);
        });
        $('input[name="update"]').on('click', initUpdateMicroCreditContract);
    }
});
