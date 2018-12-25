function check_time(timePicker) {
    console.log("success");
    $.get(url_pre + '/time/data/', function(resp){
        //获取系统日期后进行时间判定，如果时间大于选中的时间，则排除。
                console.log(resp);
                alert(timePicker.val());
            });
}
