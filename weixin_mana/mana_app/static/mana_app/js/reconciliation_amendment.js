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
       $('#reconciliation_amendment_modal_form'),
        {
            'trader_name': {
                required: true,
            },
            'pro': {
                max: 10000,
                required: true,
                format_check: /^\d{1,4}$/,
            },
        },
    );
    function queryReconciliationAmendment(data){
        $.get('/mana_app/reconciliation/amend/query/', data, function(resp){
            if(resp.success){
                refreshReconciliationAmendment(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        console.log(data);
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        queryReconciliationAmendment(data);
    });

    $('#auto_amend_btn').on('click', function(){
        swal({
            title: "自动补录确认",
            text: "自动补录会自动补录所有未补录的交易，是否确定？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            data = {
                manager_account: $('#base_manager_account').val(),
            }
            $.post('/mana_app/reconciliation/auto_amend/', data, function(resp){
                if(resp.success){
                    $('#reconciliation_amendment_modal').modal('hide');
                    swal('成功', resp.msg, 'success');
                    $('#query_btn').trigger('click');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    });
    function initUpdateReconciliationAmendment(){
        function set_optional(update_btn, field){
            var name = update_btn.parents('tr').find('td[field="' + field + '"]').text()
            $('#reconciliation_amendment_modal').find('select[name="' + field + '"] > option').each(function(idx, ele){
                if($(ele).text() == name){
                    $(ele).prop('selected', true);
                }
            });
        }
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#reconciliation_amendment_modal_form')[0].reset();
        var update_btn = $(this);

        $('#reconciliation_amendment_modal').find('.modal-title').text('手动补录');
        $('#reconciliation_amendment_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        set_optional(update_btn, 'trade_type');
        $('#reconciliation_amendment_modal_submit').off('click').on('click', function(){
            if(!$('#reconciliation_amendment_modal_form').valid()) return false;
            data = $('#reconciliation_amendment_modal_form').serializeForm();
            data['manager_account'] = $('#base_manager_account').val();
            data['amendment_id'] = update_btn.parents('tr').attr('reconciliation_amendment_id');
            updateReconciliationAmendment(JSON.stringify(data));
        });
        $('#reconciliation_amendment_modal').modal('show');
    }
    function updateReconciliationAmendment(data){
        $.post('/mana_app/reconciliation/amend_by_hand/', data, function(resp){
            if(resp.success){
                $('#reconciliation_amendment_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');;
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_reconciliation_amendment"]').on('click', initUpdateReconciliationAmendment);

    function refreshReconciliationAmendment(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="update_reconciliation_amendment"]').on('click', initUpdateReconciliationAmendment);
        $('ul.pager a').on('click', function(){
            reconciliation_amendments = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            reconciliation_amendments.page = changePage(action);
            queryReconciliationAmendment(reconciliation_amendments);
        });
    }

});
