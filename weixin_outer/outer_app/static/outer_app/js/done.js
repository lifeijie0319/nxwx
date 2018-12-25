$(function () {
    let from = get_url_args('from');
    console.log(from);
    let title = $('#content_title');
    let content = $('#content');
    let submit_btn = $('#submit');
    switch (from) {
        case 'withdraw_apply':
            title.text('申请成功');
            content.text('申请提交已发出，请等待后台人员确认');
            submit_btn.on('click', function () {
                //localStorage['refresh'] = 'true';
                window.history.go(-2);
                //window.location.href = '/seller/page/'
            });
            break;
        case 'reservation':
            title.text('申请成功');
            let type = get_url_args('type');
            if (type === 'kdd1') {
                content.text('您的申请已提交，客户经理将及时与您取得联系。点击完成返回申请页面。');
            } else if (type === 'kdd2') {
                let price = get_url_args('price');
                content.html('您的申请已提交，根据您的申请信息，本次预估可贷额度为\
                    <strong class="color_danger" style="font-size: 22px; padding: 0 10px;">'
                    + price + '万元</strong>，具体以合同最终授信额度为准。\
                    客户经理将及时与您取得联系，点击完成返回申请页面');
            } else {
                content.text('申请提交已发出，请等待后台人员确认');
            }
            submit_btn.on('click', function () {
                window.location.href = url_pre + '/staticfile/reservation_status/'
            });
            break;
        case 'reservation_dgkh':
            type = get_url_args('type');
            let msg;
            if (type === 'success') {
                title.text('预约成功');
                msg = '您的预约已成功， 我们会尽快联系您办理相关事项！请稍候！';
                submit_btn.attr('href', url_pre + '/staticfile/reservation_status/');
            } else {
                $('.ys_prompt_icon > i').removeClass('icon-correct_big').addClass('icon-close-fill color_danger');
                title.text('预约失败');
                msg = '您的预约失败，您还可通过电话预约方式进行预约！';
                submit_btn.on('click', function () {
                    wx.closeWindow();
                });
            }
            let reservation_dgkh_msg = localStorage.getItem('reservation_dgkh_msg');
            content.text(msg).after('<p class="ys_pt_desc">' + reservation_dgkh_msg + '</p>');
            break;
        case 'online_num_taking':
            title.text('取号成功');
            content.text('已经取号成功，请前往查询');
            submit_btn.on('click', function () {
                window.location.href = url_pre + '/online/num/taking/page/'
            });
            break;
        case 'promotion_order':
            title.text('购买成功');
            content.text('请到我的票券页面查看购买的优惠券');
            submit_btn.on('click', function () {
                //localStorage['refresh'] = 'true';
                window.history.go(-4);
                //window.location.href = '/promotion/page/'
            });
            break;
        case 'register':
            let isNew = get_url_args('isNew');
            title.text('注册成功');
            submit_btn.on('click', function () {
                localStorage['refresh'] = 'true';
                window.history.go(-1);
                //wx.closeWindow();
                //alert(document.referrer);
                //window.location.href = document.referrer;
            });
            //console.log(isNew);
            if (isNew === 'true') {
                content.text('恭喜您，注册成功！欢饮到南浔银行开户办理业务，绑定实名账户即可享受更多优惠！');
            } else {
                content.text('恭喜您，注册成功！点击完成返回菜单');
            }
            break;
        case 'seller_register2':
            title.text('注册申请提交成功');
            submit_btn.on('click', function () {
                //localStorage['refresh'] = 'true';
                //window.history.go(-3);
                wx.closeWindow();
            });
            //console.log(isNew);
            content.text('恭喜您，注册申请提交成功！点击完成返回菜单');
            break;
        case 'seller_auditing':
            $('title').text('商户注册申请');
            title.text('注册申请审核中');
            submit_btn.on('click', function () {
                wx.closeWindow();
            }).text('返回');
            content.text('注册申请审核中，请耐心等待。');
            break;
        case 'seller_replace_auditing':
            $('title').text('商户微信号重新绑定申请');
            title.text('微信号重新绑定申请审核中');
            submit_btn.on('click', function () {
                wx.closeWindow();
            }).text('返回');
            content.text('微信号重新绑定申请审核中，请耐心等待。');
            break;
        case 'activity':
            title.text('活动信息登记成功');
            content.text('恭喜您，点击完成返回菜单');
            submit_btn.on('click', function () {
                wx.closeWindow();
            });
            break;
        default:
            title.text('注册成功');
            content.text('恭喜您，注册成功，点击完成返回菜单');
            submit_btn.on('click', function () {
                wx.closeWindow();
            });
    }
});
