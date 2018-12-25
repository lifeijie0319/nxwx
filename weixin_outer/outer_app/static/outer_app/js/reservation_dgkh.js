$(function () {

    min_date = new Date().toISOString().split('T');
    $('input[name="due_date"]').attr('min', min_date);
    //获取协议文本
    $.get('/static/outer_app/doc/reservation_dgkh.txt', function(resp){
        //console.log(resp);
        $('#protocol').html('<pre>' + resp + '</pre>');
    });
    $('.ys_agree_clause').on('click', function(){
        $('.ys_fixed_footer').addClass('clause_btn_visible');
    });     
    $('.ys_fixed_footer').on('click', function(){
        $(this).removeClass('clause_btn_visible');
    });

    /*function getNearestBranch(cur_lat, cur_lng){
        var nearest = Number.POSITIVE_INFINITY;
        var branch_id = -1;
        var branch_name;
        $('select[name="branch"] > option').each(function(idx, ele){
            branch_id = $(ele).val();
            if(branch_id){
                branch_lat = $(ele).attr('lat');
                branch_lng = $(ele).attr('lng');
                distance = getDistance(cur_lat, cur_lng, branch_lat, branch_lng);
                //console.log(distance);
                if(distance < nearest){
                    branch_id = $(ele).val();
                    branch_name = $(ele).text();
                }
            }
        });
        $.toptips('最近的网点是' + branch_name, 'success');
        $('select[name="branch"]').val(branch_id);
    }*/
    function getNearestBranch(cur_lat, cur_lng){
        data = {
            lat: cur_lat,
            lng: cur_lng,
        }
        $.get(url_pre + '/reservation/dgkh/nearest_branch/', data, function(resp){
            branch_id = resp.branch_id;
            branch_name = resp.branch_name;
            $.toptips('最近的网点是' + branch_name, 'success');
            $('select[name="branch"]').val(branch_id);
        }).error(function(){
            $.toptips('服务器错误');
        });
    }
    $('#locate').on('click', function(){
        if (!navigator.geolocation){
            $.toptips('该浏览器不支持获取地理位置');
            return false;
        }
        navigator.geolocation.getCurrentPosition(function(position){
            $.toptips('正在计算最近的网点', 'success');
            cur_latitude = position.coords.latitude;
            cur_longitude = position.coords.longitude;
            getNearestBranch(cur_latitude, cur_longitude);
        });
    });

    $('#send_vcode').on('click', function () {
        send_vcode($(this), $('input[name="user_mobile"]'));
    });

    $('#form').form();
    var reservation_flag = false;
    var fail_count = 0;
    $("#submit_btn").on("click", function () {
        validateRes = false;
        $('#form').validate(function (error) {
            if(!error) validateRes = true;
        });
        if (!validateRes) return;
        due_date = $('input[name="due_date"]').val();
        current_date = new Date().toISOString().split('T')[0];
        //console.log(due_date, typeof due_date, current_date, typeof current_date);
        if(due_date < current_date){
            $.toptips('预约日期必须大于等于系统当前日');
            $('input[name="due_date"]').parents(".ys_cell").addClass("color_danger");
            return false;
        }

        if(reservation_flag) return false;
        reservation_flag = true;
        $.toptips('申请正在提交，请稍候', 'success');
        $.ajax({
            url: url_pre + "/reservation/dgkh/submit/",
            type: 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType: 'json',
            success: function (resp) {
                //console.log(resp)
                branch_dom = $('select[name="branch"] > option:checked');
                reservation_dgkh_msg = branch_dom.text() + '网点，联系电话：' + branch_dom.attr('telno');
                if (resp.success) {
                    localStorage.setItem('reservation_dgkh_msg', reservation_dgkh_msg);
                    window.location.href = url_pre + '/staticfile/done/?from=reservation_dgkh&type=success';
                } else {
                    fail_count++;
                    console.log(fail_count);
                    reservation_flag = false;
                    if(fail_count < 3){
                        $.toptips(resp.msg);
                    }else{
                        localStorage.setItem('reservation_dgkh_msg', reservation_dgkh_msg);
                        window.location.href = url_pre + '/staticfile/done/?from=reservation_dgkh&type=fail';
                    }
                }
            },
            error: function () {
                reservation_flag = false;
                $.toptips('服务器错误');
            }
        });
    });

});
