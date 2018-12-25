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
from ..models import TransactionDetail
from ..tools import gen_excel, get_menu


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/report_cus_trade_detail.html', context)


@login_check
def query(request):
    trade_details = TransactionDetail.objects.all()
    logger.debug(request.GET)
    try:
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        end_date = request.GET.get('end_date')
        start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        trade_details = TransactionDetail.objects.filter(trade_datetime__range
            =(start_datetime, end_datetime)).order_by('-trade_datetime')
        telno = request.GET.get('cus_telno')
        if telno:
            trade_details = trade_details.filter(trader__telno=telno)
        trade_details = [trade_detail for trade_detail in trade_details if hasattr(trade_detail.trader, 'user')]
        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['起始时间', '结束时间', '客户名称', '客户联系方式', '积分消费对手名称',
                '对手联系方式', '交易类型', '交易金额', '交易时间']
            datas = []
            for trade_detail in trade_details:
                data = [start_date, end_date, trade_detail.trader.name, trade_detail.trader.telno,
                    trade_detail.opposite.name if trade_detail.opposite else '系统',
                    trade_detail.opposite.telno if trade_detail.opposite else '无',
                    trade_detail.type, trade_detail.credits, trade_detail.trade_datetime.strftime('%Y-%m-%d %H:%M:%S')]
                datas.append(data)
            return gen_excel(headers, datas, '客户积分消费明细')

        if not trade_details:
            context = {'trade_details': trade_details}
        else:
            paginator = Paginator(trade_details, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_trade_details = paginator.page(page)
            context = {'trade_details': p_trade_details}
        html = render_to_string(APP_NAME + '/report_cus_trade_detail_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)
