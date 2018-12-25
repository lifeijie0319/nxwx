$(function () {
    console.log($(".cssload-container"));
    $('.loading').show();
    validator = initValidate(
        $('#community_assess_modal_form'),
        {
            'price': {
                required: true,
                format_check: /^\d{1,4}\.\d{2}$/,
            },
        },
    );

    function queryCusRegion(data){
        $('#loading').show();
        $.get(url_pre + '/community_assess/query/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                refreshCusRegion(resp.html);
                toptips(resp.msg, 'success');
            }else{
                toptips(resp.msg, 'danger');
            }
        }).error(function(){
            $('#loading').hide();
            toptips('服务器错误', 'danger');
        });
    }
    $('#query_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        page_dom = $('ul.pager li[name="current_page"]');
        data.page = page_dom.length == 0 ? 1 : parseInt(page_dom.text().replace(/\D/g, ''));
        //console.log(data);
        queryCusRegion(data);
    });

    $('#gen_excel_btn').on('click', function(){
        //if(!$('#query_form').valid()) return false;
        data = $('#query_form').serializeForm();
        data['mode'] = 'excel';
        query_string = toQueryString(data);
        window.open(url_pre + '/community_assess/query/' + query_string);
    });

    $('#upload_btn').on('click', function(){
        files = $('#upfile')[0].files;
        if(!files.length){
            toptips('请先选择文件', 'danger');
            return false;
        }
        file = files[0];
        f_name = file.name;
        idx1 = f_name.lastIndexOf('.');
        idx2 = f_name.length;
        suffix = f_name.substring(idx1 + 1, idx2);
        //console.log(suffix);
        if(suffix != 'xls' && suffix != 'xlsx'){
            toptips('上传文件格式不对，只接受excel', 'danger');
            return false;
        }
        var formData = new FormData();
        formData.append('upfile', file);
        $('#loading').show();
        $.ajax({
            url: url_pre + '/community_assess/upload/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(resp){
                $('#loading').hide();
                if(resp.success){
                    $('#query_btn').trigger('click');
                    swal('成功', '导入成功', 'success');
                }else{
                    swal('失败', resp.msg, 'error');
                }
            },
            error: function(resp){
                $('#loading').hide();
                swal('服务器错误', resp.msg, 'error');
            }
        });
    });
    
    function addCusRegion(data) {
        $('#loading').show();
        $.post(url_pre + '/community_assess/add/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#community_assess_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            $('#loading').hide();
            swal('错误', '服务器错误', 'error');
        });
    }
    $('#add_btn').on('click', function(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#community_assess_modal_form')[0].reset();

        $('#community_assess_modal input[name="community"]').attr('readonly', false);
        $('#community_assess_modal').find('.modal-title').text('新增记录');
        $('#community_assess_modal_submit').off('click').on('click', function(){
            if(!$('#community_assess_modal_form').valid()) return false;
            data = $('#community_assess_modal_form').serializeForm();
            addCusRegion(JSON.stringify(data));
        });
    });

    function delCusRegion(community){
        swal({
            title: "删除确认",
            text: "确定删除该记录？",
            type: "info",
            showCancelButton: true,
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(){
            var data = JSON.stringify({
                'community': community,
            });
            $.post(url_pre + '/community_assess/delete/', data, function(resp){
                if(resp.success){
                    swal('成功', resp.msg, 'success');
                    $('#query_btn').trigger('click');
                }else{
                    swal('错误', resp.msg, 'error');
                }
            }).error(function(){
                swal('错误', '服务器错误', 'error');
            });
        });
    }

    function updateCusRegion(data){
        $('#loading').show();
        $.post(url_pre + '/community_assess/update/', data, function(resp){
            $('#loading').hide();
            if(resp.success){
                $('#community_assess_modal').modal('hide');
                swal('成功', resp.msg, 'success');
                $('#query_btn').trigger('click');
            }else{
                swal('错误', resp.msg, 'error');
            }
        }).error(function(){
            $('#loading').hide();
            swal('错误', '服务器错误', 'error');
        }); 
    }
    function initUpdateCusRegion(){
        validator.resetForm();
        $('.has-error').removeClass('has-error');
        $('#community_assess_modal_form')[0].reset();

        var update_btn = $(this);

        $('#community_assess_modal input').each(function(index, dom){
            var input_name = $(this).attr('name');
            var input_value = update_btn.parents('tr').find('td[field="' + input_name + '"]').text();
            $(this).val(input_value);
        });

        $('#community_assess_modal input[name="community"]').attr('readonly', true);

        $('#community_assess_modal').find('.modal-title').text('更新');
        $('#community_assess_modal_submit').off('click').on('click', function(){
            if(!$('#community_assess_modal_form').valid()) return false;
            data = $('#community_assess_modal_form').serializeForm();
            updateCusRegion(JSON.stringify(data));
        });
        $('#community_assess_modal').modal('show');
    }

    function refreshCusRegion(html){
        $('#table_area').html(html);
        $('ul.pager a').on('click', function(){
            params = $('#query_form').serializeForm();
            action = $(this).attr('action');
            console.log(action);
            params.page = changePage(action);
            queryCusRegion(params);
        });
        $('input[name="delete"]').on('click', function(){
            community = $(this).parents('tr').find('[field="community"]').text();
            console.log(community);
            delCusRegion(community);
        });
        $('input[name="update"]').on('click', initUpdateCusRegion);
    }
});
