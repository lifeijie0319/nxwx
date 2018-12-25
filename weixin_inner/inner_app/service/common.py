# -*- coding: utf-8 -*-
"""通用视图函数

该模块用于定义一些公用的，不能轻易归类的视图函数
"""
#common.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json

from collections import OrderedDict
from ..credits_api import insert_cus_credits, insert_trade_detail, query_cus_credits,\
query_cus_info, query_coupon_term, query_sync_status, update_cus_credits
from ..logger import logger
from ..models import CommonParam, Seller, SellerRegister, SellerReplace, TransactionDetail, User, SmsRecord
from ..tools import parse_time_from_orderno


def query_credits(openid, type):
    if type == 'user':
        user = User.objects.get(openid=openid)
        logger.debug('IS_NEW: %s', user.is_new)
        if user.is_new:
            credits = user.credits
        else:
            cus_info = query_cus_credits('101' + user.idcardno)
            credits = round(cus_info[0].get('JFYE') * 0.01) if cus_info else 0
    else:
        seller = Seller.objects.get(openid=openid)
        credits = seller.credits
    return credits


def update_or_insert_credits(idcardno, credits):
    cusno = '101' + idcardno
    if query_cus_credits(cusno):
        ret = update_cus_credits(cusno, 100 * credits)
    else:
        ret = insert_cus_credits(cusno, 100 * credits)
    return ret


def add_trade_detail(trade_type, idcardno, name, credits, direction, new_credits, orderno, goods_name='', goods_cost=None, trade_num=None):
    trade_time = parse_time_from_orderno(orderno)
    info = OrderedDict({
        'DATE_ID': datetime.datetime.now().strftime('%Y%m%d'),
        'TRADE_TYPE': trade_type,
        'CUST_NO': '101' + idcardno,
        'CUST_NAME': name,
        'TRADE_TIME': trade_time.strftime('%Y-%m-%d %H:%M:%S'),
        'TRADE_SCORE': 100 * credits,
        'TRADE_DIREC': direction,
        'NEW_CREDITS': 100 * new_credits,
        'GOODS_NAME': goods_name,
        'GOODS_COST': goods_cost,
        'TRADE_NUM': trade_num,
        'TRADE_COMM1': orderno,
    })
    flag = insert_trade_detail(**info)
    return flag


def transaction_detail_save(trader, opposite, credits, trade_type, info, orderno, coupon=None):
    """存储一条交易明细记录"""
    trade_datetime = parse_time_from_orderno(orderno)
    data = {
        'trader': trader,
        'opposite': opposite,
        'credits': credits,
        'type': trade_type,
        'info': info,
        'coupon': coupon,
        'trade_datetime': trade_datetime,
        'orderno': orderno,
        'need_reconciliation': True if hasattr(trader, 'user') and not trader.is_new else False,
    }
    return TransactionDetail.objects.create(**data)


def user_register_check(openid):
    registered = User.objects.filter(openid=openid).exists()
    return {'registered': registered}


def seller_register_check(openid):
    registered = Seller.objects.filter(openid=openid).exists()
    if registered:
        return {'status': 'registered'}
    seller_auditing = SellerRegister.objects.filter(openid=openid)\
        .filter(status__in=(u'待审核', u'分配给支行', u'分配给客户经理')).exists()
    if seller_auditing:
        return {'status': 'seller_auditing'}
    seller_replace_auditing = SellerReplace.objects.filter(openid=openid)\
        .exclude(status__in=(u'通过', u'驳回')).exists()
    if seller_replace_auditing:
        return {'status': 'seller_replace_auditing'}
    return {'status': 'stranger'}


def coupon_term_check(idcardno, term_code):
    cus_term_res = query_coupon_term('101' + idcardno)
    if cus_term_res and cus_term_res[0].get(term_code):
        return True
    return False


def cus_verify(idcardno, telno):
    cus_info = query_cus_info('101' + idcardno)
    if not cus_info:
        return {'existance': False}
    telno_list = [row.get('MOBILE_NO', '').strip() for row in cus_info]
    if telno in telno_list:
        return {'existance': True, 'telno_matched': True, 'name': cus_info[0].get('CST_NAME')}
    else:
        return {'existance': True, 'telno_matched': False, 'name': cus_info[0].get('CST_NAME')}


def credits_usable():
    return query_sync_status('I_SC_KHJFYEB')


def get_manager_user(managers):
    users = []
    for manager in managers:
        m_user = User.objects.filter(idcardno=manager.idcardno).first()
        if m_user:
            users.append(m_user)
    return users


def send_vcode(openid, data=None):
    if data:
        data['openid'] = openid
        SmsRecord.objects.create(**data)
        return {'success': True}
    else:
        today = datetime.date.today()
        num = SmsRecord.objects.filter(openid=openid, add_dtime__year=today.year,
                                       add_dtime__month=today.month, add_dtime__day=today.day).count()
        limit = CommonParam.objects.get(name='单日短信条数限制').value
        logger.debug('{},{}'.format(num, limit))
        if num >= int(limit):
            return {'success': False}
        else:
            return {'success': True}
