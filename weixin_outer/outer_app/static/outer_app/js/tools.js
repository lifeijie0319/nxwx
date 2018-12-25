var base_url = 'https://wx.yinsho.com';
var url_pre = '/outer_app'
//var APPID = 'wx6290daffb81416ac';
APPID = 'wx64a1fdc74458e608';

window.onpageshow = function (e) {
    //alert(localStorage.getItem('refresh'));
    if (localStorage.getItem('refresh') == 'true') {
        //console.log(e.peristed);
        localStorage['refresh'] = 'false';
        //alert(localStorage.getItem('refresh'));
        setTimeout(function () {
            window.location.reload();
        }, 1000);
    }
}

function rd(n, m) {
    var c = m - n + 1;
    return Math.floor(Math.random() * c + n);
}

function get_url_args(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

function send_vcode(sendBtn, telephoneInputEle) {
    //alert('enter send_vcode');
    //alert('disabled:', sendBtn.prop('disabled'));
    console.log(sendBtn.prop('disabled'));
    if (sendBtn.prop('disabled')) return false;
    let telValidateRes = $.cell_validate(telephoneInputEle);
    if (telValidateRes == 'empty') {
        $.toptips('发送验证码之前请输入手机号!');
        return false;
    } else if (telValidateRes == 'notMatch') {
        return false;
    } else {
        $.post(url_pre + '/common/send_vcode/', telephoneInputEle.val(), function (resp) {
            if (resp.success) {
                $.toptips("验证码已发送，请查收！", 'success');
                let times = 60;
                sendBtn.prop('disabled', true);
                console.log(sendBtn.prop('disabled'));
                let timer = setInterval(function () {
                    times--;
                    sendBtn.text(times + "秒后重试");
                    if (times <= 0) {
                        sendBtn.text("发送验证码");
                        sendBtn.prop('disabled', false);
                        console.log(sendBtn.prop('disabled'));
                        clearInterval(timer);
                        times = 60;
                    }
                }, 1000);
            } else {
                $.toptips(resp.msg);
            }
        });
    }
}

function init_nav() {
    var currentUrl = window.location.pathname;
    switch (currentUrl) {
        case url_pre + '/staticfile/index/':
            currentNavIndex = 0;
            break;
        case url_pre + '/credits/page/':
            currentNavIndex = 1;
            break;
        case url_pre + '/staticfile/reservation/':
            currentNavIndex = 2;
            break;
        case url_pre + '/user/info/page/':
            currentNavIndex = 3;
            break;
        default:
            currentNavIndex = localStorage.getItem('currentNavIndex');
    }
    localStorage['currentNavIndex'] = currentNavIndex;
    console.log('idnex: ', currentNavIndex);
    $('div.ys_tabbar a').eq(currentNavIndex).addClass('ys_tabbar_active');
    $('div.ys_tabbar').on('click', 'a', function () {
        console.log($(this));
        localStorage['currentNavIndex'] = $('div.ys_tabbar a').index(this);
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');
console.log(csrftoken);

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
