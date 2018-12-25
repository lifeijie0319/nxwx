# coding:utf-8
import json
import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, repitition_deny, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import gen_token


@ensure_csrf_cookie
#@certified_cus_check
@user_register_check
def sign_page(request):
    request.session['handle_flag'] = False
    openid = request.session.get('openid')
    context = send2serv({'path': 'signin.sign_page', 'kargs': {'openid': openid}})
    context['req_token'] = gen_token()
    logger.debug(context)
    return render(request, APP_NAME + '/signin.html', context)


# 获取今日是否签到，总签到次数，总签到积分
def get_signin(request):
    openid = request.session.get('openid')
    context = send2serv({'path': 'signin.get_signin', 'kargs': {'openid':openid}})
    return JsonResponse(context)


# 点击签到按钮后，执行签到操作
@repitition_deny
def signin(request):
    openid = request.session.get('openid')
    logger.debug(request.body)
    post_data = json.loads(request.body)
    logger.debug(post_data)
    req_token = post_data.get('req_token')
    context = send2serv({'path': 'signin.signin', 'kargs': {'openid':openid, 'req_token': req_token}})
    if context.get('success'):
        context['req_token'] = gen_token()
    return JsonResponse(context)
