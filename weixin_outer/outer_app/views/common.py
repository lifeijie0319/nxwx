# -*- coding: utf-8 -*-
"""通用视图函数

该模块用于定义一些公用的，不能轻易归类的视图函数
"""
# common.py
#
# Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
# All rights reserved
#
__author__ = "lifeijie <lifeijie@yinsho.com>"

import json
import multiprocessing
import random
import time

from datetime import datetime
from django.core.urlresolvers import resolve
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from ..config import APP_NAME
from ..global_var import cryptor, logger, redis_conn
from ..socket_client import send2serv
from ..tools import get_img, get_oauth_url
from ..wx import oauth_get_openid, weixin_jssdk


def favicon(request, name, extension):
    with open(name + '.' + extension) as f:
        ret = f.read()
    return HttpResponse(ret)


# @csrf_exempt
def jssdk(request):
    logger.debug('url: %s', request.body)
    url = json.loads(request.body).get('url')
    return JsonResponse(weixin_jssdk(url))


def send_vcode(request):
    """视图函数，发送验证码"""
    telphone_no = request.body
    openid = request.session.get('openid')
    if not openid:
        return JsonResponse({'success': False, 'msg': '不能获取到openid'})
    ret = send2serv({'path': 'common.send_vcode', 'kargs': {'openid': openid}})
    if not ret.get('success'):
        return JsonResponse({'success': False, 'msg': '今天获取验证码次数达到上限'})
    vcode = random.randint(100000, 999999)
    logger.debug('TEL_NO: %s', telphone_no)
    logger.debug('VCODE: %s', vcode)
    request.session['vcode'] = vcode
    data = {
        'telno': telphone_no,
        'vcode': vcode,
    }
    send2serv({'path': 'common.send_vcode', 'kargs': {'openid': openid, 'data': data}})
    redis_conn.lpush('SMS_QUEUE', json.dumps(data))
    logger.debug('END VCODE')
    return JsonResponse({'success': True, 'msg': 'success'})


def check_vcode(request):
    post_data = json.loads(request.body)
    vcode = post_data.get('vcode')
    real_vcode = request.session.get('vcode')
    if int(vcode) != int(real_vcode):
        return JsonResponse({'success': False})
    request.session['vcode'] = '-1'
    return JsonResponse({'success': True})


def fetch_openid(request):
    openid = get_openid(request)
    return JsonResponse({'openid': openid})


def get_openid(request):
    logger.info('ENTER GET_OPENID')
    logger.info('SESSION: %s', request.session.items())
    openid = request.session.get('openid')
    if not openid:
        code = request.GET.get('code')
        if code:
            openid = oauth_get_openid(code)
        logger.info('FINAL OPENID: %s', openid)
        request.session['openid'] = openid
    return openid


def get_qrcode_str(request):
    logger.debug('GET %s', request.GET)
    qrcode_id = request.GET.get('qrcodeId')
    data = request.GET.copy()
    data.pop('qrcodeId')
    logger.debug(data)
    openid = request.session.get('openid')
    data['qrcodeOpenid'] = openid
    qrcode_str = 'YSWB0001' + qrcode_id + 'JSON' + json.dumps(data)
    logger.debug('QRCODE: %s', qrcode_str)
    qrcode_str = cryptor.encrypt(qrcode_str)
    logger.debug('CRYPTED QRCODE: %s', qrcode_str)
    return JsonResponse({'qrcode_str': qrcode_str, 'openid': openid})


def get_server_time(request):
    resp = time.strftime('%Y-%m-%dT%H:%M', time.localtime(time.time()))
    return HttpResponse(resp)


def user_register_check(view_func):
    def wrapper(request, *args, **kargs):
        openid = get_openid(request)
        if not openid:
            return redirect(get_oauth_url(reverse(APP_NAME + ':credits_page')))
        context = send2serv({'path': 'common.user_register_check', 'kargs': {'openid': openid}})
        if context.get('registered'):
            return view_func(request, *args, **kargs)
        else:
            return render(request, APP_NAME + '/register.html')

    return wrapper


def seller_register_check(view_func):
    def wrapper(request, *args, **kargs):
        openid = get_openid(request)
        context = send2serv({'path': 'common.seller_register_check', 'kargs': {'openid': openid}})
        if context.get('status') == 'registered':
            return view_func(request, *args, **kargs)
        elif context.get('status') == 'seller_auditing':
            return redirect('/' + APP_NAME + '/staticfile/done/?from=seller_auditing')
        elif context.get('status') == 'seller_replace_auditing':
            return redirect('/' + APP_NAME + '/staticfile/done/?from=seller_replace_auditing')
        else:
            return redirect(APP_NAME + ':register_seller')

    return wrapper


def certified_cus_check(view_func):
    def wrapper(request, *args, **kargs):
        openid = get_openid(request)
        context = send2serv({'path': 'user.get_user', 'kargs': {'openid': openid}})
        if context.get('is_new') == 'yes':
            binding_url = reverse(APP_NAME + ':user_binding')
            next_url = request.path_info
            return redirect(binding_url + '?next=' + next_url)
        else:
            return view_func(request, *args, **kargs)

    return wrapper


def is_manager_check(view_func):
    def wrapper(request, *args, **kargs):
        openid = get_openid(request)
        context = send2serv({'path': 'user.info_page', 'kargs': {'openid': openid}})
        user = context.get('user')
        if user.get('is_manager'):
            return view_func(request, *args, **kargs)
        else:
            return render(request, APP_NAME + '/todo.html')

    return wrapper


def repitition_deny(view_func):
    def wrapper(request, *args, **kargs):
        if request.session.get('handle_flag', False):
            return JsonResponse({'success': False, 'msg': '请勿重复提交'})
        request.session['handle_flag'] = True
        res = view_func(request, *args, **kargs)
        request.session['handle_flag'] = False
        return res

    return wrapper


@ensure_csrf_cookie
@user_register_check
def static(request, name):
    """视图函数，返回静态html"""
    logger.debug('STATICFILE: %s', name)
    return render(request, APP_NAME + '/' + name + u'.html')
