#-*- coding:utf-8 -*-
import json
from django.urls import reverse

from .config import APP_NAME, RESERVATION_TEMPLATE_ID, APPLICATION_TEMPLATE_ID, APPLICATION_FEEDBACK_TEMPLATE_ID
from .global_var import logger, redis_conn
from .tools import get_oauth_url


def seller_registration_apply(openids, data):
    url = get_oauth_url(reverse(APP_NAME + ':register_seller_audit_page'))
    logger.debug(url)
    content = {
        'first': {
            'value': u'收到新的商户注册申请',
            'color': '#000000'
        },
        'keyword1': {
            'value': data.get('info'),
            'color': '#000000'
        },
        'keyword2': {
            'value': data.get('name'),
            'color': '#000000'
        },
        'keyword3': {
            'value': u'商户注册',
            'color': '#000000'
        },
        'keyword4': {
            'value' : data.get('apply_datetime'),
            'color' :'#000000'
        },
        'remark': {
            'value': u'点击查看详情',
            'color': '#000000'
        },
    }
    for openid in openids:
        input_data = json.dumps({
            'openid': openid,
            'template_id': APPLICATION_TEMPLATE_ID,
            'url': url,
            'content': content,
        })
        redis_conn.lpush('QUEUE:WX:TEMPLATE_MSG', input_data)
    return {'success': True}


def seller_replace_apply_msg(openids, data):
    url = get_oauth_url(reverse(APP_NAME + ':seller_replace_audit_page'))
    logger.debug(url)
    content = {
        'first': {
            'value': u'收到新的商户微信号更换申请',
            'color': '#000000'
        },
        'keyword1': {
            'value': data.get('info'),
            'color': '#000000'
        },
        'keyword2': {
            'value': data.get('name'),
            'color': '#000000'
        },
        'keyword3': {
            'value': u'商户微信号更换',
            'color': '#000000'
        },
        'keyword4': {
            'value' : data.get('apply_datetime'),
            'color' :'#000000'
        },
        'remark': {
            'value': u'点击查看详情',
            'color': '#000000'
        },
    }
    for openid in openids:
        input_data = json.dumps({
            'openid': openid,
            'template_id': APPLICATION_TEMPLATE_ID,
            'url': url,
            'content': content,
        })
        redis_conn.lpush('QUEUE:WX:TEMPLATE_MSG', input_data)
    return {'success': True}


def reservation_apply(reservation, openids):
    '''
    当预约请求出现时调用此函数，
    向对应的客户经理发送消息
    '''
    url = get_oauth_url(reverse(APP_NAME+':staticfile', kwargs={'name': 'reservation_deal'}))
    content = {
         'first':{
             'value': '预约待处理消息',
             'color': '#000000'
         },
         'keyword1':{
             'value': reservation.get('user_name'),
             'color': '#000000'
         },
         'keyword2':{
             'value': reservation.get('busi_type'),
             'color': '#000000'
         },
         'keyword3':{
             'value': reservation.get('user_mobile'),
             'color': '#000000'
         },
         'remark':{
             'value': '点击查看详情',
             'color': '#000000'
         }
    }
    for openid in openids:
        input_data = json.dumps({
            'openid': openid,
            'template_id': RESERVATION_TEMPLATE_ID,
            'url': url,
            'content': content,
        })
        redis_conn.lpush('QUEUE:WX:TEMPLATE_MSG', input_data)
    return {'success':True}


def application_feedback(data):
    openid = data.get('openid')
    mode = data.get('mode')
    if mode == 'micro_credit_contract':
        url = get_oauth_url(reverse(APP_NAME+':staticfile', kwargs={'name': 'fshl_download'}))
    else:
        url = get_oauth_url(reverse(APP_NAME+':staticfile', kwargs={'name': 'reservation_status'}))
    content = {
         'first':{
             'value': data.get('busi_type') + '申请反馈',
             'color': '#000000'
         },
         'keyword1':{
             'value': data.get('user_name'),
             'color': '#000000'
         },
         'keyword2':{
             'value': data.get('apply_dtime'),
             'color': '#000000'
         },
         'remark':{
             'value': data.get('msg'),
             'color': '#000000'
         }
    }
    input_data = json.dumps({
        'openid': openid,
        'template_id': APPLICATION_FEEDBACK_TEMPLATE_ID,
        'url': url,
        'content': content,
    })
    redis_conn.lpush('QUEUE:WX:TEMPLATE_MSG', input_data)
    return {'success':True}


def loan_overtime_reminder(data):
    url = get_oauth_url(reverse(APP_NAME+':staticfile', kwargs={'name': 'reservation_deal'}))
    user_name = data.get('user_name')
    apply_dtime = data.get('apply_dtime')
    overtime = data.get('overtime')
    for receiver in data.get('receiver'):
        receiver_name = receiver.get('receiver_name')
        openid = receiver.get('openid')
        msg = '%s, %s的申请已超时%s未作应答，请及时处理' %(receiver_name, user_name, overtime)
        content = {
             'first':{
                 'value': '申请处理超时提醒',
                 'color': '#000000'
             },
             'keyword1':{
                 'value': user_name,
                 'color': '#000000'
             },
             'keyword2':{
                 'value': apply_dtime,
                 'color': '#000000'
             },
             'remark':{
                 'value': msg,
                 'color': '#000000'
             }
        }
        input_data = json.dumps({
            'openid': openid,
            'template_id': APPLICATION_FEEDBACK_TEMPLATE_ID,
            'url': url,
            'content': content,
        })
        redis_conn.lpush('QUEUE:WX:TEMPLATE_MSG', input_data)
    return {'success':True}
