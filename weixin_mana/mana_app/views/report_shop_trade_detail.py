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
    return render(request, APP_NAME + '/report_shop_trade_detail.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        manager_account = request.session.get('manager_account')
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        end_date = request.GET.get('end_date')
        logger.debug('END_DATE: %s', type(end_date))
        start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        logger.debug(start_datetime)
        end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        logger.debug(end_datetime)
        trade_details = TransactionDetail.objects.filter(trade_datetime__gte=start_datetime)\
            .filter(trade_datetime__lte=end_datetime).order_by('-trade_datetime')

        bank_id = request.GET.get('bank')
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)
        shops = Shop.objects.filter(bank__in=banks)
        sellers = [shop.seller for shop in shops]
        #logger.debug(sellers)
        trade_details = trade_details.filter(trader__seller__in=sellers)
        #logger.debug(trade_details)

        telno = request.GET.get('telno')
        if telno:
            trade_details = trade_details.filter(trader__telno=telno)

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['起始时间', '结束时间', '维护机构号', '商户名称', '商户联系方式', '积分交易客户名称',
                '交易类型', '交易金额', '交易时间']
            datas = []
            for trade_detail in trade_details:
                data = [start_date, end_date, trade_detail.trader.seller.shop_set.first().bank.deptno,
                    trade_detail.trader.seller.shop_set.first().name, trade_detail.trader.seller.telno,
                    trade_detail.opposite.name if trade_detail.opposite else '系统', trade_detail.type,
                    trade_detail.credits, trade_detail.trade_datetime.strftime('%Y-%m-%d %H:%M:%S')]
                datas.append(data)
            return gen_excel(headers, datas, '商户积分交易明细')

        if not trade_details:
            context = {'trade_details': trade_details}
        else:
            paginator = Paginator(trade_details, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_trade_details = paginator.page(page)
            context = {'trade_details': p_trade_details}

        html = render_to_string(APP_NAME + '/report_shop_trade_detail_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)
