# -*- coding: utf-8 -*-
"""积分商城模块

该模块用于实现积分商城的展示、购买商品等功能
"""
#promotion.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, repitition_deny, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import download_file, send2serv
from ..tools import gen_token, get_img, get_oauth_url
from ..wx import check_user_subscribed


@ensure_csrf_cookie
@user_register_check
def page(request):
    """视图函数，初始化’积分商城‘首页"""
    openid = request.session.get('openid')
    context = send2serv({'path': 'promotion.page', 'kargs': {'openid': openid}})
    #context['carousel_img1'] = get_img('promotion01', 'carousel_figure')
    #context['carousel_img2'] = get_img('promotion02', 'carousel_figure')
    #context['carousel_img3'] = get_img('promotion03', 'carousel_figure')
    return render(request, APP_NAME + '/promotion.html', context)


@ensure_csrf_cookie
@user_register_check
def all_page(request):
    """视图函数，初始化展示所有优惠券页面"""
    context = send2serv({'path': 'promotion.all_page', 'kargs': {}})
    return render(request, APP_NAME + '/promotion_all.html', context)


@ensure_csrf_cookie
@user_register_check
#@certified_cus_check
def details_page(request):
    """视图函数，初始化优惠券详情页"""
    coupon_id = request.GET.get('id')
    context = send2serv({'path': 'promotion.details_page', 'kargs': {'coupon_id': coupon_id}})
    #context['carousel_img1'] = get_img('coupon_detail01', 'carousel_figure')
    #context['carousel_img2'] = get_img('coupon_detail02', 'carousel_figure')
    coupon = context.get('coupon')
    img_path = '/' + APP_NAME + '/media/coupon/' + coupon_id + '.jpg'
    logger.debug(settings.BASE_DIR + img_path)
    coupon['img_path'] = img_path if os.path.isfile(settings.BASE_DIR + img_path) else None
    return render(request, APP_NAME + '/promotion_details.html', context)


def order_term_check(request):
    openid = request.session.get('openid')
    coupon_id = request.GET.get('coupon_id')
    context = send2serv({'path': 'promotion.order_term_check', 'kargs': {'openid': openid, 'coupon_id': coupon_id}})
    return JsonResponse(context)


@ensure_csrf_cookie
#@certified_cus_check
@user_register_check
def order_page(request):
    """视图函数，初始化优惠券下单页面"""
    request.session['handle_flag'] = False
    openid = request.session.get('openid')
    coupon_id = request.GET.get('id', '')
    context = send2serv({'path': 'promotion.order_page', 'kargs': {'openid': openid, 'coupon_id': coupon_id}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/promotion_order.html', context)


@repitition_deny
def purchase(request):
    """视图函数，用户下单购买优惠券的逻辑"""
    logger.debug('POST: %s', request.POST)
    kargs = {
        'openid': request.session.get('openid'),
        'num': request.POST.get('num'),
        'coupon_id': request.POST.get('id'),
        'req_token': request.POST.get('req_token'),
        'inviter_openid': request.session.get('coupon_inviter'),
        'invitation_couponid': request.session.get('invitation_couponid'),
    }
    context = send2serv({'path': 'promotion.purchase', 'kargs': kargs})
    if context.get('success'):
        context['req_token'] = gen_token()
        if context.get('invitation_completed'):
            del request.session['coupon_inviter']
            del request.session['invitation_couponid']
    return JsonResponse(context)
