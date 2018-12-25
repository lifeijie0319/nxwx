$(function(){
    $('#form').form();
    //console.log($('input:hidden').val());
    var raw = JSON.parse($('input:hidden').val());
    //console.log(raw)
    $("#address_pcc").cityPicker({
        title: "选择省市区",
    }, [raw]);
    $("#address_pcc").on('change', function(){
        county = $(this).val().split(' ')[2];
        $.post(url_pre + '/address/get_region_json/', {name: county, level: 'village'}, function(resp){
            tvRegion = resp.sub;
            initValue = tvRegion[0].name + ' ' + tvRegion[0].sub[0].name;
            //console.log(initValue);
            noChoice = {'code': '000000000000', 'name': '不选择', 'sub':[{'code': '000000000001', 'name': '不选择'}]};
            tvRegion.unshift(noChoice);
            //console.log(tvRegion);
            $('#address_tv').empty();
            $('#address_tv').html('<input class="ys_input" name="address_tv" type="text" value="' + initValue + '"/>')
            $('#address_tv input').cityPicker({
                title: '选择街道/镇-居委会/村',
                showDistrict: false,
            }, tvRegion);
        });
    }).trigger('change');

    var shop_register_flag = false;
    $('#submit').on('click', function(){
        validateRes = false;
        $('#form').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return;
        $.toptips('信息提交中，请等待...', 'success');
        if(shop_register_flag) return false;
        shop_register_flag = true;
        $.ajax({
            url : url_pre + "/register/shop/submit/",
            type : 'post',
            contentType: "application/json; charset=utf-8",
            data: $('#form').serializeForm(),
            dataType : 'json',
            success : function(resp) {
                shop_register_flag = false;
                if(resp.success){
                    //console.log(resp);
                    $.toptips('验证通过，信息提交成功', 'success');
                    window.location.href = url_pre + '/staticfile/done/?from=seller_register2';
                }else{
                    $.toptips(resp.msg);
                }
            },
            error: function(){
                console.log('error');
            }
        });
    });
});
