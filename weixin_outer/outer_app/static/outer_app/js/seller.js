$(function(){
    //设置openid
    if(!localStorage.getItem('openid')){
        $.get(url_pre + '/common/fetch_openid/', function(resp){
            localStorage.setItem('openid', resp.openid);
        });
    }
    $('#set_amount_form').form();

    //更新商户积分数据
    credits = parseInt($('#credits').text());
    timestamp = new Date().getTime();
    $.get(url_pre + '/seller/info/?v=' + timestamp, function(resp){
        //console.log(credits, resp.credits);
        if(resp.credits != credits){
            $('#credits').html(resp.credits + '<span>积分</span>');
        }
    });

    //jssdk
    $.ajax({
        url : url_pre + "/wx/jssdk/",
        type : 'post',
        contentType: "application/json; charset=utf-8",
        dataType : 'json',
        data : JSON.stringify({
            'url': window.location.href,
        }),
        success : function(resp) {
            if(resp.success){
                resp = resp.config;
                wx.config({
                    debug : false,
                    appId : APPID,
                    timestamp : resp.timestamp,
                    nonceStr : resp.nonceStr,
                    signature : resp.signature,
                    jsApiList : ['scanQRCode']
                });
            }else{
                console.log(resp.msg);
            }
        },
        error : function(){
            console.log('error1');
        }
    });

    var trade_flag = false;
    $('#scan').on('click', function(){
        wx.scanQRCode({
            needResult: 1, // 默认为0，扫描结果由微信处理，1则直接返回扫描结果，
            scanType: ["qrCode"], // 可以指定扫二维码还是一维码，默认二者都有
            success: function (res){
                $.toptips('正在处理数据，请等待', 'success');
                result = res.resultStr;
                //alert(result)
                $.post(url_pre + '/seller/parse_qrcode_str/', {qrcodeStr: result}, function(resp){
                    var req_token = $('#req_token').text();
                    if(resp.success){
                        if(resp.msg == 'coupon_set_amount'){
                            $('#set_amount_submit').on('click', function(){
                                validateRes = false;
                                $('#set_amount_form').validate(function (error) {
                                    if (error) {
                                    } else {
                                        validateRes = true;
                                    }
                                });
                                if(validateRes == false) return false;
                                amount = $('#set_amount_input').val();
                                data = {
                                    qrcodeStr: result,
                                    amount: amount,
                                    req_token: req_token,
                                }
                                if(trade_flag) return false;
                                trade_flag = true;
                                $.toptips('交易中。。。', 'success');
                                $.post(url_pre + '/coupon/trade/', data, function(resp){
                                    if(resp.success){
                                        //$('#req_token').text(resp.req_token);
                                        args = '?seller_log_id=' + resp.seller_log_id;
                                        window.location.href = url_pre + '/coupon/trade_reply/' + args;
                                    }else{
                                        trade_flag = false;
                                        $.toptips(resp.msg);
                                    }
                                })
                                .error(function(){
                                    console.log('error');
                                });
                            });
                            $('#set_amount_tips').text(resp.tips);
                            $('#set_amount_img').attr('src', resp.img_path);
                            $('#page_set_amount').popup();
                        }else if(resp.msg == 'coupon_confirm'){
                            $('#show_amount_submit').on('click', function(){
                                data = {
                                    qrcodeStr: result,
                                    amount: resp.amount,
                                    req_token: req_token,
                                }
                                if(trade_flag) return false;
                                trade_flag = true;
                                $.toptips('交易中。。。', 'success');
                                $.post(url_pre + '/coupon/trade/', data, function(resp){
                                    if(resp.success){
                                        //$('#req_token').text(resp.req_token);
                                        args = '?seller_log_id=' + resp.seller_log_id;
                                        window.location.href = url_pre + '/coupon/trade_reply/' + args;
                                    }else{
                                        trade_flag = false;
                                        $.toptips(resp.msg);
                                    }
                                })
                                .error(function(){
                                    console.log('error');
                                });
                            });
                            $('#show_amount_tips').text(resp.tips);
                            $('#show_amount_credits').text(resp.amount);
                            $('#show_amount_img').attr('src', resp.img_path);
                            $('#page_show_amount').popup();
                        }else if(resp.msg == 'set_amount'){
                            $('#set_amount_submit').on('click', function(){
                                validateRes = false;
                                $('#set_amount_form').validate(function (error) {
                                    if (error) {
                                    } else {
                                        validateRes = true;
                                    }
                                });
                                if(validateRes == false) return false;
                                amount = $('#set_amount_input').val();
                                data = {
                                    qrcodeStr: result,
                                    amount: amount,
                                    req_token: req_token,
                                }
                                if(trade_flag) return false;
                                trade_flag = true;
                                $.toptips('交易中。。。', 'success');
                                $.post(url_pre + '/credits/trade/', data, function(resp){
                                    if(resp.success){
                                        //$('#req_token').text(resp.req_token);
                                        window.location.href = url_pre + '/credits/trade_reply/?from=scan&id=' + resp.log_id;
                                    }else{
                                        trade_flag = false;
                                        $.toptips(resp.msg);
                                    }
                                }).error(function(){
                                    console.log('error');
                                });
                            });
                            $('#set_amount_tips').text(resp.tips);
                            $('#set_amount_img').attr('src', resp.img_path);
                            $('#page_set_amount').popup();
                        }
                    }else{
                        $.toptips(resp.msg);
                    }
                });
            }
        });
    });

});
