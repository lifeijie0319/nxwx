# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST
from ..logger import logger
from ..models import Manager, Term
from ..tools import get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
        'coupon_terms': Term.objects.all(),
    }
    return render(request, APP_NAME + '/coupon_term.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    coupon_term_code = request.GET.get('coupon_term_code')
    try:
        coupon_terms = Term.objects.all()
        if coupon_term_code:
            coupon_terms = coupon_terms.filter(code__contains=coupon_term_code.upper())
        context = {'coupon_terms': coupon_terms}
        html = render_to_string(APP_NAME + '/coupon_term_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def update(request):
    data = json.loads(request.body)
    logger.debug(data)
    coupon_term_id = data.pop('coupon_term_id')
    logger.debug(data)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get("manager_account"))
            coupon_term = Term.objects.get(id=coupon_term_id) 
            Term.objects.filter(id=coupon_term_id).update(**data)
            log_action(manager, 'update', coupon_term, data.keys())
            context = {'coupon_terms': Term.objects.all()}
            html = render_to_string(APP_NAME + '/coupon_term_table.html', context)
            response_data = {'success':True, 'msg':'优惠券条件更新成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'优惠券条件更新失败'}
    return JsonResponse(response_data)
