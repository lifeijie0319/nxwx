# -*- coding: utf-8 -*-
"""优惠券模块

该模块用于处理优惠券相关功能
"""
#coupon.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json

from django.db import transaction

from .common import add_trade_detail, credits_usable, query_credits,\
transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import RepetitionExclude, Seller, TransactionDetail, User, UserCoupon,CouponRule,BusiType
from ..tools import generate_orderno


def page(openid):
    #TODO 可能优化
    today = datetime.date.today()
    UserCoupon.objects.filter(status=u'未使用')\
        .filter(coupon__expired_date__lt=today)\
        .update(status=u'已过期')

    user_coupons = UserCoupon.objects.filter(user__openid=openid).filter(status=u'未使用')
    ret_coupons = [{
        'id': user_coupon.id,
        'name': user_coupon.coupon.name,
        'expired_date': user_coupon.coupon.expired_date.strftime('%Y-%m-%d'),
        'discount_type': user_coupon.coupon.discount_type,
    } for user_coupon in user_coupons]
    logger.debug(ret_coupons)
    return {'user_coupons': ret_coupons}


def invalid_page(openid):
    used_coupons = UserCoupon.objects.filter(user__openid=openid).filter(status=u'已使用')
    expired_coupons = UserCoupon.objects.filter(user__openid=openid).filter(status=u'已过期')
    ret_used_coupons = [{
        'user_coupon_id': used_coupon.id,
        'coupon_name': used_coupon.coupon.name,
        'discount_type': used_coupon.coupon.discount_type,
    } for used_coupon in used_coupons]
    ret_expired_coupons = [{
        'user_coupon_id': expired_coupon.id,
        'coupon_name': expired_coupon.coupon.name,
        'discount_type': expired_coupon.coupon.discount_type,
    } for expired_coupon in expired_coupons]
    return {'used_coupons': ret_used_coupons, 'expired_coupons': ret_expired_coupons}


def use_page(user_coupon_id):
    user_coupon = UserCoupon.objects.get(id=user_coupon_id)
    logger.debug(user_coupon)
    ret_coupon = {
        'id': user_coupon.coupon.id,
        'name': user_coupon.coupon.name,
        'credits': user_coupon.coupon.credits,
        'expired_date': user_coupon.coupon.expired_date.strftime('%Y-%m-%d'),
        'discount_type': user_coupon.coupon.discount_type,
        'orderno': user_coupon.in_log.get_orderno(),
    }
    shops = user_coupon.coupon.shops.all()
    ret_shops = [{
        'name': shop.name,
        'address': shop.address.get_str(),
        'seller_telno': shop.seller.telno,
    } for shop in shops]
    return {'coupon': ret_coupon, 'shops': ret_shops}

def check_seller(seller,coupon):
    now = datetime.datetime.now()
    couponrule = CouponRule.objects.all()
    busitype = BusiType.objects.all()
    for rule in couponrule:
        r_time = rule.h_time
        r_time = datetime.timedelta(seconds=r_time)
        r_num = rule.h_num
        b_time = rule.busitype.h_time
        b_time = datetime.timedelta(seconds=b_time)
        b_num = rule.busitype.h_num
        logger.debug('B_NUM:%s',str(b_num))
        logger.debug('R_NUM:%s',str(r_num))
        logger.debug('B_TIME:%s',str(b_time))
        logger.debug('R_TIME:%s',str(r_time))
        recodes = TransactionDetail.objects.filter(type=u'商户扫码兑换收取',trader__openid=seller.openid,trade_datetime__gt=(now-b_time),coupon__id = coupon.id) 
        logger.debug('recodes1:%s',str(recodes.count()))
        if recodes.count()>=b_num:
            return True
        recodes = TransactionDetail.objects.filter(type=u'商户扫码兑换收取',trader__openid=seller.openid,trade_datetime__gt=(now-r_time),coupon__id = coupon.id)
        logger.debug('recodes2:%s',str(recodes.count()))
        if recodes.count()>=r_num:
            return True
    return False

def trade(openid, qrcode_openid, user_coupon_id, amount, req_token):
    user = User.objects.get(openid=qrcode_openid)
    seller = Seller.objects.get(openid=openid)
    user_coupon = UserCoupon.objects.get(id=user_coupon_id)
    coupon = user_coupon.coupon
    logger.debug(coupon.discount_type)
    amount = int(amount)
    user_consume = amount - coupon.value
    user_init_credits = query_credits(qrcode_openid, 'user')
    if user_init_credits < user_consume:
        return {'success': False, 'msg': u'用户的积分不足'}
    if coupon.discount_type == u'满减' and  amount < coupon.discount_startline:
        return {'success': False, 'msg': u'收取的积分未达到满减条件'}
    if coupon.discount_type == u'抵用' and amount <= coupon.value:
        user_consume = 0
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    if user_coupon.status != u'未使用':
        return {'success': False, 'msg': u'优惠券' + user_coupon.status + u'，无法使用'}
    if check_seller(seller,coupon) == True:
        return {'success': False, 'msg': u'商户核销已达上限'}
    with transaction.atomic():
        RepetitionExclude.objects.create(req_token=req_token)
        if user_consume > 0:
            user.credits -= user_consume
            user.save()
        seller.credits += amount
        seller.save()
        shop = seller.shop_set.first()
        shop.trade_times += 1
        shop.save()
        orderno_list = generate_orderno(2)
        user_log = transaction_detail_save(user, seller, -user_consume,\
            u'扫码兑换支付', u'使用优惠券' + coupon.name, orderno_list[0], coupon)
        seller_log = transaction_detail_save(seller, user, amount,\
            u'商户扫码兑换收取', user.name + u'使用优惠券' + coupon.name, orderno_list[1], coupon)
        user_coupon.status = u'已使用'
        user_coupon.out_log = user_log
        user_coupon.save()
    with transaction.atomic(using='old_credits'):
        update_or_insert_credits(user.idcardno, -user_consume)
        add_trade_detail(trade_type=u'扫码兑换支付', idcardno=user.idcardno, name=user.name, \
            credits=user_consume, direction='-', new_credits=query_credits(qrcode_openid, 'user'),\
            orderno = orderno_list[0], goods_name=coupon.name, goods_cost=user_consume, trade_num=1)
    return {'success': True, 'user_log_id': user_log.id, 'seller_log_id': seller_log.id}


def trade_reply(user_log_id=None, seller_log_id=None):
    text = {}
    if user_log_id:
        log = TransactionDetail.objects.get(id=user_log_id)
        text['href'] = '/outer_app/coupon/page/'
        text[u'opposite'] = log.opposite.seller.shop_set.first().name
    elif seller_log_id:
        log = TransactionDetail.objects.get(id=seller_log_id)
        text['href'] = '/outer_app/seller/page/'
        text[u'opposite'] = log.opposite.user.name
    else:
        return {'success': False}
    text['credits'] = log.credits
    text['title'] = u'兑换成功'
    text['date_time'] = log.trade_datetime.strftime('%Y-%m-%d %H:%M:%S')
    text['order_no'] = log.get_orderno()
    text['coupon'] = log.coupon.name
    return text


def use_invalid_page(user_coupon_id):
    """视图函数，初始化无效票券的使用页面"""
    user_coupon = UserCoupon.objects.get(id=user_coupon_id)
    ret_coupon = {
        'id': user_coupon.coupon.id,
        'name': user_coupon.coupon.name,
        'credits': user_coupon.coupon.credits,
        'expired_date': user_coupon.coupon.expired_date.strftime('%Y-%m-%d'),
        'discount_type': user_coupon.coupon.discount_type,
        'orderno': user_coupon.in_log.get_orderno(),
    }
    shops = user_coupon.coupon.shops.all()
    ret_shops = [{
        'name': shop.name,
        'address': shop.address.get_str(),
        'seller_telno': shop.seller.telno,
    } for shop in shops]
    return {'coupon': ret_coupon, 'shops': ret_shops}
