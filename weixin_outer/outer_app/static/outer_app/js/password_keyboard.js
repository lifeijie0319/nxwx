(function($){
    $.fn.create_password_keyboard = function(){
        var creatingDiv, createdDiv;
        creatingDiv = '\
        <div class="keyboard_wrap ys_btop">\
            <div class="keyboard_top ys_bbottom">\
                <h1>请输入支付密码</h1>\
            </div>\
            <div class="password_wrap">\
                <form>\
                    <input readonly class="password_input" type="password" maxlength="1"value="">\
                    <input readonly class="password_input" type="password" maxlength="1"value="">\
                    <input readonly class="password_input" type="password" maxlength="1"value="">\
                    <input readonly class="password_input" type="password" maxlength="1"value="">\
                    <input readonly class="password_input" type="password" maxlength="1"value="">\
                    <input readonly class="password_input pass_right" type="password" maxlength="1" value="">\
                </form>\
            </div>\
            <div class="password_tips">\
                <span>支付环境安全，请放心支付</span>\
            </div>\
            <div class="keys_wrap">\
                <ul>\
                    <li class="symbol"><span class="off">1</span></li>\
                    <li class="symbol"><span class="off">2</span></li>\
                    <li class="symbol"><span class="off">3</span></li>\
                    <li class="tab"><span class="off">4</span></li>\
                    <li class="symbol"><span class="off">5</span></li>\
                    <li class="symbol"><span class="off">6</span></li>\
                    <li class="tab"><span class="off">7</span></li>\
                    <li class="symbol"><span class="off">8</span></li>\
                    <li class="symbol"><span class="off">9</span></li>\
                    <li class="cancle lastitem">取消</li>\
                    <li class="symbol"><span class="off">0</span></li>\
                    <li class="delete"><img class="delete_btn" src="/static/outer_app/images/delete.png"></li>\
                </ul>\
            </div>\
        </div>\
        ';
        $(this).append(creatingDiv);
        createdDiv = $('div.keyboard_wrap');
        //console.log(createdDiv);
        return createdDiv;
    }

    $.fn.config_password_keyboard = function(url, successCallback){
        createdDiv = $(this);
        var passwords = createdDiv.find('div.password_wrap > form')[0];
        var character;
        var index = 0;
        var tips = createdDiv.find('div.password_tips');
        //console.log(createdDiv.find('div.keys_wrap ul li'));
        keyboard = createdDiv.find('div.keys_wrap ul li');
        keyboard.off('click');
        keyboard.on('click', function(){
            if ($(this).hasClass('delete')) {
                console.log(index);
                $(passwords.elements[--index%6]).val('');
                if($(passwords.elements[0]).val()==''){
                    index = 0;
                }
                /*for(var i= 0,len=passwords.elements.length-1;len>=i;len--){
                    if($(passwords.elements[len]).val()!=''){
                        $(passwords.elements[len]).val('');
                        break;
                    }
                }*/
                return false;
            }
            if ($(this).hasClass('cancle')) {
                createdDiv.removeClass('keyboard_wrap_visible');
                $('div.ys_mask.ys_mask_visible').remove();
                for(var i= 0,len=passwords.elements.length-1;len>=i;len--){
                    if($(passwords.elements[len]).val()!=''){
                        $(passwords.elements[len]).val('');
                        index = 0;
                    }
                }
                tips.text('支付环境安全，请放心支付');
                tips.removeClass('color_danger');
            }
            if ($(this).hasClass('symbol') || $(this).hasClass('tab')){
                character = $(this).text();
                $(passwords.elements[index++%6]).val(character);
                if($(passwords.elements[5]).val()!=''){
                    index = 0;
                }
                /*for(var i= 0,len=passwords.elements.length;i<len;i++){
                    if($(passwords.elements[i]).val()== null ||$(passwords.elements[i]).val()==undefined||$(passwords.elements[i]).val()==''){
                        $(passwords.elements[i]).val(character);
                        break;
                    }
                }*/
                if($(passwords.elements[5]).val()!='') {
                    var tempPassword = '';
                    for (var i = 0; i < passwords.elements.length; i++) {
                        tempPassword += $(passwords.elements[i]).val();
                    }
                    retPassword = tempPassword;
                    $.get(url, {password: retPassword}, function(resp){
                        if(resp.success){
                            tips.text('密码通过验证');
                            tips.removeClass('color_danger');
                            successCallback();
                        }else{
                            for(var i= 0,len=passwords.elements.length-1;len>=i;len--){
                                if($(passwords.elements[len]).val()!=''){
                                    $(passwords.elements[len]).val('');
                                    index = 0;
                                }
                            }
                            tips.text('密码错误');
                            tips.addClass('color_danger');
                        }
                    })
                }
            }
        });
    }

})($);
