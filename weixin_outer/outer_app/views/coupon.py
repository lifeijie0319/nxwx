# -*- coding: utf-8 -*-
"""优惠券模块

该模块用于处理优惠券相关功能
"""
#coupon.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import urllib

#from channels import Group
from django.http import JsonResponse
from django.shortcuts import render

from .common import certified_cus_check, get_openid, repitition_deny, user_register_check
from ..config import APP_NAME, WS_TRADE_REPLY_URL
from ..global_var import cryptor
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import gen_token


#@certified_cus_check
@user_register_check
def page(request):
    """视图函数，初始化‘我的票券’页面"""
    openid = request.session.get('openid')
    context = send2serv({'path': 'coupon.page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/my_coupon.html', context)


#@certified_cus_check
@user_register_check
def invalid_page(request):
    """视图函数，初始化'我的票券'-'无效票券'页面"""
    openid = request.session.get('openid')
    context = send2serv({'path': 'coupon.invalid_page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/my_coupon_invalid.html', context)


#@certified_cus_check
@user_register_check
def use_page(request):
    """视图函数，初始化有效票券的使用页面"""
    request.session['handle_flag'] = False
    user_coupon_id = request.GET.get('user_coupon_id')
    logger.debug('USER_COUPON_ID: %s', user_coupon_id)
    context = send2serv({'path': 'coupon.use_page', 'kargs': {'user_coupon_id': user_coupon_id}})
    return render(request, APP_NAME + '/my_coupon_use.html', context)


@repitition_deny
def trade(request):
    """用户实际使用优惠券交易处理流程"""
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    qrcode_str = cryptor.decrypt(request.POST.get('qrcodeStr'))
    payload = json.loads(qrcode_str.split('JSON')[1])
    openid = request.session.get('openid')
    qrcode_openid = payload.get('qrcodeOpenid')
    user_coupon_id = payload.get('userCouponId')
    logger.debug('user_coupon_id: %s', user_coupon_id)
    amount = int(request.POST.get('amount'))
    kargs = {
        'openid': openid,
        'qrcode_openid': qrcode_openid,
        'user_coupon_id': user_coupon_id,
        'amount': amount,
        'req_token': request.POST.get('req_token'),
    }
    context = send2serv({'path': 'coupon.trade', 'kargs': kargs})
    if context.get('success'):
        context['req_token'] = gen_token()
        logger.debug('qrcode trade_reply')
        #Group(qrcode_openid).send({'text': str(context.get('user_log_id'))})
        reply_data = {
            'openid': qrcode_openid,
            'text': str(context.get('user_log_id'))
        }
        reply_data = json.dumps(reply_data, ensure_ascii=False)
        resp = urllib.urlopen(url=WS_TRADE_REPLY_URL, data=reply_data)
        logger.debug(resp)
    return JsonResponse(context)


#@certified_cus_check
@user_register_check
def trade_reply(request):
    """视图函数，初始化交易成功反馈信息页面"""
    user_log_id = request.GET.get('user_log_id')
    seller_log_id = request.GET.get('seller_log_id')
    openid = request.session.get('openid')
    is_scan = request.GET.get('from')
    kargs = {
        'user_log_id': user_log_id,
        'seller_log_id': seller_log_id,
    }
    context = send2serv({'path': 'coupon.trade_reply', 'kargs': kargs})
    return render(request, APP_NAME + '/pay_done.html', context)


#@certified_cus_check
@user_register_check
def use_invalid_page(request):
    """视图函数，初始化无效票券的使用页面"""
    user_coupon_id = request.GET.get('user_coupon_id')
    context = send2serv({'path': 'coupon.use_invalid_page', 'kargs': {'user_coupon_id': user_coupon_id}})
    return render(request, APP_NAME + '/my_coupon_use_invalid.html', context)
