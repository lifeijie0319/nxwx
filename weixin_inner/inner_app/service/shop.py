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

from django.db import transaction

from ..logger import logger
from ..models import Address, Manager, Seller, SellerReplace, Shop, User
from ..tools import to_json


def shop_page(openid):
    seller = Seller.objects.get(openid=openid)
    ret_seller = {
        'name': seller.name,
        'telno': seller.telno,
        'account': seller.account[:4] + '*' * len(seller.account) + seller.account[-4:],
    }
    shop = Shop.objects.filter(seller=seller).first()
    ret_shop = {
        'id': shop.id,
        'name': shop.name,
        'type': shop.type.name,
    }
    return {u'shop': ret_shop, 'seller': ret_seller}


@transaction.atomic
def name_modify(openid, new_name):
    """视图函数，修改商店名称"""
    shop = Shop.objects.get(seller__openid=openid)
    shop.name = new_name
    shop.save()
    return {'success': True}


@transaction.atomic
def seller_replace_query(shop_name, seller_account=None, telno=None):
    shops = Shop.objects.filter(name__contains=shop_name)
    if seller_account:
        shops = shops.filter(seller__account=seller_account)
    if telno:
        shops = shops.filter(seller__telno=telno)
    if len(shops) == 0:
        return ({'success': False, 'msg': '不存在符合条件的商户'})
    elif len(shops) == 1:
        ret_shop = shops.first()
        ret_shop_json = {
            'name': ret_shop.name,
            'seller_name': ret_shop.seller.name,
            'seller_telno': ret_shop.seller.telno,
        }
        return ({'success': True, 'shop': ret_shop_json})
    else:
        return ({'success': False, 'msg': '存在' + len(shops) + '个符合条件的商户，请加强筛选条件'})


@transaction.atomic
def seller_replace_apply(openid, shop_name, new_telno=''):
    shop = Shop.objects.get(name=shop_name)
    if SellerReplace.objects.filter(openid=openid).exclude(status__in=['通过', '驳回']).exists():
        return ({'success': False, 'msg': u'您有相关申请正在处理，请不要重复提交'})

    head_admins = Manager.objects.filter(role=u'总行管理员', status='normal')
    logger.debug(head_admins)
    head_admins_openid = []
    for head_admin in head_admins:
        head_admin_user = User.objects.filter(idcardno=head_admin.idcardno)
        if len(head_admin_user) == 1:
            head_admins_openid.append(head_admin_user.first().openid)
    if not head_admins_openid:
        return {'success': False, 'msg': '不存在可以处理请求的总行管理员'}

    data = {
        'openid': openid,
        'shop': shop,
        'telno': new_telno,
    }
    application = SellerReplace.objects.create(**data)

    data = {
        'name': shop.seller.name,
        'info': '申请更换店铺' + shop_name + '绑定的微信号',
        'apply_datetime': application.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return {'success': True, 'head_admins_openid': head_admins_openid, 'data': data}
