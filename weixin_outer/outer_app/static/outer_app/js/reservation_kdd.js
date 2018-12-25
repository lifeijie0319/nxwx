$(function () {

    /*var house_regions_term;
    var house_properties_term;
    $.get(url_pre + '/reservation/kdd/param/', function(resp){
        console.log(resp);
        house_regions_term = resp.house_regions;
        house_properties_term = resp.house_properties;
    }).error(function(){
        $.toptips('参数获取失败');
    });*/

    $('#form_kdd1').form();
    //var reservation_flag = false;
    $('#kdd_submit1').on('click', function () {
        validateRes = false;
        $('#form_kdd1').validate(function (error) {
            if (error) {
            } else {
                validateRes = true;
            }
        });
        if (!validateRes) return;

        house_property = $('select[name="house_property"]').val();
        if(house_property == '0'){
            $.toptips('房屋性质不能为空');
            return false;
        }
        house_region = $('select[name="house_region"]').val();
        if(house_region == '0'){
            $.toptips('房屋坐落地址不能为空');
            return false;
        }

        //if($.inArray(house_property, house_properties_term) != -1 && $.inArray(house_region, house_regions_term) != -1){
            kdd_data = JSON.parse($('#form_kdd1').serializeForm());
            if(kdd_data.house_property == '住宅'){
                $('#location_label').text('小区名称');
                $('#is_villa_switch').show();
            }else{
                $('#location_label').text('房屋地址');
                $('#is_villa_switch').hide();
            }
            //localStorage.setItem('kdd_data', kdd_data);
            $('#page_kdd2').popup();
            //window.location.href = url_pre + '/staticfile/reservation_kdd2/';
            //return false;
        //}
        /*if(reservation_flag) return false;
        reservation_flag = true;
        $.toptips('申请正在提交，请稍候', 'success');
        $.ajax({
            url: url_pre + '/reservation/kdd/submit/',
            type: 'post',
            contentType: 'application/json; charset=utf-8',
            data: $('#form_kdd1').serializeForm(),
            dataType: 'json',
            success: function (resp) {
                //console.log(resp)
                if (resp.success) {
                    window.location.href = url_pre + '/staticfile/done/?from=reservation&type=kdd1';
                } else {
                    reservation_flag = false;
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                reservation_flag = false;
                $.toptips('服务器错误');
            }
        });*/
    });

    /*kdd_data = JSON.parse(localStorage.getItem('kdd_data'));
    console.log(typeof kdd_data);
    if(!kdd_data){
        window.history.back();
    }else if(kdd_data.house_property == '住宅'){
        $('#location_label').text('小区名称');
        $('#is_villa').show();
    }
    console.log(kdd_data.house_property);*/

    var community_price;
    $('input[name="house_location"]').autocomplete({
        //minChars: 2,
        noCache: true,
        serviceUrl: url_pre + '/reservation/kdd/search/',
        onSelect: function(suggestion){
            community_price = parseInt(suggestion.data);
            console.log(suggestion);
            //$('#search_page').hide();
        },
        onSearchComplete: function(){
            community_price = 0;
            console.log(community_price);
            //$(this).autocomplete('disable');
        },
        showNoSuggestionNotice: true,
        noSuggestionNotice: '抱歉，没有匹配项',
    })/*.autocomplete('disable').on('keydown', function(e){
        if(e.keyCode == 13){
            console.log('search');
            $(this).autocomplete('clear').autocomplete('enable');
        }
    });*/
    $('#form_kdd2').form();
    var reservation_flag = false;
    $('#kdd_submit2').on('click', function(){
        validateRes = false;
        $('#form_kdd2').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if (!validateRes) return;
        branch_id = $('select[name="branch"]').val();
        if(branch_id == '0'){
            $.toptips('网点不能为空');
            return false;
        }

        var append_data = JSON.parse($('#form_kdd2').serializeForm());
        console.log(append_data);
        $.extend(kdd_data, append_data);
        kdd_data.is_villa = $('input[name="is_villa"]').prop('checked');
        if(community_price){
            var factor = 1;
            if(kdd_data.is_villa){
                factor = 1.3;
            }
            kdd_data.assess_price = community_price * 0.01 * parseInt(append_data.house_area) * 0.7 * factor;
            kdd_data.assess_price = kdd_data.assess_price.toFixed(2)
        }else{
            delete kdd_data.assess_price;
        }
        console.log(kdd_data);

        if(reservation_flag) return false;
        reservation_flag = true;
        $.toptips('申请正在提交，请稍候', 'success');
        $.ajax({
            url: url_pre + '/reservation/kdd/submit/',
            type: 'post',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(kdd_data),
            dataType: 'json',
            success: function (resp) {
                //console.log(resp)
                if (resp.success) {
                    var args = '&type=kdd1';
                    if(community_price){
                        args = '&type=kdd2&price=' + Math.round(kdd_data.assess_price);
                    }
                    window.location.href = url_pre + '/staticfile/done/?from=reservation' + args;
                } else {
                    reservation_flag = false;
                    $.toptips(resp.msg);
                }
            },
            error: function () {
                reservation_flag = false;
                $.toptips('服务器错误');
            }
        });
    });

});
