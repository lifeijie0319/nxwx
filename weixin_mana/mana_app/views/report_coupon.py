# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Coupon, Manager, Shop
from ..tools import gen_excel, get_authorized_banks, get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    manager = Manager.objects.get(account=manager_account)
    banks = get_authorized_banks(manager.bankbranch)
    context = {
        'banks': banks,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/report_coupon.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        bank_id = request.GET.get('bank')
        logger.debug('BANK_ID: %s', bank_id)
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)
        report_coupons = Coupon.objects.all()

        on_date = request.GET.get('on_date')
        if on_date:
            report_coupons = report_coupons.filter(on_date__gte=on_date)
        off_date = request.GET.get('off_date')
        if off_date:
            report_coupons = report_coupons.filter(off_date__lte=off_date)

        shops = Shop.objects.filter(bank__in=banks)
        name = request.GET.get('name')
        if name:
            shops = shops.filter(name__contains=name)

        items = []
        for report_coupon in report_coupons:
            for shop in report_coupon.shops.all():
                if shop in shops:
                    item = {
                        'bankno': shop.bank.deptno,
                        'bank': shop.bank.name,
                        'shop': shop.name,
                        'telno': shop.seller.telno,
                        'name': report_coupon.name,
                        'type': report_coupon.discount_type,
                        'on_date': report_coupon.on_date.isoformat(),
                        'off_date': report_coupon.off_date.isoformat(),
                        'soldnum': report_coupon.soldnum,
                        'leftnum': report_coupon.leftnum,
                    }
                    items.append(item)
        items = sorted(items, key=lambda x:x.get('bankno'))

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['维护机构号', '维护机构', '商户名称', '联系方式', '优惠券名称', '优惠券类型',
                '上架日期', '下架日期', '售出数量', '剩余数量']
            datas = [[item['bankno'], item['bank'], item['shop'], item['telno'], item['name'],
                item['type'], item['on_date'], item['off_date'], item['soldnum'], item['leftnum']]
                for item in items]
            return gen_excel(headers, datas, '优惠券报表')

        if not items:
            context = {'report_coupons': items}
        else:
            paginator = Paginator(items, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_items = paginator.page(page)
            context = {'report_coupons': p_items}

        html = render_to_string(APP_NAME + '/report_coupon_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)

