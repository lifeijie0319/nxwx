$(function(){
    //轮播图
    $('#slide').swipeSlide({
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

    //更新积分数据
    credits = parseInt($('#credits').text());
    timestamp = new Date().getTime();
    $.get(url_pre + '/user/get_user/?v=' + timestamp, function(resp){
        console.log(credits, resp.credits);
        if(resp.credits != credits){
            $('#credits').text(resp.credits);
        }
    });
});
