$(function(){
    var ITEM_ON = "nav_active";

    var showTab = function (a) {
        var $a = $(a);
        if ($a.hasClass(ITEM_ON)) return;
        var href = $a.attr("href");

        if (!/^#/.test(href)) return;

        $a.parent().find("." + ITEM_ON).removeClass(ITEM_ON);
        $a.addClass(ITEM_ON);

        var bd = $a.parents(".container").find(".ys_tab");

        bd.find(".tab_active").removeClass("tab_active");

        $(href).addClass("tab_active");
    }

    $.showTab = showTab;

    $(document).on("click", ".ys_navbar_item, .weui-tabbar__item", function (e) {
        var $a = $(e.currentTarget);
        var href = $a.attr("href");
        if ($a.hasClass(ITEM_ON)) return;
        if (!/^#/.test(href)) return;

        e.preventDefault();

        showTab($a);
    });

    var page1 = 1;
    var page2 = 1;
    var loading_flag = false;
    var no_data_tips = '<div class="ys_loadmore ys_loadmore_line"> <span class="ys_more_tips">暂无数据</span></div>'
    var no_more_tips = '<div id="credits_history_nomore" class="nomore">没有更多了</div>'
    function load_more(st, page){
        var data = {
            st: st,
            page: page,
        }
        $('#loading').show();
        $.get(url_pre + '/reservation/deal/list/', data, function(resp){
            //console.log(resp.page, typeof resp.page);
            if(st == '未受理'){
                $('#tab1').append(resp.html);
                if(page1 == 1){
                    if(!resp.html){
                        $("#tab1").html(no_data_tips);
                    }else if(resp.page == -1){
                        $("#tab1").append(no_more_tips);
                        page1 = -1;
                    }
                }else if(resp.page == -1){
                    $("#tab1").append(no_more_tips);
                    page1 = -1;
                }
            }else{
                page2 = resp.page;
                $('#tab2').append(resp.html);
                if(page2 == 1){
                    if(!resp.html){
                        $("#tab2").html(no_data_tips);
                    }else if(resp.page == -1){
                        $("#tab2").append(no_more_tips);
                        page2 = -1;
                    }
                }else if(resp.page == -1){
                    $("#tab2").append(no_more_tips);
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
    load_more('未受理', page1);
    load_more('已受理', page2);

    $(window).on('scroll', function(){
        //console.log(loading_flag);
        var scrollTop = $(this).scrollTop();               //滚动条距离顶部的高度
        var scrollHeight = $(document).height();           //当前页面的总高度
        var windowHeight = $(this).height();               //当前可视的页面高度

        if(scrollTop + windowHeight >= scrollHeight && !loading_flag){        //距离顶部+当前高度 >=文档总高度 即代表滑动到底部
            loading_flag = true;
            var st = $('a.nav_active').text();
            //console.log(page1, page2, typeof page1)
            if(st == '未受理' && page1 != -1){
                page1 += 1;
                //console.log(page1, typeof page1);
                load_more(st, page1);
            }else if(st == '已受理' && page2 != -1){
                page2 += 1;
                load_more(st, page2);
            }else{
                loading_flag = false;
            }
        }
    });

    var reservation_deal_flag = false;
    $('#tab1').on('click', 'input[orderno]', function(){
        orderno = $(this).attr('orderno');
        data = {
            orderno: $(this).attr('orderno'),
        }
        $.confirm('确定要处理该预约申请？', '预约申请处理确认', function(){
            if(reservation_deal_flag) return false;
            reservation_deal_flag = true;
            $.toptips('正在处理', 'success');
            $.post(url_pre+ '/reservation/deal/submit/', data, function(resp){
                //console.log(resp)
                if(resp.success){
                    window.location.reload();
                }else{
                    reservation_deal_flag = false;
                    $.toptips(resp.msg);
                }
            }).error(function(){
                $.toptips('服务器错误');
                reservation_deal_flag = false;
            });
        },function(){
        });
    });
});
