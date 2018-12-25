# -*- coding: utf-8 -*-
"""商户管理模块

该模块用于处理商户相关功能
"""
#seller.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os

from datetime import date
from decimal import Decimal
from django.db import transaction
from django.core.paginator import Paginator
from itertools import chain

from .common import query_credits
from ..credits_api import query_account
from ..logger import logger
from ..models import CommonParam, Seller, Shop, ShopType, User, UserCoupon, WithdrawAppplication


def info(openid):
    seller = Seller.objects.get(openid=openid)
    return {'credits': seller.credits, 'account': seller.account}


def cooperative_seller_page():
    all_types = ShopType.objects.all()
    paginator = Paginator(all_types, 8)
    ret_types = [
        [{'id': item.id, 'name': item.name, 'en_name': item.en_name} for item in paginator.page(i).object_list] 
    for i in range(1, paginator.num_pages + 1)]
    #TODO获取推荐商户
    shops = Shop.objects.filter(status='正常').order_by('-stick').order_by('-trade_times')[:4]
    #sticked_shops = Shop.objects.filter(stick=True)
    #logger.debug(len(sticked_shops))
    #if len(sticked_shops) < 4:
    #    added_shops = Shop.objects.filter(stick=False).order_by('-trade_times')[:4-len(sticked_shops)]
    #    logger.debug(len(added_shops))
    #    recommended_shops = chain(sticked_shops, added_shops)
    #else:
    #    recommended_shops = sticked_shops
    #logger.debug(recommended_shops)
    ret_shops = [{
        'id': shop.id,
        'name': shop.name,
        'address': shop.address.get_str(),
        'seller_tel': shop.seller.telno
    } for shop in shops]
    return {u'shop_types': ret_types, u'recommended_shops': ret_shops}


def seller_list(type_id=1):
    shops = Shop.objects.filter(status='正常').filter(type__id=type_id)
    ret_shops = [{
        'id': shop.id,
        'name': shop.name,
        'address': shop.address.get_str(),
        'seller_tel': shop.seller.telno
    } for shop in shops]
    return {u'shops': ret_shops}


def seller_page(openid):
    credits = query_credits(openid, 'seller')
    return {u'credits': credits}


@transaction.atomic
def account_modify(openid, new_account, telno):
    seller = Seller.objects.get(openid=openid)
    if seller.account == new_account:
        return ({'success': False, 'msg': u'该账（卡）号与原账（卡）号相同，不需要修改'})
    account_info = query_account(new_account)
    if not account_info:
        return {'success': False, 'msg': u'账（卡）号不存在'}
    if telno != seller.telno:
        return {'success': False, 'msg': u'该手机号与注册时的手机号不同'}
    seller.account = new_account
    seller.save()
    return {'success': True}


def withdraw_apply_page():
    """视图函数，初始化提现申请页面"""
    withdraw_params = {}
    withdraw_params[u'poundage_low'] = CommonParam.objects.get(name=u'提现手续费（有发票）').value
    withdraw_params[u'poundage_high'] = CommonParam.objects.get(name=u'提现手续费（无发票）').value
    withdraw_params[u'ratio'] = CommonParam.objects.get(name=u'积分现金兑换比').value
    withdraw_params[u'min_balance'] = CommonParam.objects.get(name=u'提现最低金额').value
    logger.debug('PARAMS: %s', withdraw_params)
    return withdraw_params


@transaction.atomic
def withdraw_apply(openid, withdraw_credits, poundage, ratio, balance, receipt_provision=''):
    seller = Seller.objects.get(openid=openid)
    if WithdrawAppplication.objects.filter(seller=seller, status='待审批').exists():
        return {'success': False, 'msg': '同一时间只能有一笔未处理的提现申请'}
    if int(withdraw_credits) > seller.credits:
        return {'success': False, 'msg': u'您的积分不足，无法通过提现申请'}
    withdraw_apply = {}
    withdraw_apply['seller'] = seller
    withdraw_apply['credits'] = int(withdraw_credits)
    withdraw_apply['poundage'] = Decimal(poundage).quantize(Decimal('0.00'))
    withdraw_apply['ratio'] = int(ratio)
    withdraw_apply['balance'] = Decimal(balance).quantize(Decimal('0.00'))
    withdraw_apply['receipt_provision'] = True if receipt_provision == 'on' else False
    withdraw_apply['status'] = u'待审批'
    withdraw_apply['application_date'] = date.today()
    WithdrawAppplication.objects.create(**withdraw_apply)
    return {'success': True}


def withdraw_status_page(openid):
    def get_logs_dict(logs):
        ret = [{
            'credits': log.credits,
            'poundage': str(log.poundage),
            'ratio': log.ratio,
            'application_date': log.application_date.strftime('%Y-%m-%d'),
            'receipt_provision': log.receipt_provision,
            'audit_date': log.audit_date.strftime('%Y-%m-%d') if log.audit_date else '',
        } for log in logs]
        return ret
    all_logs = WithdrawAppplication.objects.filter(seller__openid=openid)
    logs1 = all_logs.filter(status='待审批')
    logs2 = all_logs.filter(status='已审批')
    logs3 = all_logs.filter(status='未通过')
    ret_logs = {
        'logs1': get_logs_dict(logs1),
        'logs2': get_logs_dict(logs2),
        'logs3': get_logs_dict(logs3),
    }
    logger.debug(ret_logs)
    return ret_logs


def parse_qrcode_str(qrcode_id, qrcode_openid, openid, amount, user_coupon_id=''):
    user = User.objects.get(openid=qrcode_openid)
    seller = Seller.objects.get(openid=openid)
    if user.is_new:
        return {'success': False, 'msg': u'对方用户未绑定，无法交易'}
    if qrcode_id == '00000000':
        if amount:
            if query_credits(qrcode_openid, 'user') < int(amount):
                return ({'success': False, 'msg': u'对方的积分不足'})
            return ({'success': True, 'msg': 'confirm', 'user_id': user.id})
        tips = u'向用户 ' + user.name + u' 收积分'
        return ({'success': True, 'msg': 'set_amount', 'tips': tips, 'user_id': user.id})
    if qrcode_id == '00000003':
        user_coupon = UserCoupon.objects.get(id=user_coupon_id)
        if user_coupon.status != u'未使用':
            return {'success': False, 'msg': u'优惠券' + user_coupon.status + u'，无法继续使用'}
        coupon = user_coupon.coupon
        logger.debug('coupon_name: %s', coupon.name)
        if seller.shop_set.first() not in coupon.shops.all():
            return {'success': False, 'msg': u'该优惠券不能在此商户使用'}
        tips = u'用户 ' + user.name + u' 将要使用优惠券 ' + coupon.name\
            + u'（说明:' + coupon.description + u'）'
        if coupon.fixed_amount > 0:
            return {'success': True, 'msg': 'coupon_confirm', 'tips': tips, 'user_id': user.id, 'amount': coupon.fixed_amount}
        return {'success': True, 'msg': 'coupon_set_amount', 'tips': tips, 'user_id': user.id}
    return ({'success': False, 'msg': u'不匹配的二维码'})
