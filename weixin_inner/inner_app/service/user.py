# -*- coding: utf-8 -*-
"""用户模块

该模块用于处理用户相关的功能
"""
#user.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json
import os

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .common import add_trade_detail, credits_usable, cus_verify, query_credits,\
transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import Manager, Seller, User, UserCoupon
from ..tools import generate_orderno, to_json


def get_user(openid):
    user = User.objects.get(openid=openid)
    ret_user = {
        'id': user.id,
        'openid': openid,
        'name': user.name,
        'telno': user.telno,
        'credits': query_credits(openid, 'user'),
        'idcardno': user.idcardno,
        'address': user.address.get_str() if user.address else None,
        'is_new': 'yes' if user.is_new else 'no',
    }
    return ret_user


def info_page(openid):
    user = User.objects.get(openid=openid)
    is_manager = Manager.objects.filter(idcardno=user.idcardno, status='normal').exists()
    ret_user = {
        'id': user.id,
        'name': user.name,
        'credits': query_credits(openid, 'user'),
        'is_new': user.is_new,
        'is_manager': is_manager,
    }
    logger.debug(user.is_new)
    my_coupons_num = UserCoupon.objects.filter(user=user).filter(status=u'未使用').count()
    return {'user': ret_user, 'my_coupons_num': my_coupons_num}
 

def photo(openid):
    user = User.objects.get(openid=openid)
    ret_user = {'id': user.id}
    return ret_user


def payment_password_modify_page(openid):
    user = User.objects.get(openid=openid)
    password_existed = True if user.paypasswd else False
    return {'password_existed': password_existed}


@transaction.atomic
def payment_password_modify(openid, new_password, old_password=''):
    user = User.objects.get(openid=openid)
    if old_password and not user.check_password(old_password):
        return {'success': False, u'msg': u'原密码输入错误'}
    user.set_password(new_password)
    logger.debug(user.paypasswd)
    user.save()
    return {'success': True}


def payment_password_fetch(openid, amount=''):
    if amount and query_credits(openid, 'user') < int(amount):
        return ({'success': False, 'msg': u'您的积分不足'})
    source = User.objects.get(openid=openid)
    msg = 'need_password' if source.paypasswd else 'complete'
    return {'success': True, 'msg': msg}


def payment_password_verify(openid, verifying_password):
    user = User.objects.get(openid=openid)
    logger.debug(verifying_password)
    if user.check_password(verifying_password):
        return {'success': True}
    return {'success': False}


def parse_qrcode_str(openid, qrcode_openid, qrcode_id, amount=''):
    if qrcode_id == '00000001':
        source = User.objects.get(openid=openid)
        if source.is_new:
            return {'success': False, 'msg': u'您尚未绑定，无法交易, 请到个人信息页面绑定'}
        target = Seller.objects.get(openid=qrcode_openid)
        tips = u'向商户 ' + target.shop_set.first().name + u' 付积分'
        opposite_type = 'shop'
        opposite_id = target.shop_set.first().id
    elif qrcode_id == '00000002':
        source = User.objects.get(openid=openid)
        if source.is_new:
            return {'success': False, 'msg': u'您尚未绑定，无法交易, 请到个人信息页面绑定'}
        target = User.objects.get(openid=qrcode_openid)
        if target.is_new:
            return {'success': False, 'msg': u'对方用户未绑定，无法交易'}
        tips = u'向用户 ' + target.name + u' 付积分'
        opposite_type = 'user'
        opposite_id = target.id
    else:
        return ({'success': False, 'msg': u'不匹配的二维码'})

    if amount:
        if query_credits(source.openid, 'user') < int(amount):
            return ({'success': False, 'msg': u'您的积分不足'})
        msg = 'confirm'
        logger.debug('AMOUNT: %s', amount)
    else:
        msg = 'set_amount'
    context = {
        'success': True,
        'msg': msg,
        'tips': tips,
        'opposite_type': opposite_type,
        'opposite_id': opposite_id,
        'amount': amount,
    }
    return context


def binding(openid, user_name, user_id, user_tel):
    user = User.objects.get(openid=openid)
    if not user.is_new:
        return {'success': False, u'msg': u'用户已经绑定，请勿重复'}
    #TODO 身份证、手机号、姓名三要素检查
    cus_verify_res = cus_verify(user_id, user_tel)
    if not cus_verify_res.get('existance'):
        return {'success': False, u'msg': u'用户不存在'}
    elif not cus_verify_res.get('telno_matched'):
        return {'success': False, u'msg': u'您的手机号与银行预留手机号不同，\
            请到银行柜面修改！请注意，手机号码更新后第二天才能正常绑定！'}
    elif not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    else:
        with transaction.atomic():
            user_name = cus_verify_res.get('name')
            orderno = generate_orderno(1)[0]
            user.name = user_name
            user.idcardno = user_id
            user.telno = user_tel
            user.is_new = False
            user.save()
            transaction_detail_save(user, None, user.credits, u'绑定初始化',\
                '绑定后原有积分开始计入综合积分系统，作为该用户的初始化积分', orderno)
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user_id, user.credits)
            add_trade_detail(u'绑定初始化', user_id, user_name, user.credits, '+', query_credits(openid, 'user'), orderno)
        return {'success': True}
