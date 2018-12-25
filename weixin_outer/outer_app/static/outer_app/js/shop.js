$(function(){
    var path;

    timestamp = new Date().getTime();
    $.get(url_pre + '/seller/info/?v=' + timestamp, function(resp){
        $('#account_no').text(resp.account.slice(0, 4) + '********' + resp.account.slice(-4));
    });

    $.ajax({
        url : url_pre + '/wx/jssdk/',
        type : 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType : 'json',
        data : JSON.stringify({
            'url': window.location.href,
            //'csrfmiddlewaretoken': localStorage.getItem('csrftoken')
        }),
        success : function(resp) {
            if(resp.success){
                resp = resp.config;
                wx.config({
                    debug : false,
                    appId : APPID,
                    timestamp : resp.timestamp,
                    nonceStr : resp.nonceStr,
                    signature : resp.signature,
                    jsApiList : ['chooseImage','uploadImage']
                });
            }else{
                console.lgo(resp.msg);
            }
        },
        error : function(xhr, textStatus, errorThrown){
            alert(xhr.status);
            alert(xhr.readyState);
            alert(textStatus);
        }
    })

    $('#shop_photo').on('click', function(){
        wx.chooseImage({
            count: 1, // 默认9
            sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
            sourceType: ['album'], // 可以指定来源是相册还是相机，默认二者都有
            success: function (res) {
                var localIds = res.localIds // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
                $('#shop_photo > img').attr('src', localIds[0])
                wx.uploadImage({
                    localId: localIds[0], // 需要上传的图片的本地ID，由chooseImage接口获得
                    isShowProgressTips: 1, // 默认为1，显示进度提示
                    success: function (res) {
                        var serverId = res.serverId; // 返回图片的服务器端ID
                        mediaid = serverId;
                        data = {
                            'shop_id': $('#shop_photo').attr('photo_id'),
                            'mediaid': mediaid,
                        }
                        $.post(url_pre + '/shop/photo/', data, function(resp){
                            $.toptips('头像修改成功', 'success');
                        });
                    }
                });
            }
        });
    });

    $('a.open-popup').on('click', function(){
        window.history.pushState({}, '', url_pre + '/shop/name_modify/')
        path = url_pre + '/shop/name_modify/';
    });

    $(window).on('popstate', function(){
        if(path == url_pre + '/shop/name_modify/'){
            $.closePopup();
        }
    });

    $('#shop_name_modify_form').form();
    $('#shop_name_modify_submit').on('click', function(){
        validateRes = false;
        $('#shop_name_modify_form').validate(function(error){
            if(error){
            }else{
                validateRes = true;
            }
        });
        if(!validateRes) return false;
        newShopName = $('input[name="name"]').val();
        id = get_url_args('id')
        //console.log(newShopName);
        $.toptips('正在修改', 'success');
        $.post(url_pre + '/shop/name_modify/', {name: newShopName, id: id}, function(resp){
            shopTitleEle = $('a.open-popup div.ys_cell_bd h3');
            shopType = shopTitleEle.text().split('(')[1];
            shopTitleEle.text(newShopName + '(' + shopType);
            $.toptips('修改成功', 'success');
            //window.location.href = '/shop/page/';
            window.history.back();
            //console.log(resp);
        });
    });
});
