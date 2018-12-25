# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, DEFAULT_PASSWORD, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Group, Manager
from ..tools import get_menu, log_action


@login_check
def page(request):
    #managers = Manager.objects.all()
    groups = Group.objects.all()
    bankbranchs = BankBranch.objects.all().order_by('deptno')
    manager_account = request.session.get('manager_account')
    context = {
        #'managers': managers,
        'groups': groups,
        'bankbranchs': bankbranchs,
        'roles': Manager.ROLES,
        'status': Manager.STATUS,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/manager.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        manager_name = request.GET.get('manager_name')
        manager_account = request.GET.get('manager_account')
        page = int(request.GET.get('page', 1))
        managers = Manager.objects.all().order_by('account')
        if manager_name:
            managers = managers.filter(name__contains=manager_name)
        if manager_account:
            managers = managers.filter(account=manager_account)
        print managers
        if not managers:
            context = {'managers': managers}
        else:
            paginator = Paginator(managers, PAGE_SIZE)
            page = max(1, min(page, paginator.num_pages))
            p_managers = paginator.page(page)
            context = {'managers': p_managers}
        html = render_to_string(APP_NAME + '/manager_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug('ADD MANAGER DATA: %s', post_data)

    manager_account = post_data.get('manager_account')
    if Manager.objects.filter(account=manager_account).exists():
        response_data = {'success': False, 'msg': '账户已存在'}
        return JsonResponse(response_data)

    try:
        with transaction.atomic():
            manager_role = post_data.get('manager_role')
            manager_role = manager_role if manager_role != '0' else ''

            manager_subrole = post_data.get('manager_subrole')
            manager_subrole = manager_subrole if manager_subrole != '0' else ''

            manager_bankbranch_id = post_data.get('manager_bankbranch')
            bankbranch = BankBranch.objects.get(id=int(manager_bankbranch_id))\
                if manager_bankbranch_id != '0' else None

            manager_groups = post_data.get('manager_groups')
            if not manager_groups:
                groups = []
            elif isinstance(manager_groups, list):
                group_ids = [int(group_id) for group_id in manager_groups]
                groups = Group.objects.filter(id__in=manager_groups)
            else:
                groups = Group.objects.filter(id=int(manager_groups))

            data = {
                'account': manager_account,
                'name': post_data.get('manager_name'),
                'idcardno': post_data.get('manager_idcardno'),
                'telno': post_data.get('manager_telno'),
                'role': manager_role,
                'subrole': manager_subrole,
                'bankbranch': bankbranch,
            }
            manager = Manager(**data)
            manager.set_password(DEFAULT_PASSWORD)
            manager.save()
            manager.groups = groups

            cur_manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(cur_manager, 'add', manager)
            response_data = {'success': True, 'msg':'新增用户成功'}
    except Exception, e:
        logger.debug(e)
        response_data = {'success': False, 'msg':'新增用户失败'}
    return JsonResponse(response_data)


#@login_check
#def delete(request):
#    post_data = json.loads(request.body)
#    logger.debug(post_data)
#    manager_id = post_data.get('manager_id')
#    if not Manager.objects.filter(id=manager_id).exists():
#        response_data = {'success': False, 'msg': '用户不存在'}
#        return JsonResponse(response_data)
#    try:
#        with transaction.atomic():
#            manager = Manager.objects.get(id=manager_id)
#            for group in manager.groups.all():
#                if group.name in [u'admin']:
#                    response_data = {'success': False, 'msg': group.name + '组用户禁止删除'}
#                    return JsonResponse(response_data)
#            cur_manager = Manager.objects.get(account=request.session.get('manager_account'))
#            log_action(cur_manager, 'delete', manager)
#            manager.delete()
#
#            context = {'managers': Manager.objects.all()}
#            html = render_to_string(APP_NAME + '/manager_table.html', context)
#            response_data = {'success': True, 'msg': '用户删除成功', 'html': html}
#    except Exception, e:
#        logger.exception(e)
#        response_data = {'success': False, 'msg': '用户删除失败'}
#    return JsonResponse(response_data)


@login_check
def update(request):
    try:
        post_data = json.loads(request.body)
        logger.debug(post_data)
        with transaction.atomic():
            manager_id = post_data.get('manager_id')

            manager_role = post_data.get('manager_role')
            manager_role = manager_role if manager_role != '0' else ''

            manager_subrole = post_data.get('manager_subrole')
            manager_subrole = manager_subrole if manager_subrole != '0' else ''

            manager_bankbranch_id = post_data.get('manager_bankbranch')
            bankbranch = BankBranch.objects.get(id=int(manager_bankbranch_id))\
                if manager_bankbranch_id != '0' else None

            manager_groups = post_data.get('manager_groups')
            if not manager_groups:
                groups = []
            elif isinstance(manager_groups, list):
                group_ids = [int(group_id) for group_id in manager_groups]
                groups = Group.objects.filter(id__in=manager_groups)
            else:
                groups = Group.objects.filter(id=int(manager_groups))

            data = {
                'name': post_data.get('manager_name'),
                'idcardno': post_data.get('manager_idcardno'),
                'telno': post_data.get('manager_telno'),
                'role': manager_role,
                'subrole': manager_subrole,
                'status': post_data.get('manager_status'),
                'bankbranch': bankbranch,
            }
            Manager.objects.filter(id=manager_id).update(**data)
            manager = Manager.objects.get(id=manager_id)
            manager.groups = groups
            
            cur_manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(cur_manager, 'update', manager, data.keys())
            response_data = {'success': True, 'msg':'更新用户成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'更新用户失败'}
    return JsonResponse(response_data)


def reset_password(request):
    try:
        logger.debug(request.POST)
        with transaction.atomic():
            manager_id = request.POST.get('manager_id')
            manager = Manager.objects.get(id=manager_id)
            manager.set_password(DEFAULT_PASSWORD)
            manager.save()
            cur_manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(cur_manager, 'update', manager, ['password'])
            response_data = {'success': True, 'msg':'用户密码重置成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'用户密码重置失败'}
    return JsonResponse(response_data)
