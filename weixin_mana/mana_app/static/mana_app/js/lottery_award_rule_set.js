$(function(){
    var validator =initValidate(
       $('#lottery_award_modal_form'),
        {
            'credits': {
                required: true,
                format_check: /^\d+$/,
            },
            'pro': {
                max: 10000,
                required: true,
                format_check: /^\d{1,4}$/,
            },
        },
    );
    /*function queryLotteryAward(lottery_award_name){
        data = {
            'sign_name': lottery_award_name,
        }
        $.get('/mana_app/lottery/award/query/', data, function(resp){
            if(resp.success){
                refreshLotteryAward(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('#query_btn').on('click', function(){
        lottery_award_name = $('input[name="sign_name"]').val();
        queryLotteryAward(lottery_award_name);
    });*/


    function delLotteryAward(lottery_award_id){
        swal({
            title: "删除确认",
            text: "确定删除该奖品？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'lottery_award_id': lottery_award_id,
            });
//            alert(data);
            $.post('/mana_app/lottery/award/rule/delete/', data, function(resp){
                if(resp.success){
                    refreshLotteryAward(resp.html);
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }

    function addLotteryAward(data) {
        $.post('/mana_app/lottery/award/rule/add/', data, function(resp){
            if(resp.success){
                $('#lottery_award_modal').modal('hide');
                refreshLotteryAward(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }

    $('#add_lottery_award_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#lottery_award_modal_form')[0].reset();
        $('#lottery_award_modal').find('.modal-title').text('新增奖品');

        $('#lottery_award_modal_submit').off('click').on('click', function(){
            if(!$('#lottery_award_modal_form').valid()) return false;

            data = $('#lottery_award_modal_form').serializeForm();
            addLotteryAward(JSON.stringify(data));
        });
    });

    $('input[name="delete_lottery_award"]').on('click', function(){
        lottery_award_id = $(this).parents('tr').attr('lottery_award_id');
        console.log(lottery_award_id);
        delLotteryAward(lottery_award_id);
    });

    function initUpdateLotteryAward(){
        function set_optional(update_btn, field){
            var name = update_btn.parents('tr').find('td[field="' + field + '"]').text()
            $('#lottery_award_modal').find('select[name="' + field + '"] > option').each(function(idx, ele){
                if($(ele).text() == name){
                    $(ele).prop('selected', true);
                }
            });
        }
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#lottery_award_modal_form')[0].reset();
        var update_btn = $(this);

        $('#lottery_award_modal').find('.modal-title').text('更新抽奖奖品');
        $('#lottery_award_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        set_optional(update_btn, 'busitype');
        set_optional(update_btn, 'coupon');
        $('#lottery_award_modal_submit').off('click').on('click', function(){
            if(!$('#lottery_award_modal_form').valid()) return false;
            data = $('#lottery_award_modal_form').serializeForm();
            data['lottery_award_id'] = update_btn.parents('tr').attr('lottery_award_id');
            updateLotteryAward(JSON.stringify(data));
        });
        $('#lottery_award_modal').modal('show');
    }
    function updateLotteryAward(data){
        $.post('/mana_app/lottery/award/rule/update/', data, function(resp){
            if(resp.success){
                $('#lottery_award_modal').modal('hide');
                refreshLotteryAward(resp.html);
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update_lottery_award"]').on('click', initUpdateLotteryAward);

    function refreshLotteryAward(html){
        $('tbody').html(html);
        $('input[name="delete_lottery_award"]').on('click', function(){
            lottery_award_id = $(this).parents('tr').attr('lottery_award_id');
            delLotteryAward(lottery_award_id);
        });
        $('input[name="update_lottery_award"]').on('click', initUpdateLotteryAward);
    }

});
