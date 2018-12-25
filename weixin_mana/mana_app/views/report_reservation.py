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
from ..models import BankBranch, Manager, Reservation
from ..tools import dtime_minus, gen_excel, get_authorized_banks, get_menu, log_action


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
        'types': Reservation.TYPES,
    }
    return render(request, APP_NAME + '/report_reservation.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        bank_id = request.GET.get('bank')
        logger.debug('BANK_ID: %s', bank_id)
        my_bank = BankBranch.objects.get(id=bank_id)
        banks = get_authorized_banks(my_bank)
        reservations = Reservation.objects.filter(branch__in=banks)

        apply_date = request.GET.get('apply_date')
        if apply_date:
            start = datetime.datetime.strptime(apply_date, '%Y-%m-%d')
            end = start + datetime.timedelta(days=1)
            logger.debug(start)
            reservations = reservations.filter(apply_dtime__range=(start, end))

        busi_type = request.GET.get('type')
        if busi_type != 'all':
            reservations = reservations.filter(busi_type=busi_type)

        #reservation_date = request.GET.get('reservation_date')
        #if reservation_date:
        #    ret_reservations = []
        #    for reservation in reservations:
        #        if hasattr(reservation, 'numbertakingreservation') and\
        #            reservation.numbertakingreservation.taking_time.strftime('%Y-%m-%d') == reservation_date:
        #            ret_reservations.append(reservation)
        #        if hasattr(reservation, 'withdrawalreservation') and\
        #            reservation.withdrawalreservation.withdrawaltime.strftime('%Y-%m-%d') == reservation_date:
        #            ret_reservations.append(reservation)
        #    reservations = ret_reservations
        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['客户申请时间', '客户名称', '身份证号码', '联系方式', '选择网点', '预约业务种类',
                '预约状态', '应答客户经理', '客户经理工号', '客户经理归属机构', '受理时间', '响应间隔']
            datas = []
            for reservation in reservations:
                data = [
                    reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                    reservation.user.name,
                    reservation.user.idcardno,
                    reservation.user.telno,
                    reservation.branch.name,
                    reservation.busi_type,
                    reservation.status,
                    reservation.handler.name if reservation.handler else None,
                    reservation.handler.account if reservation.handler else None,
                    reservation.handler.bankbranch.name if reservation.handler else None,
                    reservation.deal_dtime.strftime('%Y-%m-%d %H:%M:%S') if reservation.deal_dtime else None,
                    dtime_minus(reservation.deal_dtime, reservation.apply_dtime) if reservation.deal_dtime else None,
                    reservation.reservationkdd.orgname if reservation.busi_type == '快抵贷' else None,
                    reservation.reservationkdd.assess_price if reservation.busi_type == '快抵贷' else None]
                datas.append(data)
            return gen_excel(headers, datas, '预约报表')

        if not reservations:
            context = {'reservations': reservations}
        else:
            paginator = Paginator(reservations, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_reservations = paginator.page(page)
            context = {'reservations': p_reservations}

        html = render_to_string(APP_NAME + '/report_reservation_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)

