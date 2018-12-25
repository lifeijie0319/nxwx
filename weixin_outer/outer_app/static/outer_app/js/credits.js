$(function(){
    //FastClick
    FastClick.attach(document.body);

    //样式处理
    var newRem = function() {
        var html = document.documentElement;
        html.style.fontSize = html.getBoundingClientRect().width / 10 + 'px';
    };
    window.addEventListener('resize', newRem, false);
    newRem();

    //表单验证初始化
    $('#set_amount_form').form();

    //密码键盘初始化
    var createdDiv = $('#password_keyboard_area').create_password_keyboard();

    //更新积分数据，设置openid
    credits = parseInt($('#credits').text());
    timestamp = new Date().getTime();
    $.get(url_pre + '/user/get_user/?v=' + timestamp, function(resp){
        //console.log(credits, resp.credits);
        if(resp.credits != credits){
            $('#credits').html(resp.credits + '<span>积分</span>');
        }
        if(localStorage.getItem('openid') != resp.openid){
            localStorage.setItem('openid', resp.openid);
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
                data = resp.config;
                wx.config({ 
                    debug : false,
                    appId : APPID,
                    timestamp : data.timestamp,
                    nonceStr : data.nonceStr,
                    signature : data.signature,
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
    //扫一扫
    $('#credits_scan').on('click', function(){
        wx.scanQRCode({
            needResult: 1, // 默认为0，扫描结果由微信处理，1则直接返回扫描结果，
            scanType: ["qrCode","barCode"], // 可以指定扫二维码还是一维码，默认二者都有
            success: function (res){
                result = res.resultStr;
                //result = 'YSWB000100000002JSON{"qrcodeOpenid":"oSDTiwp0mFH9R36n3tBPnO1fqEIw"}';
                //alert(result)
                openid = localStorage.getItem('openid');
                $.post(url_pre + '/user/parse_qrcode_str/', {qrcodeStr: result}, function(resp){
                    req_token = $('#req_token').text();
                    if(resp.msg == 'set_amount'){
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
                            trade(data);
                        });
                        $('#set_amount_tips').text(resp.tips);
                        $('#set_amount_img').attr('src', resp.img_path);
                        $('#page_credits').hide();
                        $('#page_set_amount').popup();
                    }else if(resp.msg == 'confirm'){
                        $('#show_amount_credits').text(resp.amount)
                        $('#show_amount_submit').on('click', function(){
                            data = {
                                qrcodeStr: result,
                                req_token: req_token,
                            }
                            trade(data);
                        });
                        $('#show_amount_tips').text(resp.tips);
                        $('#show_amount_img').attr('src', resp.img_path);
                        $('#page_credits').hide();
                        $('#page_show_amount').popup();
                    }else{
                        $.toptips(resp.msg);
                    }
                });
            }
        });
    });

    function trade(data){
        if(trade_flag) return false;
        trade_flag = true;
        function trade_apply(data){
            $.toptips('交易中。。。', 'success');
            $.post(url_pre + '/credits/trade/', data, function(resp){
                if(resp.success){
                    window.location.href = url_pre + '/credits/trade_reply/?from=scan&id=' + resp.log_id;
                }else{
                    trade_flag = false;
                    $.toptips(resp.msg);
                }
            }).error(function(){
                console.log('error');
            });
        }
        var password;
        $.get(url_pre + '/user/payment_password/fetch/', data, function(resp){
            if(resp.msg == 'need_password'){
                createdDiv.config_password_keyboard(url_pre + '/user/payment_password/verify/', function(){
                    trade_apply(data);
                });
                //console.log(createdDiv);
                createdDiv.addClass('keyboard_wrap_visible');
                $('body').append('<div class="ys_mask ys_mask_visible"></div>');
            }else if(resp.msg == 'complete'){
                trade_apply(data);
            }else{
                trade_flag = false;
                $.toptips(resp.msg);
            }
        })
    }
});
