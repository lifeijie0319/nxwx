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
from ..models import CommonParam, Manager
from ..tools import get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'params': CommonParam.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/param.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    param_name = request.GET.get('param_name')
    try:
        params = CommonParam.objects.all()
        if param_name:
            params = params.filter(name__contains=param_name)
        context = {'params': params}
        html = render_to_string(APP_NAME + '/param_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    param_name = post_data.get('name')
    if CommonParam.objects.filter(name=param_name).exists():
        response_data = {'success': False, 'msg': '参数已存在'}
        return JsonResponse(response_data)
    data = {
        'name': param_name,
        'value': post_data.get('value'),
        'remark': post_data.get('remark'),
    }
    try:
        with transaction.atomic():
            param = CommonParam.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', param)
            context = {'params': CommonParam.objects.all()}
            html = render_to_string(APP_NAME + '/param_table.html', context)
            response_data = {'success':True, 'msg':'参数新增成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'参数新增失败'}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    param_id = post_data.get('param_id')
    if not CommonParam.objects.filter(id=param_id).exists():
        response_data = {'success': False, 'msg': '参数不存在'}
        return JsonResponse(response_data)
    param = CommonParam.objects.get(id=param_id)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', param)
            param.delete()
            context = {'params': CommonParam.objects.all()}
            html = render_to_string(APP_NAME + '/param_table.html', context)
            response_data = {'success': True, 'msg': '参数删除成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '参数删除失败'}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    logger.debug(data)
    param_id = data.pop('param_id')
    logger.debug(data)
    try:
        CommonParam.objects.filter(id=param_id).update(**data)
        manager = Manager.objects.get(account=request.session.get('manager_account'))
        param = CommonParam.objects.get(id=param_id)
        log_action(manager, 'update', param, data.keys())
        context = {'params': CommonParam.objects.all()}
        html = render_to_string(APP_NAME + '/param_table.html', context)
        response_data = {'success':True, 'msg':'参数更新成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'参数更新失败'}
    return JsonResponse(response_data)
