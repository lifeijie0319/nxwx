# -*- coding: utf-8 -*-
"""分享邀请模块

该模块用于处理微信分享推广相关功能
"""
#invitation.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import requests

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, user_register_check
from ..config import APP_NAME, SUBSCRIBE_URL
from ..tools import get_oauth_url
from ..global_var import logger
from ..socket_client import send2serv
from ..wx import check_user_subscribed


@ensure_csrf_cookie
#@certified_cus_check
@user_register_check
def register_page(request):
    """视图函数，初始化’推荐送积分‘页面"""
    openid = request.session.get('openid')
    context = send2serv({'path': 'invitation.register_page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/invitation.html', context)


def ranking_list(request):
    logger.debug(request.POST)
    context = send2serv({'path': 'invitation.ranking_list', 'kargs': request.POST})
    logger.debug(context)
    html = render_to_string(APP_NAME + '/ranking_list.html', context)
    return JsonResponse({'html': html})


@ensure_csrf_cookie
def register_pre(request):
    """视图函数, 前台跳转，让用户进行oauth验证"""
    inviter_openid = request.GET.get('inviter')
    request.session['register_inviter'] = inviter_openid
    logger.debug(request.session.items())
    url = get_oauth_url('/' + APP_NAME + '/invitation/register/')
    return HttpResponse('<html><script>window.location.href="' + url + '"</script></html>')


@ensure_csrf_cookie
def register(request):
    logger.debug('SESSION: %s', request.session.items())
    """视图函数,根据用户状态，引导其进入对应页面"""
    openid = get_openid(request)
    inviter_openid = request.session.get('register_inviter')
    logger.debug('INVITOR: %s', inviter_openid)
    if openid == inviter_openid:
        return HttpResponse('您不能使用您自己分享出去的链接')
    subscribed = check_user_subscribed(openid)
    logger.debug('%s, %s', type(subscribed), subscribed)
    if subscribed == 0:
        #res = requests.get('https://mp.weixin.qq.com/s/_1lCxjaxERbVy-qXPBlnRQ', verify=False)
        #logger.debug('NEWS: %s', res.text)
        return HttpResponse('''
            <html>
                <script>
                    window.location.href="''' + SUBSCRIBE_URL + '''";
                </script>
            </html>''')
        #return render(request, APP_NAME + '/invitation_lead.html')
    registered = send2serv({'path': 'common.user_register_check', 'kargs': {'openid': str(openid)}})
    logger.debug(registered)
    if not registered.get('registered'):
        return render(request, APP_NAME + '/register.html')
    return HttpResponseRedirect('/' + APP_NAME + '/credits/page/')


@ensure_csrf_cookie
def coupon_pre(request):
    id = request.GET.get('id')
    inviter_openid = request.GET.get('inviter')
    url = get_oauth_url('/' + APP_NAME + '/invitation/coupon/?id=' + id)
    request.session['register_inviter'] = inviter_openid
    request.session['coupon_inviter'] = inviter_openid
    request.session['invitation_couponid'] = id
    logger.debug('SET PROMOTION_INVITOR: %s', request.session.get('coupon_inviter'))
    logger.debug('URL: %s', url)
    return HttpResponse('''
        <html>
            <script>
                window.location.href="''' + url + '''"
            </script>
        </html>''')


@ensure_csrf_cookie
def coupon(request):
    inviter_openid = request.session.get('coupon_inviter')
    openid = get_openid(request)
    if openid == inviter_openid:
        return HttpResponse('您不能使用您自己分享出去的链接')
    subscribed = check_user_subscribed(openid)
    if subscribed == 0:
        return HttpResponse('''
        <html>
            <script>
                window.location.href="''' + SUBSCRIBE_URL + '''";
            </script>
        </html>''')
    registered = send2serv({'path': 'common.user_register_check', 'kargs': {'openid': str(openid)}})
    logger.debug(registered)
    if not registered.get('registered'):
        return render(request, APP_NAME + '/register.html')
    id = request.GET.get('id')
    return HttpResponseRedirect('/' + APP_NAME + '/promotion/details/page/?id=' + id)
