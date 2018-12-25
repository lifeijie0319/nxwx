$(function(){
    var qrcode;
    //初始化二维码
    qrcodeId = get_url_args('qrcodeId');
    timestamp = new Date().getTime();
    $.get(url_pre + '/common/get_qrcode_str/?v=' + timestamp, {qrcodeId: qrcodeId}, function(resp){
        qrcode = new QRCode($('#receipt_qrcode')[0], {
            text: resp.qrcode_str,
            width : 160,//设置宽高
            height : 160,
            correctLevel: QRCode.CorrectLevel.L
        });
        openid = resp.openid;
        //ws连接建立并监听返回
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        socket = new ReconnectingWebSocket(ws_scheme + "://" + window.location.host + "/ws/" + openid);
        socket.onopen = function(e){
            console.log('websocket连接建立');
        }
        socket.onmessage = function(e) {
            console.log(e.data);
            window.location.href = url_pre + '/credits/trade_reply/?id=' + e.data;
        }
    });

    //初始化设置金额表单验证
    $('#set_amount_form').form();
    $('#credits_set_amount').on('click', function(){
        $('#page_set_amount').popup();
    });
    $('#set_amount_submit').on('click', function(){
        validateRes = false;
        $('#set_amount_form').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if(validateRes == false) return false;
        amount = $('#set_amount_amount').val();
        $('#receipt_credits > span').text(amount);
        $('#receipt_credits').show();
        data = {
            qrcodeId: qrcodeId,
            amount: amount,
        }
        $.get(url_pre + '/common/get_qrcode_str/', data, function(resp){
            qrcode.makeCode(resp.qrcode_str);
            $.closePopup();
        });
    });
});
