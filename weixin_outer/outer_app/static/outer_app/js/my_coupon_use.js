$(function(){
    //初始化二维码
    user_coupon_id = get_url_args('user_coupon_id');
    data = {
        qrcodeId: '00000003',
        userCouponId: user_coupon_id,
    }
    timestamp = new Date().getTime();
    $.get(url_pre + '/common/get_qrcode_str/?v=' + timestamp, data, function(resp){
        console.log(resp.qrcode_str.length);
        var qrcode = new QRCode($('#qrcode')[0], {
            text: resp.qrcode_str,
            width : 160,//设置宽高
            height : 160,
            correctLevel: QRCode.CorrectLevel.L,
        });
        openid = resp.openid;
        //建立ws连接并监听返回消息
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        socket = new ReconnectingWebSocket(ws_scheme + "://" + window.location.host + "/ws/" + openid);
        socket.onopen = function(e){
            console.log('websocket连接建立');
        }
        socket.onmessage = function(e) {
            console.log(e.data);
            window.location.href = url_pre + '/coupon/trade_reply/?user_log_id=' + e.data;
        }
        socket.onerror = function(e){
            console.log('websocket连接失败');
        }
    });
});
