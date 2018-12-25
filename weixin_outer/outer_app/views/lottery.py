# -*- coding:utf-8 -*-
'''抽奖业务逻辑代码

主要是大转盘抽奖的业务逻辑在后台生成是否中奖的随机数，
通过判定随机数与数据库中存储的中奖率的对应奖励条件是否相等来执行抽奖操作

'''
# views/lottery - pooling code for psycopg
#
# Copyright (C) 2017 liuchuang  <fog@debian.org>
#
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, certified_cus_check, repitition_deny, user_register_check
from ..config import APP_NAME
from ..socket_client import send2serv
from ..tools import gen_token


@ensure_csrf_cookie
#@certified_cus_check
@user_register_check
def lottery_page(request):
    #request.session['handle_flag'] = False
    openid = get_openid(request)
    context = send2serv({'path': 'lottery.lottery_page', 'kargs': {'openid': openid}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME +'/lottery.html', context)


#@repitition_deny
def lottery_submit(request):
    openid = request.session.get('openid')
    req_token = request.POST.get('req_token')
    context = send2serv({'path': 'lottery.lottery_submit', 'kargs': {'openid': openid, 'req_token': req_token}})
    if context.get('success'):
        context['req_token'] = gen_token()
    return JsonResponse(context)


def lottery_set(request):
    openid = request.session.get('openid')
    set = send2serv({'path':'lottery.lottery_set','kargs':{'openid':openid}})
    return JsonResponse(set)


@ensure_csrf_cookie
# 点击抽奖记录后通过此路由返回抽奖结果。
@user_register_check
def lottery_detail(request):
    openid =request.session.get('openid') 
    context = send2serv({'path':'lottery.lottery_detail','kargs':{'openid':openid}})
    return render(request, APP_NAME +'/lottery_details.html', context)
