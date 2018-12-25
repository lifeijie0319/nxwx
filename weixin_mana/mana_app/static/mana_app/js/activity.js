$(function () {
    let table_area = $('#table_area');
    let activity_id;
    let validator = initValidate(
        $('#modal_form'),
        {
            'name': {
                required: true,
            },
            'key': {
                required: true,
            },
            'typ': {
                required: true,
            },
        },
    );
    function add(data) {
        $.post('/mana_app/activity/add/', data, function(resp){
            if(resp.success){
                $('#modal').modal('hide');
                $('#query_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_btn').on('click', function(){
        let form = $('#modal_form');
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        form[0].reset();

        $('#modal_submit').off('click').on('click', function(){
            if(!form.valid()) return false;
            let data = form.serializeForm();
            add(JSON.stringify(data));
        });
    });

    function del(activity_id) {
        swal({
            title: "删除确认",
            text: "确定删除该项？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function() {
            $.post('/mana_app/activity/delete/', {id: activity_id}, function (resp) {
                if (resp.success) {
                    swal('成功', resp.msg, 'success');
                    $('#query_btn').trigger('click');
                } else {
                    swal('错误', resp.msg, 'error');
                }
            });
        });
    }
    table_area.on('click', 'input[name="delete"]', function(){
        activity_id = $(this).parents('tr').attr('item_id');
        del(activity_id);
    });

    function update() {
        let data = {
            id: $(this).parents('tr').attr('item_id'),
        };
        $.post('/mana_app/activity/update/', data, function (resp) {
            if (resp.success) {
                $('#query_btn').trigger('click');
                swal('成功', resp.msg, 'success');
            } else {
                swal('错误', resp.msg, 'error');
            }
        }).error(function () {
            swal('错误', '服务器错误', 'error');
        });
    }
    $('input[name="update"]').on('click', update);

    function refresh(html) {
        $('#table_area').html(html);
        $('input[name="update"]').on('click', update);
        $('ul.pager a').on('click', function () {
            let activity_configs = $('#query_form').serializeForm();
            let action = $(this).attr('action');
            console.log(action);
            activity_configs.page = changePage(action);
            query(activity_configs);
        });
    }

    function query(data) {
        $.get('/mana_app/activity/query/', data, function (resp) {
            if (resp.success) {
                console.log(resp);
                refresh(resp.html);
                toptips(resp.msg, 'success');
            } else {
                toptips(resp.msg, 'danger');
            }
        });
    }

    $('#query_btn').on('click', function () {
        let form = $('#query_form');
        if (!form.valid()) return false;
        let data = form.serializeForm();
        let page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length === 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        query(data);
    }).trigger('click');

    let upload_model = $('#upload_modal');
    let upload_origin = upload_model.find('img[name="origin"]');
    let upload_preview = upload_model.find('img[name="preview"]');
    let upload_input = upload_model.find('input[name="img"]');
    let upload_form = upload_model.find('form');
    let upload_submit_btn = upload_model.find('button[name="submit"]');
    function getObjectURL(file) {
        let url = null ;
        // 下面函数执行的效果是一样的，只是需要针对不同的浏览器执行不同的 js 函数而已
        if (window.createObjectURL!=undefined) { // basic
            url = window.createObjectURL(file) ;
        } else if (window.URL!=undefined) { // mozilla(firefox)
            url = window.URL.createObjectURL(file) ;
        } else if (window.webkitURL!=undefined) { // webkit or chrome
            url = window.webkitURL.createObjectURL(file);
        }
        return url;
    }
    upload_input.on('change', function(){
        let img_url = getObjectURL(this.files[0]);
        console.log(img_url);
        if(img_url){
            upload_preview.attr('src', img_url);
        }
    });
    upload_submit_btn.on('click', function(){
        let formData = new FormData(upload_form[0]);
        $.ajax({
             url: '/mana_app/activity/upload/',
             type: 'POST',
             data: formData,
             async: false,
             cache: false,
             contentType: false,
             processData: false,
             success: function (resp) {
                if(resp.success){
                    upload_model.modal('hide');
                    swal('成功', resp.msg, 'success');
                }else{
                    swal('错误', resp.msg, 'error');
                }
             },
             error: function () {
                 swal('错误', '服务器错误', 'error');
             }
        });
    });
    table_area.on('click', 'input[name="upload"]', function(){
        activity_id = $(this).parents('tr').attr('item_id');
        upload_form[0].reset();
        upload_form.find('input[name="activity_id"]').val(activity_id);
        upload_origin.one('error', function(){
            this.src='/mana_app/media/activity/default.jpg';
        });
        upload_origin.attr('src', '/mana_app/media/activity/' + activity_id + '.jpg?'
            + (new Date()).getTime());
        upload_preview.attr('src', '');
        upload_model.modal('show');
    });

    let ext_modal = $('#ext_modal');
    let ext_table_area = ext_modal.find('#ext_table_area');
    let ext_modal_form = ext_modal.find('form');
    let ext_add_btn = ext_modal.find('button[name="ext_add_btn"]');
    let ext_validator = initValidate(
        ext_modal_form,
        {
            'typ': {
                required: true,
            },
            'name': {
                required: true,
            },
            'value': {
                required: true,
            },
        },
    );
    $('#ext_tab').on('click', '[data-toggle="tab"]', function () {
        let dom = $(this);
        let ext_add_btn = ext_modal.find('[name="ext_add_btn"]');
        if(dom.text() === '查看'){
            ext_add_btn.css('display','none')
        } else {
            ext_validator.resetForm();
            ext_modal_form[0].reset();
            ext_modal_form.find('.has-error').removeClass('has-error');
            ext_add_btn.css('display','inline-block');
        }
    });

    function ext_query(activity_id, init=false){
        let data = {
            id: activity_id,
            init: init,
        };
        $.get('/mana_app/activity/ext/query/', data, function (resp) {
            if (resp.success) {
                if(init){
                    console.log(resp.names);
                    let name_list = ext_modal_form.find('select[name="name"]');
                    let name_info = resp.names;
                    name_list.empty();
                    for(let i=0; i < name_info.length; i++){
                        name_list.append('<option value="' + name_info[i] + '">' + name_info[i] + '</option>')
                    }
                }
                ext_table_area.html(resp.html);
                $('#ext_tab a:first').tab('show');
            } else {
                toptips(resp.msg, 'danger');
            }
        });
    }
    table_area.on('click', 'button[name="ext_info"]', function(){
        console.log($(this));
        ext_query($(this).parents('tr').attr('item_id'), true);
    });

    function ext_add(data) {
        let activity_id = ext_table_area.find('tbody').attr('activity_id');
        data.activity_id = activity_id;
        $.post('/mana_app/activity/ext/add/', JSON.stringify(data), function(resp){
            if(resp.success){
                swal('成功', resp.msg, 'success');
                ext_query(activity_id);
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            swal('错误', '服务器错误', 'error');
        });
    }
    ext_add_btn.on('click', function(){
        let data = ext_modal_form.serializeForm();
        if(!ext_modal_form.valid()) return false;
        ext_add(data);
    });

    function ext_delete(item_id){
        let data = {id: item_id};
        let activity_id = ext_table_area.find('tbody').attr('activity_id');
        swal({
            title: "删除确认",
            text: "确定删除该项？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function() {
            $.post('/mana_app/activity/ext/delete/', data, function (resp) {
                if (resp.success) {
                    swal('成功', resp.msg, 'success');
                    ext_query(activity_id);
                } else {
                    swal('错误', resp.msg, 'error');
                }
            });
        });
    }
    ext_table_area.on('click', 'input[name="delete"]', function(){
        console.log($(this));
        ext_delete($(this).parents('tr').attr('item_id'));
    });

});
