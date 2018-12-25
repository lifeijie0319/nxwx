# -*- coding: utf-8 -*-
"""地址应用模块

该模块用于从数据库取出地址树并作为数据源提供给前台。
"""
#address.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv


def get_region_json(request):
    """视图函数，返回json地址树"""
    start_node_name = request.POST.get('name')
    end_level = request.POST.get('level')
    kargs = {
        'start_node_name': start_node_name,
        'end_level': end_level,
    }
    context = send2serv({'path': 'address.get_region_json', 'kargs': kargs})
    return JsonResponse(context)


@ensure_csrf_cookie
@user_register_check
def modify_page(request):
    """视图函数，返回初始化地址修改页面"""
    from_page = request.GET.get('from')
    logger.debug('FROM: %s', from_page)
    openid = request.session.get('openid')
    kargs = {
        'from_page': from_page,
        'openid': openid,
        'start_node_code': '330000000000',
        'end_level': 'county',
    }
    context = send2serv({'path': 'address.modify_page', 'kargs': kargs})
    return render(request, APP_NAME + '/address_modify.html', context)


def modify(request):
    """视图函数，根据请求修改用户/商户地址"""
    logger.debug('POST: %s', request.POST)
    from_page = request.POST.get('from')
    openid = request.session.get('openid')
    id = request.POST.get('id')
    #地址解析
    address = {}
    address_pcc = request.POST.get('addressPcc')
    province = address_pcc.split(' ')[0]
    city = address_pcc.split(' ')[1]
    county = address_pcc.split(' ')[2]
    address_tv = request.POST.get('addressTv')
    town = address_tv.split(' ')[0]
    town = town if town != '不选择' else None
    village = address_tv.split(' ')[1]
    village = village if village != '不选择' else None
    address_detail = request.POST.get('addressDetail')
    kargs = {
        'from_page': from_page,
        'openid': openid,
        'id': id,
        'province': province,
        'city': city,
        'county': county,
        'town': town,
        'village': village,
        'address_detail': address_detail,
    }
    context = send2serv({'path': 'address.modify', 'kargs': kargs})
    return JsonResponse(context)
