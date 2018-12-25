$(function(){

    var type = get_url_args('type');
    $.get(url_pre + '/credits/history/page/?type=' + type, function(resp){
        $('#credits_history_list').append(resp);
        id = $('#last_id').text();
        if($('#credits_history_list > a.ys_item_media').length == 0){
            $('#loading').replaceWith('\
                <div id="credits_history_empty" class="ys_loadmore ys_loadmore_line">\
                    <span class="ys_more_tips">您还未有积分明细</span>\
                </div>');
            //$('#credits_history_empty').show();
        }else if(id == -1){
            $('#loading').replaceWith('<div id="credits_history_nomore" class="nomore">没有更多了</div>');
            //$('#credits_history_nomore').show();
        }
        $('input:hidden').val(id);
        $('#last_id').remove();
    });

    var loading_flag = true;
    $(window).scroll(function(){
        var scrollTop = $(this).scrollTop();               //滚动条距离顶部的高度
        var scrollHeight = $(document).height();           //当前页面的总高度
        var windowHeight = $(this).height();               //当前可视的页面高度

        if(scrollTop + windowHeight >= scrollHeight && loading_flag){        //距离顶部+当前高度 >=文档总高度 即代表滑动到底部
            loading_flag = false;
            last = parseInt($('input:hidden').val());
            if(last == -1){
                return false;
            }
            //$('#loading').show();
            $.get(url_pre + '/credits/history/page/?type=' + type + '&last=' + last, function(resp){
                setTimeout(function(){
                    console.log(resp);
                    $('#credits_history_list').append(resp);
                    idEle = $('#last_id').remove();
                    id = parseInt(idEle.text());
                    console.log(id);
                    if(id == -1){
                        $('#loading').replaceWith('<div id="credits_history_nomore" class="nomore">没有更多了</div>');
                        //$('#credits_history_nomore').show();
                    }
                    $('input:hidden').val(id);
                    loading_flag = true;
                    //$('#loading').hide();
                }, 500);
            }).error(function(){
                loading_flag = true;
            });
        }
    });
});
