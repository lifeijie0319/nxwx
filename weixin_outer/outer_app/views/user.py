# -*- coding: utf-8 -*-
"""用户模块

该模块用于处理用户相关的功能
"""
#user.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, repitition_deny, user_register_check
from ..config import APP_NAME
from ..global_var import cryptor
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import get_img_path
from ..wx import get_tmp_media


def get_user(request):
    """视图函数，获取用户相关信息"""
    openid_get = request.GET.get('openid')
    openid = openid_get if openid_get else request.session.get('openid')
    user = send2serv({'path': 'user.get_user', 'kargs': {'openid': openid}})
    user['img_path'] = get_img_path(user.get('id'), 'user')
    return JsonResponse(user)


@ensure_csrf_cookie
@user_register_check
def info_page(request):
    """视图函数，初始化’我的信息‘页面"""
    request.session['handle_flag'] = False
    openid = get_openid(request)
    context = send2serv({'path': 'user.info_page', 'kargs': {'openid': openid}})
    user = context.get('user')
    user['img_path'] = get_img_path(user.get('id'), 'user')
    #logger.debug(context)
    return render(request, APP_NAME + '/my_info.html', context)
 

def photo(request):
    """视图函数，更换用户头像"""
    openid = request.session.get('openid')
    user = send2serv({'path': 'user.photo', 'kargs': {'openid': openid}})
    mediaid = request.POST.get('mediaid')
    res_pic = get_tmp_media(mediaid)
    pic = res_pic.content
    logger.debug('WRITING: %s', (APP_NAME + '/media/user/' + str(user.get('id')) + '.jpg', 'wb'))
    with open(APP_NAME + '/media/user/' + str(user.get('id')) + '.jpg', 'wb') as f:
        logger.debug(f)
        f.write(pic)
    return JsonResponse({'success': True})


@ensure_csrf_cookie
@user_register_check
def payment_password_modify_page(request):
    """视图函数，初始化密码修改页面"""
    request.session['handle_flag'] = False
    openid = request.session.get('openid')
    context = send2serv({'path': 'user.payment_password_modify_page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/payment_password_modify.html', context)


@repitition_deny
def payment_password_modify(request):
    """视图函数，修改用户密码"""
    logger.debug('POST: %s', request.POST)
    old_password = request.POST.get('old_password', '')
    new_password = request.POST.get('new_password')
    logger.debug('OLD PASSWORD: %s', old_password)
    logger.debug('NEW PASSWORD: %s', new_password)
    openid = request.session.get('openid')
    kargs = {'openid': openid, 'old_password': old_password, 'new_password': new_password}
    context = send2serv({'path': 'user.payment_password_modify', 'kargs': kargs})
    return JsonResponse(context)


def payment_password_fetch(request):
    """视图函数，检测是否需要验证密码"""
    openid = request.session.get('openid')
    amount = request.GET.get('amount', '')
    context = send2serv({'path': 'user.payment_password_fetch', 'kargs': {'openid': openid, 'amount': amount}})
    return JsonResponse(context)


def payment_password_verify(request):
    """视图函数，验证输入密码与用户密码是否匹配"""
    openid = request.session.get('openid')
    verifying_password = request.GET.get('password')
    kargs = {'openid': openid, 'verifying_password': verifying_password}
    context = send2serv({'path': 'user.payment_password_verify', 'kargs': kargs})
    return JsonResponse(context)


@repitition_deny
def parse_qrcode_str(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    qrcode_str = cryptor.decrypt(request.POST.get('qrcodeStr'))
    logger.debug('QRCODE: %s', qrcode_str)
    qrcode_id = qrcode_str.split('JSON')[0][-8:]
    payload = json.loads(qrcode_str.split('JSON')[1])
    qrcode_openid = payload.get('qrcodeOpenid')
    openid = request.session.get('openid')
    if qrcode_openid == openid:
        return JsonResponse({'success': False, 'msg': u'您无法与自己交易'})
    amount = payload.get('amount', '')
    kargs = {
        'openid': openid,
        'qrcode_openid': qrcode_openid,
        'qrcode_id': qrcode_id,
        'amount': amount,
    }
    context = send2serv({'path': 'user.parse_qrcode_str', 'kargs': kargs})
    if context.get('success'):
        opposite_type = context.get('opposite_type')
        opposite_id = context.get('opposite_id')
        context['img_path'] = get_img_path(opposite_id, opposite_type)
    return JsonResponse(context)


@user_register_check
@repitition_deny
def binding(request):
    """视图函数，处理新用户绑定请求"""
    openid = get_openid(request)
    logger.debug('OPENID: %s', openid)

    if request.method == 'GET':
        context = send2serv({'path': 'user.get_user', 'kargs': {'openid': openid}})
        return render(request, APP_NAME + '/binding.html', context)

    logger.debug('%s, %s', request.body, type(request.body))
    post_data = json.loads(request.body)

    user_name = post_data.get('user_name')
    user_id = post_data.get('user_id')
    user_tel = post_data.get('user_tel')

    register_kargs = {
        'user_name': user_name,
        'user_id': user_id,
        'user_tel': user_tel,
        'openid': openid,
    }

    binding = send2serv({'path': 'user.binding', 'kargs': register_kargs})
    logger.debug(binding)
    return JsonResponse(binding)
