$(function () {
    $('input[name="reg_date"]').val(getCurrentDate());
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
            'reg_date': {
                required: true,
            },
        },
    );

    function queryShop(data){
        $.get('/mana_app/shop/query/', data, function(resp){
            if(resp.success){
                refreshShop(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_shop_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        console.log(data);
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        queryShop(data);
    });
    $('#gen_excel_btn').on('click', function(){
        if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open('/mana_app/shop/query/' + query_string);
    });

    /*function stickShop(shop_id, stick){
        var data = JSON.stringify({
            'shop_id': shop_id,
            'stick': stick,
        });
        $.post('/mana_app/shop/stick/', data, function(resp){
            if(resp.success){
                $('#query_shop_btn').trigger('click');
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('input[name="stick_shop"]').on('click', function(){
        shop_id = $(this).parents('tr').attr('shop_id');
        stickShop(shop_id, true);
    });
    $('input[name="unstick_shop"]').on('click', function(){
        shop_id = $(this).parents('tr').attr('shop_id');
        stickShop(shop_id, false);
    });*/

    function updateShop(data){
        $.post('/mana_app/shop/update/', data, function(resp){
            if(resp.success){
                $('#shop_update_modal').modal('hide');
                $('#query_shop_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function updateShopModal(){
        function set_optional(update_btn, field){
            var name = update_btn.parents('tr').find('td[field="' + field + '"]').text()
            $('#shop_update_modal').find('select[name="' + field + '"] > option').each(function(idx, ele){
                if($(ele).text() == name){
                    $(ele).prop('selected', true);
                }
            });
        }
        $('#shop_update_form')[0].reset();
        var update_btn = $(this);
        var shop_id = update_btn.parents('tr').attr('shop_id');
        $('#shop_update_modal').find('input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        set_optional(update_btn, 'type');
        set_optional(update_btn, 'bank');
        set_optional(update_btn, 'stick');
        var coupon_names = update_btn.parents('tr').find('td[field="coupons"]').text().split('|');
        console.log('coupon_names', coupon_names);
        var real_coupon_names = new Array();
        $.each(coupon_names, function(index, value, array){
            real_value = value.replace(/\s*/g, '');
            if(real_value){
                real_coupon_names.push(real_value);
            }
        });
        $('#shop_update_modal').find('select[name="coupons"] > option').each(function(idx, ele){
            if($.inArray($(ele).text(), real_coupon_names) != -1){
                $(ele).prop('selected', true);
            }
        });
        $('#coupons_update_submit').off('click').on('click', function(){
            data = $('#shop_update_form').serializeForm();
            data['shop_id'] = shop_id;
            console.log(data);
            updateShop(JSON.stringify(data));
        });
        $('#shop_update_modal').modal('show');
    }
    $('input[name="update"]').on('click', updateShopModal);

    function refreshShop(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="update"]').on('click', updateShopModal);
        /*$('input[name="stick_shop"]').on('click', function(){
            shop_id = $(this).parents('tr').attr('shop_id');
            stickShop(shop_id, true);
        });
        $('input[name="unstick_shop"]').on('click', function(){
            shop_id = $(this).parents('tr').attr('shop_id');
            stickShop(shop_id, false);
        });*/
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryShop(params);
        });
    }
});
