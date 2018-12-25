$(function () {
    
    $('.table-responsive').responsiveTable({
        addFocusBtn: false,
        i18n:{
            focus:"聚焦",
            display:"选择显示",
            displayAll:"显示全部"
        }
    });
    console.log(initValidate)
    var validator = initValidate(
        $('#coupon_modal_form'),
        {
            'name': {
                required: true,
                format_check: /^(.){1,16}$/,
            },
            'credits': {
                required: true,
            },
            'value': {
                required: true,
            },
            'on_date': {
                required: true,
            },
            'off_date': {
                required: true,
            },
            'expired_date': {
                required: true,
            },
            'leftnum': {
                required: true,
            },
        },
    );

    function addCoupon(data) {
        $.post('/mana_app/coupon/add/', data, function(resp){
            if(resp.success){
                $('#coupon_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_coupon_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_coupon_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#coupon_modal_form')[0].reset();
        $('#coupon_modal').find('.modal-title').text('新增优惠券');
        $('#coupon_modal_submit').off('click').on('click', function(){
            if(!$('#coupon_modal_form').valid()) return false;
            data = JSON.stringify($('#coupon_modal_form').serializeForm());
            console.log(data);
            addCoupon(data);
        });
    });

    function delCoupon(coupon_id){
        swal({
            title: "删除确认",
            text: "确定删除该优惠券？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'coupon_id': coupon_id,
            });
            $.post('/mana_app/coupon/delete/', data, function(resp){
                if(resp.success){
                    swal('成功', resp.msg, 'success');
                    $('#query_coupon_btn').trigger('click');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }
    $('input[name="delete_coupon"]').on('click', function(){
        coupon_id = $(this).parents('tr').attr('coupon_id');
        console.log(coupon_id);
        delCoupon(coupon_id);
    });

    function updateCoupon(data){
        $.post('/mana_app/coupon/update/', data, function(resp){
            if(resp.success){
                $('#coupon_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_coupon_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    function updateCouponModal(){
        function set_optional(update_btn, field){
            var name = update_btn.parents('tr').find('td[field="' + field + '"]').text()
            $('#coupon_modal').find('select[name="' + field + '"] > option').each(function(idx, ele){
                if($(ele).text() == name){
                    $(ele).prop('selected', true);
                }
            });
        }
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#coupon_modal_form')[0].reset();

        var update_btn = $(this);
        var coupon_id = update_btn.parents('tr').attr('coupon_id');
        $('#coupon_modal').find('.modal-title').text('更新优惠券');
        $('#coupon_modal').find('input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });
        var description = update_btn.parents('tr').find('td[field="description"]').text();
        $('#coupon_modal textarea[name="description"]').val(description);
        set_optional(update_btn, 'discount_type');
        set_optional(update_btn, 'term1');
        set_optional(update_btn, 'term2');
        set_optional(update_btn, 'term_relation');
        var shop_names = update_btn.parents('tr').find('td[field="shops"]').text().split('|');
        var real_shop_names = new Array();
        $.each(shop_names, function(index, value, array){
            real_value = value.replace(/\s*/g, '');
            if(real_value){
                real_shop_names.push(real_value);
            }
        });
        $('#coupon_modal').find('select[name="shops"] > option').each(function(idx, ele){
            if($.inArray($(ele).text(), real_shop_names) != -1){
                $(ele).prop('selected', true);
            }
        });
        $('#coupon_modal_submit').off('click').on('click', function(){
            if(!$('#coupon_modal_form').valid()) return false;
            data = $('#coupon_modal_form').serializeForm();
            data['id'] = coupon_id;
            console.log(data);
            updateCoupon(JSON.stringify(data));
        });
        $('#coupon_modal').modal('show');
    }
    $('input[name="update_coupon"]').on('click', updateCouponModal);

    function queryCoupon(data){
        $.get('/mana_app/coupon/query/', data, function(resp){
            if(resp.success){
                refreshCoupon(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        }).error(function(){
            toptips('服务器错误', 'danger');
        });
    }
    $('#query_coupon_btn').on('click', function(){
        page_dom = $('ul.pager li[name="current_page"]');
        data = {
            'coupon_name': $('input[name="query_coupon_name"]').val(),
            'page': page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, '')),
        }
        queryCoupon(data);
    });

    function refreshCoupon(html){
        $('#table_area').html(html);
        $('.table-responsive').responsiveTable('update');
        $('input[name="delete_coupon"]').on('click', function(){
            coupon_id = $(this).parents('tr').attr('coupon_id');
            delCoupon(coupon_id);
        });
        $('input[name="update_coupon"]').on('click', updateCouponModal);
        /*$('input[name="show_coupon_detail"]').on('click', function(){
            coupon_id = $(this).parents('tr').attr('coupon_id');
            console.log(coupon_id);
            showCouponDetail(coupon_id);
        });*/
        $('input[name="send_coupon"]').on('click',function(){
            var coupon_id = $(this).parents('tr').attr('coupon_id');
            $('input[name="coupon_id"]').val(coupon_id);
            $('#coupon_send_modal').modal('show');
        });
        $('input[name="upload_coupon"]').on('click', function(){
            var coupon_id = $(this).parents('tr').attr('coupon_id');
            $('input[name="coupon_id"]').val(coupon_id);
            $('#origin_img').one('error', function(){
                this.src='/mana_app/media/coupon/default.jpg';
            });
            $('#origin_img').attr('src', '/mana_app/media/coupon/' + coupon_id + '.jpg');
            $('#preview').attr('src', '');
            console.log($('#origin_img').attr('src'));
            $('#coupon_upload_modal').modal('show');
        });
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryCoupon(params);
        });
    }
    $('#coupon_send_submit').on('click',function(){

       var formData = new FormData($( "#coupon_send_form" )[0]);
       $.ajax({
           url:'/mana_app/coupon/send/',
           type:'POST',
           data: formData,
           async: false,
           cache: false,
           contentType: false,
           processData: false,
           success: function (resp) {
                if (resp.success){
                swal('成功', 'success');
                    }
                else{
                swal('失败', resp.msg,'error') ;
                    }
                $('#coupon_send_modal').modal('hide');
           },
           error: function(resp){
                 swal('错误', '服务器错误', 'error');
           }
           })
    });

    $('input[name="img"]').on('change', function(){
        var img_url = getObjectURL(this.files[0]) ;
        console.log(img_url);
        if(img_url){
            $('#preview').attr('src', img_url);
        }
    });
    $('#coupon_upload_submit').on('click', function(){
        var formData = new FormData($( "#coupon_upload_form" )[0]);
        var coupon_id = $('input[name="coupon_id"]').val();
        $.ajax({
             url: '/mana_app/coupon/upload/',
             type: 'POST',
             data: formData,
             async: false,
             cache: false,
             contentType: false,
             processData: false,
             success: function (resp) {
                if(resp.success){
                    $('#coupon_upload_modal').modal('hide');
                    swal('成功', resp.msg, 'success');
                    img_dom = $('tr[coupon_id="' + coupon_id + '"]').find('img');
                    img_dom.attr('src', '/mana_app/media/coupon/' + coupon_id + '.jpg?t=' + Math.random());
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
    /*function setImagePreviews() {
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
    function showCouponDetail(coupon_id){
        data = {
            'coupon_id': coupon_id,
        }
        $.get('/mana_app/coupon/detail/', data, function(resp){
            if(resp.success){
                $('#coupon_detail_table tbody').html(resp.html);
                $('#coupon_detail_modal').modal('show');
            }else{
                toptips(resp.msg, 'danger');
            }
        });
    }
    $('input[name="show_coupon_detail"]').on('click', function(){
        coupon_id = $(this).parents('tr').attr('coupon_id');
        console.log(coupon_id);
        showCouponDetail(coupon_id);
    });*/
});
