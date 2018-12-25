$(function () {
    $('input[name="update_figure"]').on('click', function(){
        var figure_id = $(this).parents('tr').attr('figure_id');
        $('input[name="figure_id"]').val(figure_id);
        var figure_name = $(this).parent().siblings('td[field="name"]').text();
        console.log(figure_name);
        $('input[name="figure_name"]').val(figure_name);
        $('#figure_modal').modal('show');
    });
    $('input[name="img"]').on('change', function(){
        var img_url = getObjectURL(this.files[0]) ;
        console.log(img_url);
        if(img_url){
            $('#preview').css({'display': 'block', 'width': '200px', 'height': '180px'}).attr('src', img_url);
        }
    });
    $('#figure_update_submit').on('click', function(){
        var formData = new FormData($( "#figure_update_form" )[0]);
        var figure_name = $('input[name="figure_name"]').val();
        $.ajax({
             url: '/mana_app/carousel_figure/update/',
             type: 'POST',
             data: formData,
             async: false,
             cache: false,
             contentType: false,
             processData: false,
             success: function (resp) {
                if(resp.success){
                    $('#figure_modal').modal('hide');
                    var figure_id = $('input[name="figure_id"]').val();
                    console.log(figure_id);
                    img_dom = $('tr[figure_id="' + figure_id + '"]').find('img');
                    console.log(img_dom.attr('src') + '?t=' + Math.random());
                    img_dom.attr('src', img_dom.attr('src') + '?t=' + Math.random());
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
             },
             error: function (resp) {
                 swal('错误', '服务器错误', 'error');
             }
        });
    });
    function getObjectURL(file) {  
        var url = null ;   
        // 下面函数执行的效果是一样的，只是需要针对不同的浏览器执行不同的 js 函数而已  
        if (window.createObjectURL!=undefined) { // basic  
            url = window.createObjectURL(file) ;  
        } else if (window.URL!=undefined) { // mozilla(firefox)  
            url = window.URL.createObjectURL(file) ;  
        } else if (window.webkitURL!=undefined) { // webkit or chrome  
            url = window.webkitURL.createObjectURL(file) ;  
        }  
        return url ;  
    }  
    //下面用于多图片上传预览功能
    function setImagePreviews() {
        //获取选择图片的对象
        var docObj = $('input[name="img"]')[0]
        //后期显示图片区域的对象
        var dd = document.getElementById("preview");
        dd.innerHTML = "";
        //得到所有的图片文件
        var fileList = docObj.files;
        //循环遍历
        for (var i = 0; i < fileList.length; i++) {    
            //动态添加html元素        
            dd.innerHTML += "<div style='float:left' > <img id='img" + i + "'  /> </div>";
            //获取图片imgi的对象
            var imgObjPreview = document.getElementById("img"+i); 
            
            if (docObj.files && docObj.files[i]) {
                //火狐下，直接设img属性
                imgObjPreview.style.display = 'block';
                imgObjPreview.style.width = '200px';
                imgObjPreview.style.height = '180px';
                //imgObjPreview.src = docObj.files[0].getAsDataURL();
                //火狐7以上版本不能用上面的getAsDataURL()方式获取，需要以下方式
                imgObjPreview.src = window.URL.createObjectURL(docObj.files[i]);   //获取上传图片文件的物理路径
                console.log(imgObjPreview.src);
            }
            else {
                //IE下，使用滤镜
                docObj.select();
                var imgSrc = document.selection.createRange().text;
                //alert(imgSrc)
                var localImagId = document.getElementById("img" + i);
               //必须设置初始大小
                localImagId.style.width = "200px";
                localImagId.style.height = "180px";
                //图片异常的捕捉，防止用户修改后缀来伪造图片
                try {
                    localImagId.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale)";
                    localImagId.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = imgSrc;
                }
                catch (e) {
                    alert("您上传的图片格式不正确，请重新选择!");
                    return false;
                }
                imgObjPreview.style.display = 'none';
                document.selection.empty();
            }
        }  
        return true;
    }
/*    function showCouponDetail(figure_id){
        data = {
            'figure_id': figure_id,
        }
        $.get('/mana_app/figure/detail/', data, function(resp){
            if(resp.success){
                $('#figure_detail_table tbody').html(resp.html);
                $('#figure_detail_modal').modal('show');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('input[name="show_figure_detail"]').on('click', function(){
        figure_id = $(this).parents('tr').attr('figure_id');
        console.log(figure_id);
        showCouponDetail(figure_id);
    });*/
});
