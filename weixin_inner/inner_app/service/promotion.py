# -*- coding: utf-8 -*-
"""积分商城模块

该模块用于实现积分商城的展示、购买商品等功能
"""
#promotion.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json

from django.db import transaction

from .common import add_trade_detail, coupon_term_check, credits_usable,\
query_credits, transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import CommonParam, Coupon, CouponInvitation, RepetitionExclude, User, UserCoupon
from ..tools import generate_orderno


def page(openid):
    """视图函数，初始化’积分商城‘首页"""
    user = User.objects.get(openid=openid)
    ret_user = {
        'id': user.id,
        'name': user.name,
        'credits': query_credits(openid, 'user'),
        'is_new': user.is_new,
    }
    today = datetime.date.today()
    coupons = Coupon.objects.filter(on_date__lte=today)\
        .filter(off_date__gte=today).order_by('soldnum')[:4]
    ret_coupons = [{
        'id': coupon.id,
        'name': coupon.name,
        'credits': coupon.credits,
        'discount_type': coupon.discount_type,
    } for coupon in coupons]
    return {'user': ret_user, 'coupons': ret_coupons}


def all_page():
    today = datetime.date.today()
    coupons = Coupon.objects.filter(on_date__lte=today)\
        .filter(off_date__gte=today)
    ret_coupons = [{
        'id': coupon.id,
        'name': coupon.name,
        'credits': coupon.credits,
        'discount_type': coupon.discount_type,
    } for coupon in coupons]
    return {'coupons': ret_coupons}

    
def details_page(coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    ret_coupon = {
        'name': coupon.name,
        'description': coupon.description,
        'credits': coupon.credits,
        'limit': coupon.limit,
        'soldnum': coupon.soldnum,
        'leftnum': coupon.leftnum,
        'on_date': coupon.on_date.strftime('%Y年%m月%d日'),
        'off_date': coupon.off_date.strftime('%Y年%m月%d日'),
        'expired_date': coupon.expired_date.strftime('%Y年%m月%d日'),
        'term1': coupon.term1.get_str() if coupon.term1 else None,
        'term2': coupon.term2.get_str() if coupon.term2 else None,
        'term_relation': coupon.term_relation,
    }
    shops = coupon.shops.all()
    ret_shops = [{
        'name': shop.name,
        'address': shop.address.get_str(),
        'seller_telno': shop.seller.telno,
    } for shop in shops]
    return {'coupon': ret_coupon, 'shops': ret_shops}


def order_term_check(openid, coupon_id):
    user = User.objects.get(openid=openid)
    coupon = Coupon.objects.get(id=coupon_id)
    cur_num = UserCoupon.objects.filter(user=user, coupon=coupon).count()
    if coupon.limit > 0 and cur_num == coupon.limit:
        return {'success': False, 'msg': '达到优惠券购买数量上限'}
    if coupon.credits > 0 and query_credits(openid, 'user') < coupon.credits:
        return {'success': False, 'msg': '您的积分不足'}
    term1_satisfied = coupon_term_check(user.idcardno, coupon.term1.code) if coupon.term1 else True
    term2_satisfied = coupon_term_check(user.idcardno, coupon.term2.code) if coupon.term2 else True
    if coupon.term1 and coupon.term2:
        if coupon.term_relation == 'or':
            if not term1_satisfied and not term2_satisfied:
                return {'success': False, 'msg': '条件1和条件2均不满足'}
        elif not term1_satisfied:
            return {'success': False, 'msg': '条件1不满足'}
        elif not term2_satisfied:
            return {'success': False, 'msg': '条件2不满足'}
    elif coupon.term1 and not term1_satisfied:
        return {'success': False, 'msg': '条件不满足'}
    elif coupon.term2 and not term2_satisfied:
        return {'success': False, 'msg': '条件不满足'}
    return {'success': True}


def order_page(openid, coupon_id):
    ret_user = {
        'credits': query_credits(openid, 'user'),
    }
    coupon = Coupon.objects.get(id=coupon_id)
    ret_coupon = {
        'credits': coupon.credits,
        'name': coupon.name,
        'discount_type': coupon.discount_type,
    }
    return {'user': ret_user, 'coupon': ret_coupon}


def purchase(openid, num, coupon_id, req_token, inviter_openid='', invitation_couponid=''):
    user = User.objects.get(openid=openid)
    coupon = Coupon.objects.get(id=coupon_id)
    num = int(num)
    cur_num = UserCoupon.objects.filter(user=user, coupon=coupon).count()
    if coupon.limit > 0 and cur_num + num > coupon.limit:
        return {'success': False, 'msg': '超出优惠券购买数量限制'}
    if coupon.busi_type:
        typed_coupons = Coupon.objects.filter(busi_type=coupon.busi_type)
        typed_cur_num = UserCoupon.objects.filter(user=user, coupon__in=typed_coupons).count()
        typed_limit = int(CommonParam.objects.get(name=coupon.busi_type).value)
        logger.debug('typed_cur_num: %s, typed_limit: %s', typed_cur_num, typed_limit)
        if typed_cur_num + num > typed_limit:
            return {'success': False, 'msg': '超出同类优惠券购买数量限制'}
    amount = coupon.credits * num
    if user.is_new:
        return {'success': False, 'msg': '您尚未绑定，无法交易, 请到个人信息页面绑定'}
    if coupon.leftnum < num:
        return {'success': False, 'msg': '剩余的优惠券只有' + str(coupon.leftnum) + '张，数量不足'}
    if query_credits(openid, 'user') < amount:
        return {'success': False, 'msg': '您的积分不足'}
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    invited_flag = CouponInvitation.objects.filter(inviter__openid=inviter_openid)\
        .filter(invitee=user).filter(coupon__id=coupon_id).exists()
    #判断是否来自邀请
    if inviter_openid and invitation_couponid == coupon_id and not invited_flag:
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            orderno_list = generate_orderno(2)
            coupon.soldnum += num
            coupon.leftnum -= num
            coupon.save()
            user.credits -= amount
            user.save()
            log = transaction_detail_save(user, None, -amount, '优惠券购买', str(num) + '张' + coupon.name, orderno_list[0])
            for i in range(0, num):
                UserCoupon.objects.create(user=user, coupon=coupon, status='未使用', in_log=log)
            gift_credits = int(CommonParam.objects.get(name='优惠券分享赠送积分').value)
            inviter = User.objects.get(openid=inviter_openid)
            inviter.credits += gift_credits
            inviter.save()
            transaction_detail_save(inviter, None, gift_credits, '推荐购券', '推荐' + user.name + '购买优惠券', orderno_list[1])
            CouponInvitation.objects.create(inviter=inviter, invitee=user, type='优惠券分享', is_completed=True, coupon=coupon)
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, -amount)
            add_trade_detail(trade_type='优惠券购买', idcardno=user.idcardno, name=user.name,\
                credits=amount, direction='-', new_credits=query_credits(openid, 'user'),\
                orderno=orderno_list[0], goods_name=coupon.name, goods_cost=coupon.credits, trade_num=num)
            update_or_insert_credits(inviter.idcardno, gift_credits)
            add_trade_detail(trade_type='推荐购券', idcardno=inviter.idcardno, name=inviter.name,\
                credits=gift_credits, direction='+', new_credits=query_credits(inviter_openid, 'user'),\
                orderno=orderno_list[1], goods_name=coupon.name, goods_cost=coupon.credits, trade_num=num)
        return {'success': True, 'invitation_completed': True}
    else:
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            orderno = generate_orderno(1)[0]
            coupon.soldnum += num
            coupon.leftnum -= num
            coupon.save()
            user.credits -= amount
            user.save()
            log = transaction_detail_save(user, None, -amount, '优惠券购买', str(num) + '张' + coupon.name, orderno)
            for i in range(0, num):
                UserCoupon.objects.create(user=user, coupon=coupon, status='未使用', in_log=log)
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, -amount)
            add_trade_detail(trade_type='优惠券购买', idcardno=user.idcardno, name=user.name,\
                credits=amount, direction='-', new_credits=query_credits(openid, 'user'),\
                orderno=orderno, goods_name=coupon.name, goods_cost=coupon.credits, trade_num=num)
        return {'success': True}
