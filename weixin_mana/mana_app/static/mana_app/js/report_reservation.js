$(function () {
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
            'on_date': {
                required: true,
            },
            'off_date': {
                required: true,
            },
        },
    );

    function queryReservation(data){
        $.get('/mana_app/report/reservation/query/', data, function(resp){
            if(resp.success){
                refreshReservation(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        //console.log(data);
        queryReservation(data);
    });

    $('#gen_excel_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/report/reservation/query/' + query_string);
    });

    function refreshReservation(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('ul.pager a').on('click', function(){
            reservations = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            reservations.page = changePage(action);
            queryReservation(reservations);
        });
    }
});
