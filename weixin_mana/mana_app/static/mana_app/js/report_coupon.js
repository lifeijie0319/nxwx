$(function () {
    $('input[name="on_date"]').val('2017-01-01');
    $('input[name="off_date"]').val(getCurrentDate());
    validator = initValidate(
        $('#query_form'),
        {   
            'on_date': {
                required: true,
            },
            'off_date': {
                required: true,
            },
        },
    );

    function queryCoupon(data){
        $.get('/mana_app/report/coupon/query/', data, function(resp){
            if(resp.success){
                refreshCoupon(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_report_coupon_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        console.log(data);
        queryCoupon(data);
    });

    $('#gen_excel_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/report/coupon/query/' + query_string);
    });

    function refreshCoupon(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryCoupon(params);
        });
    }
});
