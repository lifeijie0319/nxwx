$(function () {
    $('input[name="start_date"]').val('2017-01-01');
    $('input[name="end_date"]').val(getCurrentDate());
    //console.log(initValidate)
    validator = initValidate(
        $('#query_form'),
        {
            'start_date': {
                required: true,
            },
            'end_date': {
                required: true,
            },
            'cus_telno': {
                format_check: /^\d{11}$/,
            },
        },
    );

    function queryTradeDetail(data){
        $.get('/mana_app/report/cus_trade_detail/query/', data, function(resp){
            if(resp.success){
                refreshTradeDetail(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_trade_detail_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        //console.log(data);
        queryTradeDetail(data);
    });
    $('#gen_excel_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/report/cus_trade_detail/query/' + query_string);
        /*$.get('/mana_app/report/cus_trade_detail/query/', data, function(resp){
            if(resp.success){
                console.log(resp);//toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });*/
    });

    function refreshTradeDetail(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryTradeDetail(params);
        });
    }
});
