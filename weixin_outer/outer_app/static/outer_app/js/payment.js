$(function(){
    //初始化二维码
    timestamp = new Date().getTime();
    $.get(url_pre + '/common/get_qrcode_str/?v=' + timestamp, {qrcodeId: '00000000'}, function(resp){
        var qrcode = new QRCode($('#qrcode')[0], {
            text: resp.qrcode_str,
            width : 160,//设置宽高
            height : 160,
            correctLevel: QRCode.CorrectLevel.L
        });
        //建立ws连接并监听后台消息
        openid = resp.openid;
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        socket = new ReconnectingWebSocket(ws_scheme + "://" + window.location.host + "/ws/" + openid);
        socket.onopen = function(e){
            console.log('websocket连接建立');
        }
        socket.onmessage = function(e) {
            console.log(e.data);
            window.location.href = url_pre + '/credits/trade_reply/?id=' + e.data;
        }
        socket.onerror = function(e){
            console.log('websocket连接失败');
        }
    });
});
