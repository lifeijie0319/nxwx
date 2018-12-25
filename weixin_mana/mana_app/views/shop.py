# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import get_ordered_shops, login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Coupon, Manager, Shop, ShopType
from ..tools import gen_excel, get_authorized_banks, get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    manager = Manager.objects.get(account=manager_account)
    banks = get_authorized_banks(manager.bankbranch)
    #shops = get_ordered_shops(Shop.objects.filter(bank__in=banks))
    coupons = Coupon.objects.all()
    types = ShopType.objects.all()
    context = {
        'banks': banks,
        'types': types,
        'statuses': Shop.STATUS,
        'coupons': coupons,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/shop.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        bank_id = request.GET.get('bank')
        logger.debug('BANK_ID: %s', bank_id)
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)
        shops = Shop.objects.filter(bank__in=banks)

        name = request.GET.get('name')
        if name:
            shops = shops.filter(name__contains=name)

        reg_date = request.GET.get('reg_date')
        if reg_date:
            reg_datetime = datetime.datetime.strptime(reg_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            shops = shops.filter(created_datetime__lte=reg_datetime)

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['数据日期', '商户注册日期', '商户名称', '商户类型', '地址', '交易次数',
                '维护机构号', '经营者名称', '联系方式', '关联账户']
            datas = []
            for shop in get_ordered_shops(shops):
                data = [reg_date, shop.created_datetime.strftime('%Y-%m-%d'), shop.name, shop.type.name,
                    shop.address.get_str(), shop.trade_times, shop.bank.deptno, shop.seller.name,
                    shop.seller.telno, shop.seller.account]
                datas.append(data)
            return gen_excel(headers, datas, '商户基本信息')
        
        if not shops:
            context = {'shops': shops}
        else:
            shops = get_ordered_shops(shops)
            paginator = Paginator(shops, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_shops = paginator.page(page)
            context = {'shops': p_shops}
        html = render_to_string(APP_NAME + '/shop_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


#@login_check
#def stick(request):
#    logger.debug(request.body)
#    post_data = json.loads(request.body)
#    shop_id = post_data.get('shop_id')
#    stick = post_data.get('stick')
#    try:
#        with transaction.atomic():
#            shop = Shop.objects.get(id=shop_id)
#            shop.stick = stick
#            shop.save()
#            manager = Manager.objects.get(account=request.session.get('manager_account'))
#            log_action(manager, 'update', shop, ['stick'])
#            res = {'success': True, 'msg': u'置顶状态变换成功'}
#    except Exception, e:
#        logger.debug(e)
#        res = {'success': False, 'msg': u'置顶状态变换失败'}
#    return JsonResponse(res)


@login_check
def update(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    shop_id = post_data.get('shop_id')
    logger.debug('POST: %s', post_data)
    try:
        with transaction.atomic():
            shop = Shop.objects.get(id=shop_id)
            shop.name = post_data.get('name')
            shop.type = ShopType.objects.filter(id=int(post_data.get('type'))).first()
            shop.bank = BankBranch.objects.filter(id=int(post_data.get('bank'))).first()
            shop.stick = post_data.get('stick')
            shop.status = post_data.get('status')
            shop.save()

            if not post_data.get('coupons'): 
                coupons = []
            elif isinstance(post_data.get('coupons'), list):
                coupons = post_data.get('coupons')
            else:
                coupons = [post_data.get('coupons')]
            logger.debug('COUPONS: %s', coupons)
            shop.coupon_set = coupons

            seller = shop.seller
            seller.name = post_data.get('seller')
            seller.telno = post_data.get('telno')
            seller.account = post_data.get('account')
            seller.save()

            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'update', shop, ['*'])
            log_action(manager, 'update', seller, ['name', 'telno', 'account'])
            res = {'success': True, 'msg': u'可消费优惠券设置成功'}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'可消费优惠券设置失败'}
    return JsonResponse(res)
