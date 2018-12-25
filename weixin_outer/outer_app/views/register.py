# -*- coding:utf-8 -*-
"""注册模块

该模块用于实现用户、商户的注册
"""
#register.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json

from django.http import JsonResponse,HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..template_msg import seller_registration_apply
from ..tools import get_and_delete


@ensure_csrf_cookie
def page(request):
    return render(request, APP_NAME + '/register.html')


def get_protocol(request):
    """视图函数，获取注册协议内容"""
    with open(APP_NAME + '/doc/protocol.txt', 'r') as f:
        protocol = f.read()
    #logger.debug('PROTOCOL: %s', protocol)
    return JsonResponse({'protocol': protocol})


def user_register(request):
    """视图函数，处理用户注册请求"""
    logger.info('visitor ip: %s', request.META.get('HTTP_X_FORWARDED_FOR'))
    logger.info('USER REGISTER: %s, %s', request.body, type(request.body))
    post_data = json.loads(request.body)

    vcode = post_data.get('user_vcode')
    real_vcode = request.session.get('vcode')
    if int(vcode) != int(real_vcode):
        return JsonResponse({u'msg': u'验证码不匹配'})

    openid = request.session.get('openid')
    logger.debug('OPENID: %s', openid)
    user_name = post_data.get('user_name')
    user_id = post_data.get('user_id')
    user_tel = post_data.get('user_tel')
    new_cus = post_data.get('new_cus')
    update_flag = post_data.get('update_flag')
    invited = 'no'

    inviter_openid = request.session.get('register_inviter')
    if inviter_openid:
        logger.debug('SESSION: %s', request.session.items())
        invited = 'yes'
    register_kargs = {
        'user_name': user_name,
        'user_id': user_id,
        'user_tel': user_tel,
        'openid': str(openid),
        'inviter_openid': inviter_openid,
        'new_cus': new_cus,
        'update_flag': update_flag,
    }

    registration = send2serv({'path': 'register.user_register', 'kargs': register_kargs})
    if inviter_openid and registration.get('success'):
        del request.session['register_inviter']
        logger.debug('SESSION: %s', request.session.items())
    logger.debug(registration)
    return JsonResponse(registration)


def seller_register(request):
    """视图函数，处理商户注册

    处理经营者信息部分，暂时存入session
    """
    if request.method == 'GET':
        return render(request, APP_NAME + '/seller_register_tips.html')
    logger.debug('BODY: %s', request.body)
    #数据获取
    post_data = json.loads(request.body)
    vcode = post_data.get('vcode')
    real_vcode = request.session.get('vcode')
    if not real_vcode:
        return JsonResponse({'msg': u'请先获取验证码'})
    if int(vcode) != int(real_vcode):
        return JsonResponse({'msg': u'验证码不匹配'})
    openid = request.session.get('openid')
    name = post_data.get('name')
    bankcard_no = post_data.get('bankcard_no')
    teller_no = post_data.get('teller_no')
    telephone_no = post_data.get('telephone_no')
    #校验
    register_kargs = {
        'openid': openid,
        'name': name,
        'bankcard_no': bankcard_no,
        'teller_no': teller_no,
        'telephone_no': telephone_no,
    }
    registration = send2serv({'path': 'register.seller_register', 'kargs': register_kargs})
    #数据存入session
    request.session['seller_name'] = name
    request.session['seller_tel_no'] = telephone_no
    request.session['seller_account_no'] = bankcard_no
    request.session['seller_teller_no'] = teller_no
    return JsonResponse(registration)


@ensure_csrf_cookie
def seller_register2_page(request):
    """视图函数，初始化商户注册店铺信息页面"""
    context = send2serv({'path': 'register.seller_register2_page', 'kargs': {}})
    return render(request, APP_NAME + '/seller_register2.html', context)


def seller_register2(request):
    """视图函数，处理商户注册

    处理店铺信息部分，整合第一步的经营者信息，存入数据库
    """
    openid = request.session.get('openid')
    #构造经营者seller对象，存入数据库
    logger.debug('SESSION: %s', request.session.items())
    name = get_and_delete(request.session, 'seller_name')
    tel_no = get_and_delete(request.session, 'seller_tel_no')
    account_no = get_and_delete(request.session, 'seller_account_no')
    teller_no = get_and_delete(request.session, 'seller_teller_no')
    #解析商店数据
    post_data = json.loads(request.body)
    logger.debug('POST: %s', post_data)
    shop_name = post_data.get('name')
    shop_type = post_data.get('shop_type')
    #地址数据处理
    address_pcc = post_data.get('address_pcc')
    province = address_pcc.split(' ')[0]
    city = address_pcc.split(' ')[1]
    county = address_pcc.split(' ')[2]
    address_tv = post_data.get('address_tv')
    town = address_tv.split(' ')[0]
    village = address_tv.split(' ')[1]
    if town == u'不选择':
        town = ''
        village = ''
    address_detail = post_data.get('address_detail')
    kargs = {
        'openid': openid,
        'name': name,
        'tel_no': tel_no,
        'account_no': account_no,
        'teller_no': teller_no,
        'shop_name': shop_name,
        'shop_type': shop_type,
        'province': province,
        'city': city,
        'county': county,
        'town': town,
        'village': village,
        'address_detail': address_detail,
    }
    context = send2serv({'path': 'register.seller_register2', 'kargs': kargs})
    if context.get('success'):
        head_admins_openid = context.get('head_admins_openid')
        data = context.get('data')
        seller_registration_apply(head_admins_openid, data)
    return JsonResponse(context)
