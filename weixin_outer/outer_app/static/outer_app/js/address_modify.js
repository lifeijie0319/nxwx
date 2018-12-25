$(function(){
    console.log($('input:hidden').val());
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
            $('#address_tv').html('<input class="ys_input" type="text" value="' + initValue + '"/>')
            $('#address_tv input').cityPicker({
                title: '选择街道/镇-居委会/村',
                showDistrict: false,
            }, tvRegion);
        });
    }).trigger('change');
    $('#submit').on('click', function(){
        from = get_url_args('from');
        id = get_url_args('id');
        data = {
            from: from,
            id: id,
            addressPcc: $('#address_pcc').val(),
            addressTv: $('#address_tv input').val(),
            addressDetail: $('#address_detail').val(),
        }
        $.toptips('正在修改地址', 'success');
        $.post(url_pre + '/address/modify/', data, function(resp){
            if(resp.success){
                //console.log(resp);
                $.toptips('地址修改成功!', 'success');
                setTimeout(function(){
                    window.history.go(-1);
                    //if(from == 'shop'){
                    //    window.location.href = url_pre + '/shop/page/';
                    //}else{
                    //    window.location.href = url_pre + '/user/info/page/';
                    //}
                }, 1000);
            }
        });
    });
});
