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
        $('#coupon_term_modal_form'),
        {
            'arg_x': {
                required: true,
                format_check: /(^\d+$)|(^\d+\.\d+$)/,
            },
            'arg_y': {
                required: true,
                format_check: /(^\d+$)|(^\d+\.\d+$)/,
            },
            'arg_z': {
                required: true,
                format_check: /(^\d+$)|(^\d+\.\d+$)/,
            },
        },
    );

    function updateCouponTerm(data){
        $.post('/mana_app/coupon_term/update/', data, function(resp){
            if(resp.success){
                $('#coupon_term_modal').modal('hide');
                refreshCouponTerm(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function initUpdateCouponTerm(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#coupon_term_modal_form')[0].reset();

        var update_btn = $(this);
        var coupon_term_id = $(this).parents('tr').attr('coupon_term_id');

        $('#coupon_term_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            //console.log(input_value, !input_value);
            if(!input_value){
                $(this).prop('disabled', true);
            }else if(input_name == 'code'){
                $(this).val(input_value);
            }else{
                $(this).prop('disabled', false).val(input_value);
            }
        });
        var description = update_btn.parents('tr').find('td[field="description"]').text();
        $('#coupon_term_modal textarea[name="description"]').val(description);
        $('#coupon_term_modal_submit').off('click').on('click', function(){
            if(!$('#coupon_term_modal_form').valid()) return false;
            data = {};
            $('#coupon_term_modal input').each(function(index, dom){
                var input_name = $(this).attr('name');
                if(!$(this).prop('disabled')){
                    data[input_name] = $(this).val();
                }
            });
            data['coupon_term_id'] = coupon_term_id;
            updateCouponTerm(JSON.stringify(data));
        });
        $('#coupon_term_modal').modal('show');
    }
    $('input[name="update_coupon_term"]').on('click', initUpdateCouponTerm);

    function queryCouponTerm(coupon_term_code){
        data = {
            'coupon_term_code': coupon_term_code,
        }
        $.get('/mana_app/coupon_term/query/', data, function(resp){
            if(resp.success){
                refreshCouponTerm(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_coupon_term_btn').on('click', function(){
        coupon_term_code = $('input[name="query_coupon_term_code"]').val();
        queryCouponTerm(coupon_term_code);
    });

    function refreshCouponTerm(html){
        $('tbody').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="update_coupon_term"]').on('click', initUpdateCouponTerm);
    }
});
