var turnplate = {
    restaraunts: [],       //大转盘奖品名称
    colors: [],          //大转盘奖品区块对应背景颜色
    outsideRadius: 192,      //大转盘外圆的半径
    textRadius: 155,       //大转盘奖品位置距离圆心的距离
    insideRadius: 40,      //大转盘内圆的半径
    startAngle: 0,       //开始角度
    bRotate: false,       //false:停止ture:旋转
};

window.onload = function () {

    //动态添加大转盘的奖品与奖品区域背景颜色
    $.ajax({
        type: "get",
        url: url_pre + '/lottery/set/',
        data: "",
        async: false,
        success: function(resp){
            awards = resp.awards;
            for(i = 0; i < awards.length; i++){
                turnplate.restaraunts.push(awards[i].dec);
                if(i % 2 == 0){
                    turnplate.colors.push("#FFFFFF");
                }else{
                    turnplate.colors.push("#FFF4D6");
                }
            }
        },
        error: function(){
            console.log('服务器错误');
        }
    });

    drawRouletteWheel();
    function drawRouletteWheel() {
        console.log(turnplate.restaraunts);
        var canvas = document.getElementById("wheelcanvas")
        if (canvas.getContext) {
            //根据奖品个数计算圆周角度
            var arc = Math.PI / (turnplate.restaraunts.length / 2)
            var ctx = canvas.getContext("2d")
            //在给定矩形内清空一个矩形
            ctx.clearRect(0, 0, 422, 422)
            //strokeStyle 属性设置或返回用于笔触的颜色、渐变或模式
            ctx.strokeStyle = "#FFF4D6"
            //font 属性设置或返回画布上文本内容的当前字体属性
            ctx.font = '16px Microsoft YaHei'
            for (var i = 0; i < turnplate.restaraunts.length; i++) {
                var angle = turnplate.startAngle + i * arc
                ctx.fillStyle = turnplate.colors[i]
                ctx.beginPath()
                //arc(x,y,r,起始角,结束角,绘制方向) 方法创建弧/曲线（用于创建圆或部分圆）
                ctx.arc(211, 211, turnplate.outsideRadius, angle, angle + arc, false)
                ctx.arc(211, 211, turnplate.insideRadius, angle + arc, angle, true)
                ctx.stroke()
                ctx.fill()
                //锁画布(为了保存之前的画布状态)
                ctx.save()
                //----绘制奖品开始----
                ctx.fillStyle = "#E5302F"
                var text = turnplate.restaraunts[i]
                if (/\(\d+\)$/.test(text)) {
                    commodityCode = text.replace(/\D/g, '')
                    text = text.split('(')[0]
                }
                var line_height = 17
                //translate方法重新映射画布上的 (0,0) 位置
                ctx.translate(211 + Math.cos(angle + arc / 2) * turnplate.textRadius, 211 + Math.sin(angle + arc / 2) * turnplate.textRadius)

                //rotate方法旋转当前的绘图
                ctx.rotate(angle + arc / 2 + Math.PI / 2)

                /** 下面代码根据奖品类型、奖品名称长度渲染不同效果，如字体、颜色、图片效果。(具体根据实际情况改变) **/
                if (text.length > 6) {//奖品名称长度超过一定范围
                    text = text.substring(0, 6) + "||" + text.substring(6)
                    var texts = text.split("||")
                    for (var j = 0; j < texts.length; j++) {
                        ctx.fillText(texts[j], -ctx.measureText(texts[j]).width / 2, j * line_height)
                    }
                } else {
                    //在画布上绘制填色的文本。文本的默认颜色是黑色
                    //measureText()方法返回包含一个对象，该对象包含以像素计的指定字体宽度
                    ctx.fillText(text, -ctx.measureText(text).width / 2, 0)
                }

                //添加对应图标
                if (text.indexOf("积分") > 0) {
                    var img = document.getElementById("shan-img")
                    img.onload = function () {
                        ctx.drawImage(img, -15, 10)
                    }
                    ctx.drawImage(img, -15, 10)
                } else if (text.indexOf("谢谢参与") >= 0) {
                    var img = document.getElementById("sorry-img")
                    img.onload = function () {
                        ctx.drawImage(img, -15, 10)
                    }
                    ctx.drawImage(img, -15, 10)
                } else {
                    var img = document.getElementById("shan-img")
                    img.onload = function () {
                        ctx.drawImage(img, -15, 30, 32, 32)
                    }
                    ctx.drawImage(img, -15, 30, 32, 32)
                }
                //把当前画布返回（调整）到上一个save()状态之前
                ctx.restore()
                //----绘制奖品结束----
            }
        }
    }
}


$(document).ready(function () {
    $('div.loadEffect').hide();
    $.get(url_pre + '/user/get_user/', function(resp){
        if(!resp.address){
            $.alert('您尚未登记住址，为便于发放奖品，请先到个人信息页面登记住址', '登记住址提醒', function(){
                window.location.href = url_pre + '/user/info/page/';
            })
        }
    });
    var rotateTimeOut = function () {
        $('#wheelcanvas').rotate({
            angle: 0,
            animateTo: 2160,
            duration: 4000,
            callback: function () {
                alert('网络超时，请检查您的网络设置！')
            }
        })
    }
    //旋转转盘 item:奖品位置 txt：提示语
    var rotateFn = function (item, txt) {
        var angles = item * (360 / turnplate.restaraunts.length) - (360 / (turnplate.restaraunts.length * 2))
        if (angles < 270) {
            angles = 270 - angles
        } else {
            angles = 360 - angles + 270
        }
        $('#wheelcanvas').stopRotate()
        $('#wheelcanvas').rotate({
            angle: 0,
            animateTo: angles + 1800,
            duration: 4000,
            callback: function () {
                //alert(txt)
                if (txt == "谢谢参与") {
                    $('.sorry_popup').addClass('is_visible')
                    $('.lottery_txt').html(txt)
                } else if (txt.indexOf('积分') > 0) {
                    $('.wow_popup').addClass('is_visible')
                    $('.lottery_txt').text(txt)
                    $('.wow_popup .lottery_check').attr('href', url_pre + '/staticfile/credits_history/?type=user')
                } else {
                    $('.wow_popup').addClass('is_visible')
                    $('.lottery_txt').text(txt)
                    $('.wow_popup .lottery_check').attr('href', url_pre + '/lottery/details/')
                }
                //console.log($('.wow_popup .lottery_check'));
                turnplate.bRotate = !turnplate.bRotate;
            }
        });
    }

    $('.wow_popup').on('click', function (event) {
        if ($(event.target).is('.popup_close') || $(event.target).is('.lottery_check')) {
            $(this).removeClass('is_visible')
        }
    })

    $('.sorry_popup').on('click', function (event) {
        if ($(event.target).is('.popup_close') || $(event.target).is('.lottery_check')) {
            $(this).removeClass('is_visible')
        }
    })

    $('.pointer').click(function(){
        if (turnplate.bRotate) return;
        turnplate.bRotate = !turnplate.bRotate;
        $('div.loadEffect').show();
        req_token = $('#req_token').text()
        //获取随机数(奖品个数范围内)
        $.post(url_pre + '/lottery/submit/', {'req_token': req_token}, function (resp) {
            $('div.loadEffect').hide();
            if(resp.success){
                console.log(resp.award.dec);
                var award_index = turnplate.restaraunts.indexOf(resp.award.dec);
                rotateFn(award_index + 1, turnplate.restaraunts[award_index]);
                $("#my_lottery span").text(resp.credits);
                $('#req_token').text(resp.req_token);
            }else{
                $.toptips(resp.msg);
            }
            //奖品数量等于10,指针落在对应奖品区域的中心角度[252, 216, 180, 144, 108, 72, 36, 360, 324, 288]
        }).error(function(){
            $.toptips('服务器错误');
        });
    });
})
