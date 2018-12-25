$(function(){
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
        id = get_url_args('id')
        wx.onMenuShareAppMessage({
            title: '南浔银行',
            desc: '优惠券推广赚积分',
            link: base_url + url_pre + '/invitation/coupon_pre/?id=' + id + '&inviter=' + localStorage.getItem('openid'),
            imgUrl: base_url + url_pre + '/static/outer_app/images/logox.png',
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
            title: '南浔银行', // 分享标题
            link: base_url + url_pre + '/invitation/coupon_pre/?id=' + id + '&inviter=' + localStorage.getItem('openid'),
            imgUrl: base_url + url_pre + '/static/outer_app/images/logox.png', // 分享图标
            success: function () {
                $.toptips('分享成功', 'success');
            },
            cancel: function () {
                $.toptips('取消分享');
            }
        });
    });

    $('#promotion_slide').swipeSlide({
        autoSwipe:true,//自动切换默认是
        speed:4000,//速度默认4000
        continuousScroll:true,//默认否
        transitionType:'cubic-bezier(0.22, 0.69, 0.72, 0.88)',//过渡动画linear/ease/ease-in/ease-out/ease-in-out/cubic-bezier
        lazyLoad:true,//懒加载默认否
        firstCallback : function(i,sum,me){
            me.find('.dot').children().first().addClass('cur');
        },
        callback : function(i,sum,me){
            me.find('.dot').children().eq(i).addClass('cur').siblings().removeClass('cur');
        }
    });

    $('#order').on('click', function(){
        id = get_url_args('id');
        $.get(url_pre + '/promotion/details/order_term_check/?coupon_id=' + id, function(resp){
            if(resp.success){
                window.location.href = url_pre + '/promotion/order/page/?id=' + id;
            }else{
                $.alert(resp.msg);
            }
        });
    });
    $('a.share_btn').on('click', function(){
        $('.share').fadeIn();
    });
});
