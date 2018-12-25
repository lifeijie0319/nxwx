# -*- coding:utf-8 -*-
import time
# import urllib
from django.shortcuts import render, reverse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from xml.etree import ElementTree as ET

from ..config import APP_NAME, BASE_URL
from ..global_var import logger, redis_conn
from ..socket_client import send2serv
from ..tools import get_oauth_url
from ..wx import weixin_check


@csrf_exempt
def index(request):
    logger.debug('root msg: %s', request.body)
    if request.method == 'GET':
        return weixin_check(request)
    elif request.method == 'POST':
        doc_root = ET.fromstring(request.body)
        xml_type = doc_root.find('MsgType').text
        if xml_type == 'text':
            return text_handler(request, doc_root)
        elif xml_type == 'event':
            return event_handler(request, doc_root)
        else:
            return HttpResponse('')


def text_handler(request, doc_root):
    openid = doc_root.find('FromUserName').text
    server_id = doc_root.find('ToUserName').text
    send_text = doc_root.find('Content').text
    context = {
        'to_user': openid,
        'from_user': server_id,
        'create_time': int(time.time())
    }
    activity_rtn = send2serv({'path': 'activity.config', 'kargs': {'key': send_text}})
    if activity_rtn['matched']:
        activity_id = str(activity_rtn['id'])
        origin_url = reverse(APP_NAME + ':activity') + '?activity_id=' + activity_id
        if activity_rtn['typ'] == '信息登记':
            items = [{
                'title': activity_rtn['name'],
                'picurl': BASE_URL + '/outer_app/media/activity/' + activity_id + '.jpg?t=' + str(time.time()),
                'url': get_oauth_url(origin_url),
            }]
            context['count'] = 1
            context['items'] = items
            logger.debug('ACTIVITY RES XML:{}'.format(context))
            logger.debug('XML RET: {}'.format(render_to_string(APP_NAME + '/xml/news.xml', context)))
            return render(request, APP_NAME + '/xml/news.xml', context, content_type='application/xml')
        elif activity_rtn['typ'] == '盖楼':
            award_flag, cur_level, msg = activity_award_judge(openid, activity_rtn)
            if award_flag:
                url = get_oauth_url(origin_url)
                context['content'] = '您是' + str(cur_level) + '楼，恭喜您中奖了，奖品是' + msg +\
                    '。为了方便银行与您联系，请<a href="' + url + '">填写您的个人信息</a>'
            else:
                context['content'] = msg
            return render(request, APP_NAME + '/xml/text.xml', context, content_type='application/xml')
    else:
        msgs = '\n'.join([activity['name'] + ': 回复关键字"' + activity['key'] + '"参加'
                          + activity['typ'] + '活动' for activity in activity_rtn['items']])
        context['content'] = '当前可以参加的活动如下，请回复正确的关键字：\n' + msgs
        return render(request, APP_NAME + '/xml/text.xml', context, content_type='application/xml')


def event_handler(request, doc_root):
    return HttpResponse('')


# 判断盖楼是否获奖，如果获奖，将中奖信息记录
def activity_award_judge(openid, activity):
    queue_name = 'WX_ACTIVITY_' + str(activity['id'])
    cur_level = redis_conn.get(queue_name)
    if not cur_level:
        cur_level = 1
        redis_conn.incr(queue_name)
    ext_info = activity['ext_info']
    logger.debug('ACTIVITY EXT INFO:{}'.format(ext_info))
    loop_names = [u'循环一', u'循环二', u'循环三']
    loops = []
    for i in range(3):
        num = ext_info.get(loop_names[i])
        award = ext_info.get(loop_names[i] + u'奖品')
        if num:
            if award:
                loops.append((num, award))
            else:
                return False, cur_level, loop_names[i] + '未配置奖品'
    loops.sort(key=lambda x: x[0], reverse=True)
    logger.debug('LOOPS: {}'.format(loops))
    real_award = ''
    if loops:
        for num, award in loops:
            if int(cur_level) % int(num) == 0:
                real_award = award
                break
        award_add_rtn = send2serv({'path': 'activity.post_award_add', 'kargs': {
            'openid': openid,
            'activity_id': activity['id'],
            'level': cur_level,
            'award': real_award,
        }})
        if award_add_rtn['success']:
            redis_conn.incr(queue_name)
            if real_award:
                return True, cur_level, real_award
            else:
                return False, cur_level, '您是' + str(cur_level) + '楼，大奖与您擦肩而过'
        else:
            return False, cur_level, award_add_rtn['msg']
    else:
        return False, cur_level, '该活动未配置循环和奖品，请联系管理员'