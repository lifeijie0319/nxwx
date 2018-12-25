# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string


from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import RepetitionExclude,TransactionDetail
from ..tools import get_menu, log_action,generate_orderno,transaction_detail_save,gen_excel



@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/write_off_page.html', context)


@login_check
def query(request):
    try:
        opposite = request.GET.get('seller_name')

        awards = TransactionDetail.objects.filter(type= '商户扫码兑换收取')
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        if start_date:
            start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            logger.debug(start_datetime)
            awards = awards.filter(trade_datetime__gte=start_datetime)
        end_date = request.GET.get('end_date')
        logger.debug('END_DATE: %s', type(end_date))
        if end_date:
            end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            logger.debug(end_datetime)
            awards = awards.filter(trade_datetime__lte=end_datetime)
        if opposite:
            awards = awards.filter(opposite__name__contains=opposite)
        mode = request.GET.get('mode')

        if mode == 'excel':
            headers = ['交易人', '优惠券名称', '优惠券类别','优惠类别','满减起点积分','消费抵用积分', '核销时间', '核销商户','交易编号','交易信息']
            datas = []
            for award in awards:
                if award.coupon :
                    data = [award.opposite.name,award.coupon.name,
                       award.coupon.busi_type,award.coupon.discount_type,
                       award.coupon.discount_startline,
                       award.coupon.value,award.trade_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                       award.trader.name,award.orderno,award.info]
                else:
                    data = [award.opposite.name,None,None,
                        award.trade_datetime,award.trader.name,award.orderno,
                        award.info]
                datas.append(data)
            return gen_excel(headers, datas, '赠送清单')

        if not awards:
            context = {'lottery_records': awards}
        else:
            paginator = Paginator(awards, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_awards = paginator.page(page)
            context = {'lottery_records': p_awards}
        html = render_to_string(APP_NAME + '/write_off_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)



