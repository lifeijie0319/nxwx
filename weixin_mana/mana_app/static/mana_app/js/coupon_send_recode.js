$(function(){

    function updateLotteryAward(){
        data = {
            manager_account: $('#base_manager_account').val(),
            lottery_record_id: $(this).parents('tr').attr('lottery_record_id'),
        }
        $.post('/mana_app/coupon_send_recode/table/', data, function(resp){
            if(resp.success){
                $('#query_lottery_record_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_lottery_record"]').on('click', updateLotteryAward)

    function refreshLotteryAward(html){
        $('#table_area').html(html);
        $('input[name="update_lottery_record"]').on('click', updateLotteryAward);
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryLotteryAward(params);
        });
    }

    function queryLotteryAward(data){
        $.get('/mana_app/coupon_send_recode/table/', data, function(resp){
            if(resp.success){
                refreshLotteryAward(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger'); 
            }
        });
    }
    $('#query_lottery_record_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        queryLotteryAward(data);
    });

    $('#gen_excel_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/coupon_send_recode/table//' + query_string);
    });
});
