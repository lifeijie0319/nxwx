# -*- coding: utf-8 -*-
"""积分模块

该模块用于处理积分系统相关功能
"""
#credits.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json
import os
import time

from django.db import transaction

from .common import add_trade_detail, credits_usable, query_credits,\
transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import CommonParam, RepetitionExclude, Seller, Shop, TransactionDetail, User
from ..tools import generate_orderno


def page(openid):
    credits = query_credits(openid, 'user')
    gift_credits = int(CommonParam.objects.get(name='邀请注册赠送积分').value)
    return {'credits': credits, 'gift_credits': gift_credits}


def trade_reply(openid, log_id, is_scan=''):
    log = TransactionDetail.objects.get(id=log_id)
    text = {}
    if log.trader.openid == openid:
        text['credits'] = log.credits
        if log.credits > 0:
            text['title'] = u'收款成功'
        else:
            text['title'] = u'付款成功'
        if hasattr(log.opposite, 'seller'):
            text[u'opposite'] = log.opposite.seller.shop_set.first().name
        else:
            text[u'opposite'] = log.opposite.name
        if hasattr(log.trader, 'user'):
            text['href'] = '/outer_app/credits/page/'
        else:
            text['href'] = '/outer_app/seller/page/'
    else:
        text['credits'] = -log.credits
        if log.credits > 0:
            text['title'] = u'付款成功'
        else:
            text['title'] = u'收款成功'
        if hasattr(log.trader, 'seller'):
            text[u'opposite'] = log.trader.seller.shop_set.first().name
        else:
            text[u'opposite'] = log.trader.name
        if hasattr(log.opposite, 'user'):
            text['href'] = '/outer_app/credits/page/'
        else:
            text['href'] = '/outer_app/seller/page/'
    text['date_time'] = log.trade_datetime.strftime('%Y-%m-%d %H:%M:%S')
    text['order_no'] = log.orderno
    return text


def trade(openid, qrcode_openid, amount, qrcode_id, req_token):
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    amount = int(amount)
    orederno_list = generate_orderno(2)
    if qrcode_id == '00000000':
        if query_credits(qrcode_openid, 'user') < amount:
            return ({'success': False, 'msg': u'对方的积分不足'})
        user = User.objects.get(openid=qrcode_openid)
        seller = Seller.objects.get(openid=openid)
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            user.credits -= amount
            user.save()
            seller.credits += amount
            seller.save()        
            shop = seller.shop_set.first()
            shop.trade_times += 1
            shop.save()
            log1 = transaction_detail_save(seller, user, amount, u'商户扫码直接收取',\
                u'向' + user.name + u'收取积分', orederno_list[1])
            log2 = transaction_detail_save(user, seller, -amount, u'扫码直接支付',\
                u'支付积分给' + shop.name, orederno_list[0])
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, -amount)
            add_trade_detail(u'扫码直接支付', user.idcardno, user.name, amount, '-',\
                query_credits(qrcode_openid, 'user'), orederno_list[0])
    elif qrcode_id == '00000001':
        user = User.objects.get(openid=openid)
        seller = Seller.objects.get(openid=qrcode_openid)
        if query_credits(openid, 'user') < amount:
            return {'success': False, 'msg': u'您的积分不足'}
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            user.credits -= amount
            user.save()
            seller.credits += amount
            seller.save()
            shop = seller.shop_set.first()
            shop.trade_times += 1
            shop.save()
            log1 = transaction_detail_save(user, seller, -amount, u'扫码直接支付',\
                u'支付积分给' + shop.name, orederno_list[0])
            log2 = transaction_detail_save(seller, user, amount, u'商户扫码直接收取',\
                u'向' + user.name + u'收取积分', orederno_list[1])
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, -amount)
            add_trade_detail(u'扫码直接支付', user.idcardno, user.name, amount, '-',\
                query_credits(openid, 'user'), orederno_list[0])
    elif qrcode_id == '00000002':
        scan_user = User.objects.get(openid=openid)
        qrcode_user = User.objects.get(openid=qrcode_openid)
        logger.debug('%s, %r', type(query_credits(openid, 'user')), query_credits(openid, 'user'))
        logger.debug('%s, %r', type(amount), amount)
        if query_credits(openid, 'user') < amount:
            return ({'success': False, 'msg': u'您的积分不足'})
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            scan_user.credits -= amount
            scan_user.save()
            qrcode_user.credits += amount
            qrcode_user.save()
            log1 = transaction_detail_save(scan_user, qrcode_user, -amount, u'扫码赠送',\
                u'赠送积分给' + qrcode_user.name, orederno_list[0])
            log2 = transaction_detail_save(qrcode_user, scan_user, amount, u'扫码获赠',\
                u'获得' + scan_user.name + u'赠送的积分', orederno_list[1])
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(scan_user.idcardno, -amount)
            update_or_insert_credits(qrcode_user.idcardno, amount)
            add_trade_detail(u'扫码赠送', scan_user.idcardno, scan_user.name, amount, '-',\
                query_credits(openid, 'user'), orederno_list[0])
            add_trade_detail(u'扫码获赠', qrcode_user.idcardno, qrcode_user.name, amount, '+',\
                query_credits(qrcode_openid, 'user'), orederno_list[1])
    return {'success': True, 'log_id': log1.id}


def history_page(openid, query_type, last_id=''):
    def get_opposite_id(log):
        if hasattr(log.opposite, 'user'):
            opposite_id = log.opposite.user.id
        elif hasattr(log.opposite, 'seller'):
            opposite_id = log.opposite.seller.shop_set.first().id
        else:
            opposite_id = 'system'
        return opposite_id
    if last_id:
        last = TransactionDetail.objects.get(id=last_id).trade_datetime
        history = TransactionDetail.objects.filter(trader__openid=openid).filter(trade_datetime__lt=last).order_by('-trade_datetime')
    else:
        history = TransactionDetail.objects.filter(trader__openid=openid).order_by('-trade_datetime')
    history = [log for log in history if hasattr(log.trader, query_type)][:10]
    ret_history = [{
        'id': log.id,
        'type': log.type,
        'info': log.info,
        'credits': log.credits,
        'opposite_type': 'user' if hasattr(log.opposite, 'user') else 'seller',
        'opposite_id': get_opposite_id(log),
        'trade_datetime': log.trade_datetime.strftime('%Y年%m月%d日 %H时%M分'),
    } for log in history]
    ret_id = -1 if len(history) < 10 else history[-1].id
    return {'ret_history': ret_history, 'last_id': ret_id}


def history_details_page(id):
    detail = TransactionDetail.objects.get(id=id)
    ret_detail = {
        'credits': detail.credits,
        'opposite_name': detail.opposite.name if detail.opposite else '系统',
        'type': detail.type,
        'info': detail.info,
        'trade_datetime': detail.trade_datetime.strftime('%Y.%m.%d %H:%M:%S'),
        'orderno': detail.get_orderno(),
    }
    return {'detail': ret_detail}
