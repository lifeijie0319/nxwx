$(function () {
    $('input[name="start_date"]').val('2017-01-01');
    $('input[name="end_date"]').val(getCurrentDate());
    $('.table-responsive').responsiveTable({
        addFocusBtn: false,
        i18n:{
            focus:"聚焦",
            display:"选择显示",
            displayAll:"显示全部"
        }
    });
    validator = initValidate(
        $('#query_form'),
        {   
            'start_date': {
                required: true,
            },
            'end_date': {
                required: true,
            },
        }
    );

    function queryWithdrawAppplication(data){
        $.get('/mana_app/withdraw_application/query/', data, function(resp){
            if(resp.success){
                refreshWithdrawAppplication(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_withdraw_application_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        queryWithdrawAppplication(data);
    });
    $('#gen_excel_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/withdraw_application/query/' + query_string);
    });

    function auditWithdrawAppplication(withdraw_application_id, audit){
        var data = JSON.stringify({
            'withdraw_application_id': withdraw_application_id,
            'audit': audit,
        });
        $.post('/mana_app/withdraw_application/audit/', data, function(resp){
            if(resp.success){
                $('#query_withdraw_application_btn').trigger('click');
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('input[name="pass_withdraw_application"]').on('click', function(){
        withdraw_application_id = $(this).parents('tr').attr('withdraw_application_id');
        auditWithdrawAppplication(withdraw_application_id, 'pass');
    });
    $('input[name="reject_withdraw_application"]').on('click', function(){
        withdraw_application_id = $(this).parents('tr').attr('withdraw_application_id');
        auditWithdrawAppplication(withdraw_application_id, 'reject');
    });
    function refreshWithdrawAppplication(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="pass_withdraw_application"]').on('click', function(){
            withdraw_application_id = $(this).parents('tr').attr('withdraw_application_id');
            auditWithdrawAppplication(withdraw_application_id, 'pass');
        });
        $('input[name="reject_withdraw_application"]').on('click', function(){
            withdraw_application_id = $(this).parents('tr').attr('withdraw_application_id');
            auditWithdrawAppplication(withdraw_application_id, 'reject');
        });
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryWithdrawAppplication(params);
        });
    }
});
