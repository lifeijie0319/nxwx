$(document).ready(function() {
    var $dateBox = $('#js-qiandao-list'),
        $currentDate = $('.current-date'),
        $qiandaoBnt = $('#js-just-qiandao'),
        _html = '',
        _handle = true,
        myDate = new Date();
    var dateArray = [1, 2, 4, 6] // 假设已经签到的

    //获取签到天数、总签到次数、连续签到次数、总签到积分
    $.ajax({
        url: url_pre + '/sign/get/signin/',
        type: 'get',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        async: false,
        success: function(resp){
            dateArray = resp.signed_dates;
            //console.log(dateArray);
            if(resp.today_is_signed == 'true'){
                //alert('今日已签到');
                $qiandaoBnt.addClass('actived');
                $qiandaoBnt.html('今日已签');
                //openLayer('qiandao-active', qianDao);
                _handle = false;
            }
            $('#all_sign').html(dateArray.length + '天');
            //console.log(resp.credits);
            $('#all_sign_points').html(resp.credits + '积分');
        },
        error: function(){
            console.log('服务器错误');
        }
    });

    $currentDate.text(myDate.getFullYear() + '年' + parseInt(myDate.getMonth() + 1) + '月' + myDate.getDate() + '日');

    var monthFirst = new Date(myDate.getFullYear(), parseInt(myDate.getMonth()), 1).getDay();

    var d = new Date(myDate.getFullYear(), parseInt(myDate.getMonth() + 1), 0);
    var totalDay = d.getDate(); //获取当前月的天数

    for(var i = 0; i < 42; i++) {
        _html += '<li><div class="qiandao-icon"></div></li>'
    }
    $dateBox.html(_html) //生成日历网格

    var $dateLi = $dateBox.find('li');
    for(var i = 0; i < totalDay; i++) {
        $dateLi.eq(i + monthFirst).html('<div class="qiandao-icon">' + parseInt(i + 1) + '</div>');

        for(var j = 0; j < dateArray.length; j++) {
            if(i == dateArray[j]) {
                $dateLi.eq(i + monthFirst).addClass('qiandao');
            }
        }
    } //生成当月的日历且含已签到
    for(var i = totalDay; i < 42; i++) {
        $dateLi.eq(i + monthFirst).html('');
    }

    $('.date' + myDate.getDate()).addClass('able-qiandao');
    $dateBox.on('click', 'li', function() {
        if($(this).hasClass('able-qiandao') && _handle) {
            $(this).addClass('qiandao');
            qiandaoFun();
        }
    }) //签到

    $qiandaoBnt.on('click', function() {
        if(_handle) {
            qiandaoFun();
        }
    }); //签到

    function qiandaoFun() {
        _handle = false;
        req_token = $('#req_token').text()
        $.ajax({
            url: url_pre + '/sign/signin/',
            type: 'post',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({'req_token': req_token}),
            success: function(resp){
                console.log(resp);
                if(resp.success){
                    $qiandaoBnt.addClass('actived');
                    $qiandaoBnt.html('今日已签');
                    openLayer('qiandao-active', qianDao);
                    //_handle = false;
                    var dateLi = $dateBox.find('li');
                    var monthFirst = new Date(myDate.getFullYear(), parseInt(myDate.getMonth()), 1).getDay();
                    $dateLi.eq(parseInt(resp.today_index) + monthFirst - 1).addClass('qiandao');
                    $('#all_sign').html((parseInt($('#all_sign').html())+1).toString()+ '天');
                    $('#all_sign_points').html((parseInt($('#all_sign_points').html())+resp.added_credits).toString() + '积分');
                    $('#credits_added').text(resp.added_credits + '积分');
                    $('#my_credits').text('我的积分：' + resp.new_credits);
                }else{
                    _handle = true;
                    $.toptips(resp.msg);
                }
            },
            error: function() {
                _handle = false;
                console.log('服务器错误');
            }
        });
    }

    function qianDao() {
        $('.date' + myDate.getDate()).addClass('qiandao');
    }

	function openLayer(a, Fun) {
		$('.' + a).fadeIn(Fun)
	} //打开弹窗
    $('.close-qiandao-layer').on('click', function() {
        $(this).parents('.qiandao-layer').fadeOut();
    })

	$('#js-qiandao-history').on('click', function() {
		openLayer('qiandao-history-layer', myFun);

		function myFun() {
			//console.log(1)
		} //打开弹窗返回函数
	})

    var $layer = $('.qiandao-layer-con');
    $layer.css({'margin-top':($(window).height() - 213)/2});
    var $qiandao = $('.qiandao-icon');
    var $li_width = $qiandao.width();
    $qiandao.css({'height':$li_width,'line-height':$li_width+'px'});
});
