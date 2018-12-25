# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Manager, Seller, Shop, WithdrawAppplication
from ..tools import gen_excel, generate_orderno, get_authorized_banks, get_menu, log_action, transaction_detail_save


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    manager = Manager.objects.get(account=manager_account)
    banks = get_authorized_banks(manager.bankbranch)
    context = {
        'banks': banks,
        #'withdraw_applications': WithdrawAppplication.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/withdraw_application.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        bank_id = request.GET.get('bank')
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)
        shops = Shop.objects.filter(bank__in=banks)
        sellers = [shop.seller for shop in shops]
        withdraw_applications = WithdrawAppplication.objects.filter(seller__in=sellers)

        start_date = request.GET.get('start_date')
        if start_date:
            withdraw_applications = withdraw_applications.filter(application_date__gte=start_date)
        end_date = request.GET.get('end_date')
        if end_date:
            withdraw_applications = withdraw_applications.filter(application_date__lte=end_date)
        telno = request.GET.get('telno')
        if telno:
            withdraw_applications = withdraw_applications.filter(seller__telno=telno)
        mode = request.GET.get('mode')

        if mode == 'excel':
            headers = ['统计起始日期', '统计结束日期', '维护机构号', '商户名称', '联系方式', '关联账户',
                '提现积分数', '是否自开增值税发票', '实际提现金额（元）', '提现申请日期']
            datas = []
            for withdraw_application in withdraw_applications:
                data = [start_date, end_date, withdraw_application.seller.shop_set.first().bank.deptno,
                    withdraw_application.seller.shop_set.first().name, withdraw_application.seller.telno,
                    withdraw_application.seller.account, withdraw_application.credits,
                    bool(withdraw_application.receipt_provision), withdraw_application.balance,
                    withdraw_application.application_date.isoformat()]
                datas.append(data)
            return gen_excel(headers, datas, '商户提现申请')

        if not withdraw_applications:
            context = {'withdraw_applications': withdraw_applications}
        else:
            paginator = Paginator(withdraw_applications, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_withdraw_applications = paginator.page(page)
            context = {'withdraw_applications': p_withdraw_applications}
        html = render_to_string(APP_NAME + '/withdraw_application_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def audit(request):
    logger.debug(request.body)
    post_data = json.loads(request.body)
    withdraw_application_id = post_data.get('withdraw_application_id')
    audit = post_data.get('audit')
    try:
        with transaction.atomic():
            manager_account = request.session.get('manager_account')
            manager = Manager.objects.get(account=manager_account)
            withdraw_application = WithdrawAppplication.objects.get(id=withdraw_application_id)
            if audit == 'pass':
                withdraw_application.status = u'已审批'
                msg = u'审批通过'
                seller = withdraw_application.seller
                seller.credits -= withdraw_application.credits
                seller.save()
                orderno = generate_orderno(1)[0]
                transaction_detail_save(seller, None, -withdraw_application.credits, '商户提现', 
                    '提现' + str(withdraw_application.credits) + '积分', orderno)
            elif audit == 'reject':
                withdraw_application.status = u'未通过'
                msg = u'审批不通过'
            withdraw_application.manager = manager
            withdraw_application.audit_date = datetime.date.today()
            withdraw_application.save()
            log_action(manager, 'update', withdraw_application, ['status', 'manager', 'audit_date'])
            res = {'success': True, 'msg': msg}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'服务器错误'}
    return JsonResponse(res)
