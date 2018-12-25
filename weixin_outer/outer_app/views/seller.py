# -*- coding: utf-8 -*-
"""商户管理模块

该模块用于处理商户相关功能
"""
#seller.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os

from datetime import date
from decimal import Decimal
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, repitition_deny, seller_register_check, user_register_check
from ..config import APP_NAME
from ..global_var import cryptor
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import gen_token, get_img_path


@seller_register_check
def info(request):
    openid = request.session.get('openid')
    context = send2serv({'path': 'seller.info', 'kargs': {'openid': openid}})
    return JsonResponse(context)


@ensure_csrf_cookie
@user_register_check
def cooperative_seller_page(request):
    """视图函数，初始化合作商户页面"""
    openid = get_openid(request)
    context = send2serv({'path': 'seller.cooperative_seller_page', 'kargs': {}})
    for shop in context.get('recommended_shops'):
        shop['img_path'] = get_img_path(shop.get('id'), 'shop')
    return render(request, APP_NAME + '/cooperative_seller.html', context)


@ensure_csrf_cookie
def seller_list(request, type_id=1):
    """视图函数，分类显示合作商户"""
    shops = send2serv({'path': 'seller.seller_list', 'kargs': {'type_id': type_id}})
    for shop in shops.get('shops'):
        shop['img_path'] = get_img_path(shop.get('id'), 'shop')
    logger.debug(shops)
    return render(request, APP_NAME + '/cooperative_seller_list.html', shops)


@ensure_csrf_cookie
@seller_register_check
def seller_page(request):
    """视图函数，初始化商户管理页面"""
    request.session['handle_flag'] = False
    openid = get_openid(request)
    context = send2serv({'path': 'seller.seller_page', 'kargs': {'openid': openid}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/seller.html', context)


@seller_register_check
@repitition_deny
def account_modify(request):
    """视图函数，修改店铺绑定的经营者的账户"""
    openid = request.session.get('openid')
    post_data = json.loads(request.body)
    bankcard_no = post_data.get('bankcard_no')
    telephone_no = post_data.get('telephone_no')
    vcode = post_data.get('vcode')
    real_vcode = request.session.get('vcode')
    if not real_vcode:
        return JsonResponse({'success': False, 'msg': u'请先获取验证码'})
    if int(vcode) != int(real_vcode):
        return JsonResponse({'success': False, 'msg': u'验证码不匹配'})
    kargs = {
        'openid': openid,
        'new_account': bankcard_no,
        'telno': telephone_no,
    }
    context = send2serv({'path': 'seller.account_modify', 'kargs': kargs})
    return JsonResponse(context)


@ensure_csrf_cookie
@seller_register_check
def withdraw_apply_page(request):
    """视图函数，初始化提现申请页面"""
    request.session['handle_flag'] = False
    context = send2serv({'path': 'seller.withdraw_apply_page', 'kargs': {}})
    return render(request, APP_NAME + '/withdraw_apply.html', context)


@seller_register_check
@repitition_deny
def withdraw_apply(request):
    """视图函数，处理提交的提现申请"""
    kargs = {
        'openid': request.session.get('openid'),
        'withdraw_credits': request.POST.get('credits'),
        'poundage': request.POST.get('poundage'),
        'ratio': request.POST.get('ratio'),
        'balance': request.POST.get('balance'),
        'receipt_provision': request.POST.get('receiptProvision'),
    }
    context = send2serv({'path': 'seller.withdraw_apply', 'kargs': kargs})
    return JsonResponse(context)


@ensure_csrf_cookie
@seller_register_check
def withdraw_status_page(request):
    """视图函数，初始化‘提现申请状态查询’页面"""
    openid = request.session.get('openid')
    context = send2serv({'path': 'seller.withdraw_status_page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/withdraw_status.html', context)


@seller_register_check
@repitition_deny
def parse_qrcode_str(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    qrcode_str = cryptor.decrypt(request.POST.get('qrcodeStr'))
    qrcode_id = qrcode_str.split('JSON')[0][-8:]
    payload = json.loads(qrcode_str.split('JSON')[1])
    qrcode_openid = payload.get('qrcodeOpenid')
    openid = request.session.get('openid')
    amount = payload.get('amount', '')
    user_coupon_id = payload.get('userCouponId', '')
    if qrcode_openid == openid:
        return JsonResponse({'success': False, 'msg': u'您无法与自己交易'})
    kargs = {
        'qrcode_id': qrcode_id,
        'qrcode_openid': qrcode_openid,
        'openid': openid,
        'amount': amount,
        'user_coupon_id': user_coupon_id,
    }
    context = send2serv({'path': 'seller.parse_qrcode_str', 'kargs': kargs})
    if context.get('success'):
        user_id = context.get('user_id')
        context['img_path'] = get_img_path(user_id, 'user')
    return JsonResponse(context)
