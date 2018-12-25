$(function(){
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
                console.log(resp.msg);
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
                        $.post(url_pre + '/user/photo/', {mediaid: mediaid}, function(resp){
                            $.toptips('头像修改成功', 'success');
                        });
                    }
                });
            }
        });
    });

});
