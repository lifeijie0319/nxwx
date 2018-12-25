# -*- coding: utf-8 -*-
"""商店模块

该模块用于处理商店相关功能
"""
#load_region.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os
import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, repitition_deny, seller_register_check
from ..config import APP_NAME
from ..global_var import logger, redis_conn
from ..socket_client import send2serv
from ..template_msg import seller_replace_apply_msg
from ..tools import get_img_path, to_json
from ..wx import get_tmp_media


@ensure_csrf_cookie
@seller_register_check
def shop_page(request):
    """视图函数，初始化商店页面"""
    request.session['handle_flag'] = False
    openid = get_openid(request)
    context = send2serv({'path': 'shop.shop_page', 'kargs': {'openid': openid}})
    shop = context.get('shop')
    shop['img_path'] = get_img_path(shop.get('id'), 'shop')
    return render(request, APP_NAME + '/shop.html', context)


@seller_register_check
@repitition_deny
def name_modify(request):
    """视图函数，修改商店名称"""
    logger.debug('BODY: %s', request.body)
    logger.debug('POST: %s', request.POST)
    new_name = request.POST.get('name')
    logger.debug('%s, %s', type(new_name), new_name)
    openid = request.session.get('openid')
    context = send2serv({'path': 'shop.name_modify', 'kargs': {'openid': openid, 'new_name': new_name}})
    return JsonResponse(context)


@seller_register_check
def photo(request):
    """视图函数，更换店铺头像"""
    shop_id = request.POST.get('shop_id')
    mediaid = request.POST.get('mediaid')
    res_pic = get_tmp_media(mediaid)
    pic = res_pic.content
    logger.debug('WITING SHOP PHOTO: %s', APP_NAME + '/media/shop/' + str(shop_id) + '.jpg')
    with open(APP_NAME + '/media/shop/' + str(shop_id) + '.jpg', 'wb') as f:
        f.write(pic)
    return JsonResponse({'success': True})


@seller_register_check
def seller_replace_query(request):
    post_data = json.loads(request.body)
    shop_name = post_data.get('name')
    seller_account = post_data.get('bankcard_no')
    telno = post_data.get('telephone_no')
    kargs = {
        'shop_name': shop_name,
        'seller_account': seller_account,
        'telno': telno,
    }
    context = send2serv({'path': 'shop.seller_replace_query', 'kargs': kargs})
    return JsonResponse(context)


@seller_register_check
@repitition_deny
def seller_replace_apply(request):
    openid = get_openid(request)
    logger.debug(request.POST)
    shop_name = request.POST.get('shop_name')
    new_telno = request.POST.get('new_telno_show')
    kargs = {
        'openid': openid,
        'shop_name': shop_name,
        'new_telno': new_telno if new_telno else '',
    }
    context = send2serv({'path': 'shop.seller_replace_apply', 'kargs': kargs})
    if context.get('success'):
        head_admins_openid = context.get('head_admins_openid')
        data = context.get('data')
        seller_replace_apply_msg(head_admins_openid, data)
    return JsonResponse(context)
