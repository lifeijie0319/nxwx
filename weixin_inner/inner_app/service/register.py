# -*- coding:utf-8 -*-
"""注册模块

该模块用于实现用户、商户的注册
"""
#register.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import datetime
import json

from django.db import transaction

from .address import get_region_tree
from .common import add_trade_detail, credits_usable, cus_verify,\
query_credits, transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..credits_api import query_account
from ..models import Address, CommonParam, Invitation, Manager, Seller, SellerRegister, Shop, ShopType, User 
from ..tools import generate_orderno


def user_register(openid, user_name, user_id, user_tel, inviter_openid='', new_cus='no', update_flag='no'):
    #managers = Manager.objects.filter(status='normal')
    #manager_flag = user_id in [manager.idcardno for manager in managers]
    #print [manager.idcardno for manager in managers]
    #print user_id, manager_flag
    #if not manager_flag:
    #    return {'success': False, u'msg': u'公众号升级内测中，尚未对外开放'}
    if not openid:
        return {'success': False, u'msg': u'错误的微信唯一标识，请联系管理员'}
    if User.objects.filter(openid=openid).exists():
        return {'success': False, u'msg': u'请不要重复注册'}
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    with transaction.atomic():
        if new_cus == 'no':
            cus_verify_res = cus_verify(user_id, user_tel)
            if not cus_verify_res.get('existance'):
                return {'success': False, u'msg': u'用户不存在'}
            elif not cus_verify_res.get('telno_matched'):
                return {'success': False, u'msg': u'您填写的手机号与银行预留手机号不同，\
                    请到银行柜面修改！请注意，手机号码更新后第二天才能正常注册！'}
            elif User.objects.filter(idcardno=user_id).exists():
                logger.debug(update_flag)
                if update_flag == 'no':
                    return {'success': False, u'msg': u'身份证号已存在'}
                User.objects.filter(idcardno=user_id).update(openid=openid, telno=user_tel, is_new=False)
                user = User.objects.get(openid=openid)
            else:
                user_name = cus_verify_res.get('name')
                user = User.objects.create(openid=openid, name=user_name, idcardno=user_id, telno=user_tel, is_new=False)
        else:
            if User.objects.filter(idcardno=user_id).exists():
                logger.debug(update_flag)
                if update_flag == 'no':
                    return {'success': False, u'msg': u'身份证号已存在'}
                User.objects.filter(idcardno=user_id).update(openid=openid, telno=user_tel, is_new=True)
                user = User.objects.get(openid=openid)
            user = User.objects.create(openid=openid, name=user_name, idcardno=user_id, telno=user_tel, is_new=True)
        if inviter_openid:
            gift_credits = int(CommonParam.objects.get(name=u'邀请注册赠送积分').value)
            inviter = User.objects.get(openid=inviter_openid)
            inviter.credits += gift_credits
            inviter.save()
            user.credits += gift_credits
            user.save()
            Invitation.objects.create(inviter=inviter, invitee=user, type=u'注册邀请', is_completed=True)
            orderno_list = generate_orderno(2)
            transaction_detail_save(inviter, None, gift_credits, u'推荐注册',\
                u'推荐' + user.name, orderno_list[0])
            transaction_detail_save(user, None, gift_credits, u'推荐注册',\
                u'被' + inviter.name + '推荐', orderno_list[1])
    with transaction.atomic(using='old_credits'):
        if inviter_openid and not inviter.is_new:
            update_or_insert_credits(inviter.idcardno, gift_credits)
            add_trade_detail(trade_type=u'推荐注册', idcardno=inviter.idcardno, name=inviter.name,\
                credits=gift_credits, direction='+', new_credits=query_credits(inviter_openid, 'user'),\
                orderno=orderno_list[0])
        if inviter_openid and not user.is_new:
            update_or_insert_credits(user.idcardno, gift_credits)
            add_trade_detail(trade_type=u'推荐注册', idcardno=user.idcardno, name=user.name,\
                credits=gift_credits, direction='+', new_credits=query_credits(inviter_openid, 'user'),\
                orderno=orderno_list[1])
    return {'success': True, 'is_new': new_cus}


def seller_register(openid, name, bankcard_no, telephone_no, teller_no=''):
    if Seller.objects.filter(openid=openid).exists():
        return {'success': False, 'msg': u'请不要重复注册'}
    #校验
    account_info = query_account(bankcard_no)
    if not account_info:
        return {'success': False, 'msg': u'卡号不存在'}
    return {'success': True}


def seller_register2_page():
    """视图函数，初始化商户注册店铺信息页面"""
    tree = get_region_tree(start_node_code=u'330000000000', end_level=u'county')
    region_tree = json.dumps(tree, ensure_ascii=False, encoding='utf-8')
    shop_types = [shop.name for shop in ShopType.objects.all()]
    logger.debug('SHOP_TYPES: %s', shop_types)
    return {u'region_tree': region_tree, u'shop_types': shop_types}


@transaction.atomic
def seller_register2(openid, name, tel_no, account_no, shop_name, shop_type, province, city, county, town, village, address_detail, teller_no=''):
    if SellerRegister.objects.filter(openid=openid).exclude(status__in=['通过', '驳回']).exists():
        return ({'success': False, 'msg': u'请不要重复提交'})
    if Shop.objects.filter(name=shop_name).exists():
        return {'success': False, 'msg': '该商店名称已存在，请换一个名字'}
    address = Address.objects.create(province=province, city=city, county=county, town=town, village=village, detail=address_detail)
    shop_type_obj = ShopType.objects.get(name=shop_type)
    now = datetime.datetime.now()
    registration = SellerRegister.objects.create(openid=openid, name=name, telno=tel_no, accountno=account_no,\
        tellerno=teller_no, shop_name=shop_name, shop_type=shop_type_obj, shop_address=address, apply_datetime=now, status=u'待审核')

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
        'name': name,
        'info': u'在' + address.get_str() + u'开一家' + shop_name,
        'apply_datetime': registration.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return {'success': True, 'head_admins_openid': head_admins_openid, 'data': data}
