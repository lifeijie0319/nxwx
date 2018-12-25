# -*- coding: utf-8 -*-
"""积分模块

该模块用于处理积分系统相关功能
"""
#credits.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json
import os
import random
import time
import urllib

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, repitition_deny, user_register_check
from ..config import APP_NAME, WS_TRADE_REPLY_URL
from ..global_var import cryptor, logger
from ..socket_client import send2serv
from ..tools import gen_token, get_img_path, to_json


@ensure_csrf_cookie
@user_register_check
def page(request):
    request.session['handle_flag'] = False
    logger.debug('CSRF_COOKIE: %s', request.META.get('CSRF_COOKIE'))
    """视图函数，初始化‘我的积分‘页面"""
    openid = get_openid(request)
    context = send2serv({'path': 'credits.page', 'kargs': {'openid': openid}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/credits.html', context)


@ensure_csrf_cookie
#@certified_cus_check
@user_register_check
def trade_reply(request):
    """视图函数，初始化交易反馈页面"""
    log_id = request.GET.get('id')
    openid = request.session.get('openid')
    is_scan = request.GET.get('from', '')
    kargs = {
        'openid': openid,
        'log_id': log_id,
        'is_scan': is_scan,
    }
    context = send2serv({'path': 'credits.trade_reply', 'kargs': kargs})
    return render(request, APP_NAME + '/pay_done.html', context)


@repitition_deny
def trade(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    qrcode_str = cryptor.decrypt(request.POST.get('qrcodeStr'))
    qrcode_id = qrcode_str.split('JSON')[0][-8:]
    payload = json.loads(qrcode_str.split('JSON')[1])
    qrcode_openid = payload.get('qrcodeOpenid')
    openid = request.session.get('openid')
    amount = payload.get('amount') if payload.get('amount') else request.POST.get('amount')
    kargs = {
        'openid': openid,
        'qrcode_openid': qrcode_openid,
        'amount': amount,
        'qrcode_id': qrcode_id,
        'req_token': request.POST.get('req_token'),
    }
    context = send2serv({'path': 'credits.trade', 'kargs': kargs})
    if context.get('success'):
        context['req_token'] = gen_token()
        logger.debug('qrcode trade_reply')
        reply_data = {
            'openid': qrcode_openid,
            'text': str(context.get('log_id'))
        }
        reply_data = json.dumps(reply_data, ensure_ascii=False)
        resp = urllib.urlopen(url=WS_TRADE_REPLY_URL, data=reply_data)
        logger.debug(resp)
    return JsonResponse(context)


@ensure_csrf_cookie
@user_register_check
def history_page(request):
    """视图函数，初始化积分明细页面"""
    query_type = request.GET.get('type')
    openid = request.session.get('openid')
    last_id = request.GET.get('last')
    kargs = {
        'query_type': query_type,
        'openid': openid,
        'last_id': last_id if last_id else '',
    }
    context = send2serv({'path': 'credits.history_page', 'kargs': kargs})
    logger.debug(context)
    for log in context.get('ret_history'):
        opposite_id = log.get('opposite_id')
        if log.get('opposite_type') == 'user':
            log['img_path'] = get_img_path(opposite_id, 'user')
        elif log.get('opposite_type') == 'seller':
            log['img_path'] = get_img_path(opposite_id, 'shop')
        else:
            log['img_path'] = '/static/outer_app/images/system.png'
    return render(request, APP_NAME + '/credits_history_list.html', context)


@ensure_csrf_cookie
@user_register_check
def history_details_page(request):
    """视图函数，初始化积分明细详情页面"""
    id = request.GET.get('id')
    context = send2serv({'path': 'credits.history_details_page', 'kargs': {'id': id}})
    return render(request, APP_NAME + '/credits_history_detail.html', context)
