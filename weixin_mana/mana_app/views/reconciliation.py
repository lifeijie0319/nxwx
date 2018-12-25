# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from collections import OrderedDict
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check, query_credits, update_or_insert_credits
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..credits_api import insert_trade_detail, query_sync_status
from ..logger import logger
from ..models import Manager, ReconciliationAmendment, ReconciliationLog, TransactionDetail, User
from ..tools import get_menu


@login_check
def log_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'reconciliation_logs': ReconciliationLog.objects.all().order_by('-opt_datetime'),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/reconciliation_log.html', context)


@login_check
def log_query(request):
    try:
        reconciliation_logs = ReconciliationLog.objects.all()
        start_date = request.GET.get('start_date')
        if start_date:
            start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            reconciliation_logs = reconciliation_logs.filter(start_datetime__gte=start_datetime)
        end_date = request.GET.get('end_date')
        if end_date:    
            end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            logger.debug(end_datetime)
            reconciliation_logs = reconciliation_logs.filter(end_datetime__lte=end_datetime)
        if not reconciliation_logs:
            context = {'reconciliation_logs': reconciliation_logs}
        else:
            reconciliation_logs = reconciliation_logs.order_by('-opt_datetime')
            paginator = Paginator(reconciliation_logs, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_reconciliation_logs = paginator.page(page)
            context = {'reconciliation_logs': p_reconciliation_logs}
        html = render_to_string(APP_NAME + '/reconciliation_log_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def amend_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        #'reconciliation_amendments': ReconciliationAmendment.objects.all().order_by('-reconciliation_log__opt_datetime'),
        'trade_types': TransactionDetail.TRADE_TYPES,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
        'statuses': ReconciliationAmendment.AMENDSTATUS,
    }
    return render(request, APP_NAME + '/reconciliation_amendment.html', context)


@login_check
def amend_query(request):
    try:
        reconciliation_amendments = ReconciliationAmendment.objects.all()
        status = request.GET.get('status')
        if status:
            reconciliation_amendments = reconciliation_amendments.filter(status=status)

        if not reconciliation_amendments:
            context = {'reconciliation_amendments': reconciliation_amendments}
        else:
            reconciliation_amendments = reconciliation_amendments.order_by('-reconciliation_log__opt_datetime')
            paginator = Paginator(reconciliation_amendments, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_reconciliation_amendments = paginator.page(page)
            context = {'reconciliation_amendments': p_reconciliation_amendments}
        html = render_to_string(APP_NAME + '/reconciliation_amendment_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def amend_by_hand(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    idcardno = post_data.get('trader_id')
    direction = post_data.get('trade_direction')
    credits = post_data.get('trade_credits')
    if not query_sync_status('I_SC_KHJFYEB'):
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    try:
        with transaction.atomic(using='old_credits'):
            real_credits = int(credits) if direction == '+' else -int(credits)
            update_or_insert_credits(idcardno, real_credits)
            new_credits = query_credits(idcardno)
            goods_name = post_data.get('trade_goods_name')
            if goods_name == '无':
                goods_name = None
            goods_cost = post_data.get('trade_goods_cost')
            if goods_cost == '无':
                goods_cost = None
            now = datetime.datetime.now()
            info = OrderedDict({
                'DATE_ID': now.strftime('%Y%m%d'),
                'TRADE_TYPE': post_data.get('trade_type'),
                'CUST_NO': '101' + post_data.get('trader_id'),
                'CUST_NAME': post_data.get('trader_name'),
                'TRADE_TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
                'TRADE_SCORE': 100 * int(credits),
                'TRADE_DIREC': direction,
                'NEW_CREDITS': 100 * new_credits,
                'GOODS_NAME': goods_name,
                'GOODS_COST': goods_cost,
                'TRADE_MARK': '手动补录',
                'TRADE_COMM1': post_data.get('trade_orderno'),
            })
            logger.debug(info)
            insert_trade_detail(**info)
        with transaction.atomic():
            amendment_id = post_data.get('amendment_id')
            amendment = ReconciliationAmendment.objects.get(id=amendment_id)
            amendment.status = '手动补录'
            manager_account = post_data.get('manager_account')
            manager = Manager.objects.get(account=manager_account)
            amendment.manager = manager
            amendment.amend_datetime = datetime.datetime.now()
            amendment.save()
            log = amendment.reconciliation_log
            if not ReconciliationAmendment.objects.filter(reconciliation_log=log).filter(status='未补录').exists():
                log.result = '失败但已补录'
                log.save()
        res = {'success': True, 'msg':'补录成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'补录失败'}
    return JsonResponse(res)


@login_check
def auto_amend(request):
    amendments = ReconciliationAmendment.objects.filter(status='未补录')
    manager_account = request.POST.get('manager_account')
    if not query_sync_status('I_SC_KHJFYEB'):
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    try:
        manager = Manager.objects.get(account=manager_account)
        now = datetime.datetime.now()
        for amendment in amendments:
            with transaction.atomic(using='old_credits'):
                trade_detail = amendment.transaction_detail
                trader = trade_detail.trader.user
                update_or_insert_credits(trader.idcardno, trade_detail.credits)
                new_credits = query_credits(trader.idcardno)
                info = OrderedDict({
                    'DATE_ID': now.strftime('%Y%m%d'),
                    'TRADE_TYPE': trade_detail.type,
                    'CUST_NO': '101' + trader.idcardno,
                    'CUST_NAME': trader.name,
                    'TRADE_TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'TRADE_SCORE': 100 * abs(trade_detail.credits),
                    'TRADE_DIREC': '+' if trade_detail.credits >= 0 else '-',
                    'NEW_CREDITS': 100 * new_credits,
                    'GOODS_NAME': trade_detail.coupon.name if trade_detail.coupon else None,
                    'GOODS_COST': trade_detail.coupon.credits if trade_detail.coupon else None,
                    'TRADE_MARK': '手动补录',
                    'TRADE_COMM1': trade_detail.orderno,
                })
                logger.debug(info)
                insert_trade_detail(**info)
            with transaction.atomic():
                amendment.status = '自动补录'
                amendment.manager = manager
                amendment.amend_datetime = datetime.datetime.now()
                amendment.save()
                log = amendment.reconciliation_log
                if not ReconciliationAmendment.objects.filter(reconciliation_log=log).filter(status='未补录').exists():
                    log.result = '失败但已补录'
                    log.save()
        res = {'success': True, 'msg':'补录成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'补录失败'}
    return JsonResponse(res)
