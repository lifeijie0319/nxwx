# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Manager, Seller, Shop, TransactionDetail
from ..tools import gen_excel, get_authorized_banks, get_menu


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
    return render(request, APP_NAME + '/report_shop_trade_total.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        end_date = request.GET.get('end_date')
        start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        trade_details = TransactionDetail.objects.filter(trade_datetime__range
            =(start_datetime, end_datetime)).order_by('-trade_datetime')

        #logger.debug('TRADE_DETAILS:%s', trade_details)
        bank_id = request.GET.get('bank')
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)

        trade_totals = []
        for bank in banks:
            item = {
                'bankno': bank.deptno,
                'bank': bank.name,
                'shop_num': bank.shop_set.count()
            }
            shops = Shop.objects.filter(bank=bank)
            #logger.debug('SHOP: %s', shops)
            sellers = [shop.seller for shop in shops]
            #logger.debug('SELLER: %s', sellers)
            #logger.debug(trade_details)
            bank_trade_details = trade_details.filter(trader__seller__in=sellers)
            #logger.debug(bank_trade_details)
            item['trade_num'] = bank_trade_details.count()
            #logger.debug(bank_trade_details.aggregate(Sum('credits')))
            item['credits'] = bank_trade_details.aggregate(Sum('credits')).get('credits__sum') if bank_trade_details else 0
            trade_totals.append(item)

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['起始时间', '结束时间', '维护机构号', '维护机构名称', '商户数量', '积分交易笔数', '积分交易金额']
            datas = []
            for trade_total in trade_totals:
                data = [start_date, end_date, trade_total.get('bankno'), trade_total.get('bank'),
                    trade_total.get('shop_num'), trade_total.get('trade_num'), trade_total.get('credits')]
                datas.append(data)
            return gen_excel(headers, datas, '积分消费汇总')

        if not trade_totals:
            context = {'trade_totals': trade_totals}
        else:
            paginator = Paginator(trade_totals, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_trade_totals = paginator.page(page)
            context = {'trade_totals': p_trade_totals}

        html = render_to_string(APP_NAME + '/report_shop_trade_total_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)
