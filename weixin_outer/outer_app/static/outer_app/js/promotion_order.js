$(function(){

    $('#minus').on('click', function(){
        num = parseInt($('#real_num').text());
        if(num == 1){
            $.toptips('已经是最小购买数量了');
            return false;            
        }else if(num > 1){
            num -= 1;
            $('#real_num').text(num);
            $('#input_num').val(num);
            price = parseInt($('#price').text());
            sum = num * price;
            //console.log(sum);
            $('#sum').text(sum);
            originCredits = parseInt($('#my_credits').text());
            currentCredits = originCredits + price;
            $('#my_credits').text(currentCredits);
        }
    })

    $('#plus').on('click', function(){
        price = parseInt($('#price').text())
        creditsLeft = parseInt($('#my_credits').text())
        //console.log(price);
        //console.log(creditsLeft);
        if(price > creditsLeft){
            $.toptips('您的积分不足');
            return false;
        }else{
            $('#perchase').removeClass('disable');
            num = parseInt($('#real_num').text());
            //console.log(typeof num)
            //console.log(num)
            num += 1;
            $('#input_num').val(num);
            $('#real_num').text(num);
            sum = num * price;
            $('#sum').text(sum);
            originCredits = parseInt($('#my_credits').text());
            currentCredits = originCredits - price;
            $('#my_credits').text(currentCredits);
        }
    }).trigger('click');

    $('#input_num').on('keyup paste', function(){
        $(this).val($(this).val().replace('/[^1-9]/g', ''));
    }).on('blur', function(){
        price = parseInt($('#price').text());
        totalCredits = parseInt($('#my_credits').text()) + parseInt($('#sum').text());
        num = parseInt($(this).val());
        //console.log(num);
        if(Number.isNaN(num) || num == 0){
            $.toptips('您的输入不正确');
            num = 1;
        }else if(num * price > totalCredits){
            $.toptips('您的积分不足');
            num = parseInt(totalCredits / price);
        }
        $(this).val(num);
        $('#real_num').text(num);
        sum = num * price;
        $('#sum').text(sum);
        $('#my_credits').text(totalCredits-sum);
    });

    var purchase_flag = false;
    $('#purchase').on('click', function(){
        num = parseInt($('#real_num').text())
        name = $('#name').text()
        currentCredits = parseInt($('#my_credits').text());
        $.confirm('您将要购买' + name + num + '张，请确认。一经购买，无法退回。', '优惠券购买确认', function(){
            if(purchase_flag) return false;
            purchase_flag = true;
            $.toptips('正在提交购买申请', 'success');
            data = {
                id: get_url_args('id'),
                num: num,
                currentCredits: currentCredits,
                req_token: $('#req_token').text(),
            }
            $.post(url_pre + '/promotion/purchase/', data, function(resp){
                //console.log(resp)
                purchase_flag = false;
                if(resp.success){
                    //$('#req_token').text(resp.req_token);
                    window.location.href = url_pre + '/staticfile/done/?from=promotion_order';
                }else{
                    $.toptips(resp.msg);
                }
            }).error(function(){
                $.toptips('服务器错误');
            });
        },function(){
        });
    })

});
