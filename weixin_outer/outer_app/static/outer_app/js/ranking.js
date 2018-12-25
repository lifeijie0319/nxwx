$(function(){
    var now_dt = new Date();
    function getRank(type){
        if(type == 'month'){
            data = {year: now_dt.getFullYear(), month: now_dt.getMonth() + 1}
        }else{
            data = {year: now_dt.getFullYear()}
        }
        $.post(url_pre + '/invitation/ranking/list/', data, function(resp){
            if(type == 'month'){
                $('#tab1').html(resp.html);
            }else{
                $('#tab2').html(resp.html);
            }
        }).error(function(){
            alert('服务器错误');
        });
    }
    getRank('month');
    getRank('year');
});
