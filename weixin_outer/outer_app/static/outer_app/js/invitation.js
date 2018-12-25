$(function(){
    $('#share_btn').on('click', function(){
        $('.share').fadeIn();
    });

    $.ajax({
        url : url_pre + '/wx/jssdk/',
        type : 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType : 'json',
        data : JSON.stringify({
            'url': window.location.href,
            //'csrfmiddlewaretoken': localStorage.getItem('csrftoken')
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
                    jsApiList : ['onMenuShareTimeline','onMenuShareAppMessage']
                });
            }else{
                console.log(resp.msg);
            }
        },
        error : function(xhr, textStatus, errorThrown){
            alert(xhr.status);
            alert(xhr.readyState);
            alert(textStatus);
        }
    })

    wx.ready(function(){
        wx.onMenuShareAppMessage({
            title: '南浔银行年度大礼——丰收之果，诚意奉上！',
            desc: '现在邀请好友注册，即刻获得果果好礼！',
            link: base_url + url_pre + '/invitation/register_pre/?inviter=' + localStorage.getItem('openid'),
            imgUrl: base_url + '/static/outer_app/images/logox.png',
            type: '',
            dataUrl: '',
            success: function () {
                $.toptips('分享成功', 'success');
            },
            cancel: function () {
                $.toptips('取消分享');
            },
        });
        wx.onMenuShareTimeline({
            title: '南浔银行年度大礼——丰收之果，诚意奉上！', // 分享标题
            link: base_url + url_pre + '/invitation/register_pre/?inviter=' + localStorage.getItem('openid'),
            imgUrl: base_url + '/static/outer_app/images/logox.png', // 分享图标
            success: function () {
                $.toptips('分享成功', 'success');
            },
            cancel: function () { 
                $.toptips('取消分享');
            }
        });
    });

});
