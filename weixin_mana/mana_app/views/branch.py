# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from decimal import Decimal
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Manager
from ..tools import get_menu, log_action

@login_check
def page(request):
    branches = BankBranch.objects.all().order_by('deptno')
    manager_account = request.session.get('manager_account')
    context = {
        'levels': BankBranch.LEVELS,
        'branches': branches,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/branch.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    branch_name = request.GET.get('branch_name')
    try:
        branches = BankBranch.objects.order_by('deptno')
        if branch_name:
            branches = branches.filter(name__contains=branch_name)
        if not branches:
            context = {'branches': branches}
        else:
            paginator = Paginator(branches, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_branches = paginator.page(page)
            context = {'branches': p_branches}
        html = render_to_string(APP_NAME + '/branch_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            parent_id = post_data.get('parent', '0')
            parent = BankBranch.objects.get(id=parent_id) if parent_id != '0' else None
            data = {
                'name': post_data.get('name'),
                'telno': post_data.get('telno'),
                'deptno': post_data.get('deptno'),
                'latitude': Decimal(post_data.get('latitude')),
                'longitude': Decimal(post_data.get('longitude')),
                'is_map': post_data.get('is_map'),
                'is_withdrawal': post_data.get('is_withdrawal'),
                'is_oppen_account': post_data.get('is_oppen_account'),
                'is_etc': post_data.get('is_etc'),
                'is_loan': post_data.get('is_loan'),
                'address': post_data.get('address'),
                'parent': parent,
                'level': post_data.get('level'),
                'telno': post_data.get('telno'),
                'officehours': post_data.get('officehours') if post_data.get('officehours') else '8:00-17:00',
            }
            branch = BankBranch(**data)
            branch.save()
            log_action(manager, 'add', branch)
            res = {'success': True, 'msg': u'记录添加成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'记录添加失败'}
    return JsonResponse(res)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    branch_id = post_data.get('branch_id')
    try:
        with transaction.atomic():
            if not BankBranch.objects.filter(id=branch_id).exists():
                res = {'success': False, 'msg': u'记录不存在'}
            else:
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                branch = BankBranch.objects.get(id=branch_id)
                log_action(manager, 'delete', branch)
                branch.delete()
                res = {'success': True, 'msg': u'删除成功'}
    except Exception ,e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录删除失败'}
    return JsonResponse(res)


@login_check
def update(request):
    post_data = json.loads(request.body)
    branch_id = post_data.get('branch_id')
    try:
        if not BankBranch.objects.filter(id=branch_id).exists():
            res = {'success': False, 'msg': u'记录不存在'}
        else:
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            parent_id = post_data.get('parent') if post_data.get('parent') != '0' else None
            data = {
                'name': post_data.get('name'),
                'latitude': Decimal(post_data.get('latitude')),
                'longitude': Decimal(post_data.get('longitude')),
                'is_map': post_data.get('is_map'),                  
                'is_withdrawal': post_data.get('is_withdrawal'),
                'is_oppen_account': post_data.get('is_oppen_account'),
                'is_etc': post_data.get('is_etc'),
                'is_loan': post_data.get('is_loan'),
                'is_dgkh': post_data.get('is_dgkh'),
                'deptno': post_data.get('deptno'),
                'address': post_data.get('address'),
                'parent': parent_id,
                'level': post_data.get('level'),
                'telno': post_data.get('telno'),
                'officehours': post_data.get('officehours')
            }
            with transaction.atomic():
                BankBranch.objects.filter(id=branch_id).update(**data)
                bankbranch = BankBranch.objects.get(id=branch_id)
                log_action(manager, 'update', bankbranch, data.keys())
                res = {'success': True, 'msg': u'更新成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'记录更新失败'}
    return JsonResponse(res)
