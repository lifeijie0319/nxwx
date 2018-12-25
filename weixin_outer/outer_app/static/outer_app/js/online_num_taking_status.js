$(function(){
    var page1 = 1;
    var page2 = 1;
    var loading_flag = false;
    var no_data_tips = '<div class="ys_loadmore ys_loadmore_line"> <span class="ys_more_tips">暂无数据</span> </div>'
    var no_more_tips = '<div id="credits_history_nomore" class="nomore">没有更多了</div>'
    function load_more(st, page){
        var data = {
            st: st,
            page: page,
        }
        $('#loading').show();
        $.get(url_pre + '/online/num/taking/status/list/', data, function(resp){
            console.log(resp.page, (resp.html));
            if(st == '未完成'){
                $('#tab1').append(resp.html);
                if(page1 == 1){
                    if(!resp.html){
                        $('#tab1').html(no_data_tips);
                    }else if(resp.page == -1){
                        $('#tab1').append(no_more_tips);
                        page1 = -1;
                    }
                }else if(resp.page == -1){
                    $('#tab1').append(no_more_tips);
                    page1 = -1;
                }
            }else{
                $('#tab2').append(resp.html);
                if(page2 == 1){
                    if(!resp.html){
                        $('#tab2').html(no_data_tips);
                    }else if(resp.page == -1){
                        $('#tab2').append(no_more_tips);
                        page2 = -1;
                    }
                }else if(resp.page == -1){
                    $('#tab2').append(no_more_tips);    
                    page2 = -1;
                }
            }
            loading_flag = false;
             $('#loading').hide();
        }).error(function(){
            loading_flag = false
            $.toptips('服务器错误');
             $('#loading').hide();
        });
    }
    load_more('未完成', page1);
    load_more('已完成', page2);

    $(window).on('scroll', function(){
        console.log(loading_flag);
        var scrollTop = $(this).scrollTop();               //滚动条距离顶部的高度
        var scrollHeight = $(document).height();           //当前页面的总高度
        var windowHeight = $(this).height();               //当前可视的页面高度

        if(scrollTop + windowHeight >= scrollHeight && !loading_flag){        //距离顶部+当前高度 >=文档总高度 即代表滑动到底部
            loading_flag = true;
            var st = $('a.nav_active').text();
            console.log(page1, page2, typeof page1)
            if(st == '未完成' && page1 != -1){
                page1 += 1;
                console.log(page1, typeof page1);
                load_more(st, page1);
            }else if(st == '已完成' && page2 != -1){
                page2 += 1;
                load_more(st, page2);
            }else{
                loading_flag = false;
            }
        }
    });

});
