$(function(){
    $('#form').form();
    poundage_low = parseFloat($('input[name="poundage"]').val());
    poundage_high = $('input[name="poundage"]').attr('poundage_high');
    //console.log(poundage_low, poundage_high)
    $('input[name="receipt_provision"]').on('change', function(){
        checked = $(this).prop('checked');
        if(checked){
            $('input[name="poundage"]').val(poundage_low);
        }else{
            $('input[name="poundage"]').val(poundage_high);
        }
        $('input[name="credits"]').trigger('blur');
    });
    ratio = parseInt($('input[name="ratio"]').val().split(':')[0]);
    //console.log(ratio);
    $('input[name="credits"]').on('keyup blur', function(){
        poundage = parseFloat($('input[name="poundage"]').val());
        credits = parseInt($(this).val())
        //console.log(credits);
        if(isNaN(credits)){
            balance = 0;
        }else{
            balance = Math.round(credits*(1-poundage)/ratio*100)/100;
        }
        //console.log(balance);
        $('input[name="balance"]').val(balance);
    });
    var withdraw_apply_flag = false;
    $('#submit').on('click', function(){
        validateRes = false;
        $('#form').validate(function(error){
            if(error){
            }else{      
                validateRes = true;
            }
        });
        if(!validateRes) return false;
        balance = parseFloat($('input[name="balance"]').val());
        var min_balance = parseInt($('input[name="min_balance"]:hidden').val());
        if(balance < min_balance){
            $.toptips('提现金额太少，请至少累积到' + min_balance + '元');
            return false;
        }
        data = {
            credits: $('input[name="credits"]').val(),
            receiptProvision: $('input[name="receipt_provision"]').val(),
            poundage: parseFloat($('input[name="poundage"]').val()),
            ratio: ratio,
            balance: $('input[name="balance"]').val()
        }
        $.confirm('您确定要提现积分' + $('input[name="credits"]').val() + '?', "提现申请确认", function() {
            if(withdraw_apply_flag) return false;
            withdraw_apply_flag = true;
            $.toptips('正在提交，请稍后', 'success');
            $.post(url_pre + '/seller/withdraw_apply/', data, function(resp){
                withdraw_apply_flag = false;
                if(resp.success){
                    window.location.href = url_pre + '/staticfile/done/?from=withdraw_apply';
                }else{
                    $.toptips(resp.msg);
                }
            }).error(function(){
                $.toptips('服务器错误');
            });
        }, function() {
          //取消操作
        }); 
    });
});
