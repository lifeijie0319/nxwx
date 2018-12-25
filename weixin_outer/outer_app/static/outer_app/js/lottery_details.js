$(function(){

    type = get_url_args('type');
    $.get(url_pre + '/credits/history/page/?type=' + type, function(resp){
        $('#credits_history_list').append(resp);
        id = $('#last_id').text();
        if($('#credits_history_list > a.ys_item_media').length == 0){
            $('#credits_history_empty').show();
        }else if(id == -1){
            $('#credits_history_nomore').show();
        }
        $('input:hidden').val(id);
        $('#last_id').remove();
    });

    $(window).scroll(function(){
        var scrollTop = $(this).scrollTop();               //滚动条距离顶部的高度
        var scrollHeight = $(document).height();           //当前页面的总高度
        var windowHeight = $(this).height();               //当前可视的页面高度

        if(scrollTop + windowHeight >= scrollHeight){        //距离顶部+当前高度 >=文档总高度 即代表滑动到底部
            last = parseInt($('input:hidden').val());
            if(last == -1){
                return false;
            }
            $('#loading').show();
            $.get(url_pre + '/credits/history/page/?type=' + type + '&last=' + last, function(resp){
                console.log(resp);
                $('#credits_history_list').append(resp);
                idEle = $('#last_id').remove();
                id = parseInt(idEle.text());
                console.log(id);
                if(id == -1){
                    $('#credits_history_nomore').show();
                }
                $('input:hidden').val(id);
                $('#loading').hide();
            });
        }
    });
});
