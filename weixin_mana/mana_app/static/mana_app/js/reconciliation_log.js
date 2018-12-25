$(function () {
    function queryReconciliationLog(data){
        $.get('/mana_app/reconciliation/log/query/', data, function(resp){
            if(resp.success){
                refreshReconciliationLog(resp.html);
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
        queryReconciliationLog(data);
    });

    function refreshReconciliationLog(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            reconciliation_logs = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            reconciliation_logs.page = changePage(action);
            queryReconciliationLog(reconciliation_logs);
        });
    }
});
