$(function(){
    var width = $('#signed_qrcode').width();
    var height = $('#signed_qrcode').width();
    var x = width * 0.4;
    var y = height * 0.4;
    var lw = width * 0.2;
    var lh = height * 0.2;
    $.get(url_pre + '/user/get_user/', function(resp){
        $('.amounted').text('分享人:' + resp.name);
        $('#qrcode').qrcode({
            width: width,
            height: height,
            text: base_url + url_pre + '/invitation/register_pre/?inviter=' + resp.openid,
        });
        var canvas = $('canvas')[0];
        console.log(canvas);
        context = canvas.getContext('2d');
        logo = new Image();
        logo.src = '/static/outer_app/images/invitation/logo.jpg'
        logo.onload = function(){
            context.drawImage(logo, x, y, lw, lh);
            html2canvas($('.payment_content')[0]).then(function(canvas){
                dataURL = canvas.toDataURL('image/png');
                $('.payment_content').html('<img style="width:100%;height:100%" src="' + dataURL + '">')
            });
        }
    }).error(function(){
        alert('服务器错误');
    });
})
