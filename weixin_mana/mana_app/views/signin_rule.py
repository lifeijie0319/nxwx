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
from ..models import Manager, SignRule
from ..tools import get_menu, log_action


@login_check
def page(request):
    signin_rules  = SignRule.objects.all()
    manager_account = request.session.get('manager_account')
    context = {
        'signin_rules': signin_rules,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request,APP_NAME+ '/signin.html', context)


@login_check
def add(request):
    data = json.loads(request.body)
    logger.debug(data)
    try:
        with transaction.atomic():
            sign = SignRule.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', sign)
            context ={'signin_rules': SignRule.objects.all()}
            html = render_to_string(APP_NAME + '/signin_table.html', context)
            res = {'success': True, 'msg': u'添加签到规则成功', 'html':html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'添加签到规则失败'}
    return JsonResponse(res)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    signin_rule_id = post_data.get('signin_rule_id')
    try:
        if not SignRule.objects.filter(id=signin_rule_id).exists():
            res = {'success': False, 'msg': u'签到规则不存在'}
        else:
            with transaction.atomic():
                signin_rule = SignRule.objects.get(id=signin_rule_id)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                log_action(manager, 'delete', signin_rule)
                signin_rule.delete()
                context = {'signin_rules': SignRule.objects.all()}
                html = render_to_string(APP_NAME + '/signin_table.html', context)
                res = {'success':True, 'msg':u'签到规则删除成功', 'html':html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': '签到规则删除失败'}
    return JsonResponse(res)


@login_check
def update(request):
    data = json.loads(request.body)
    signin_rule_id = data.pop('signin_rule_id')
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            SignRule.objects.filter(id=signin_rule_id).update(**data)
            for item in SignRule.objects.filter(id=signin_rule_id):
                log_action(manager, 'update', item, data.keys())
            context = {'signin_rules': SignRule.objects.all()}
            html = render_to_string(APP_NAME + '/signin_table.html', context)
            res = {'success':True,'msg':u'更新成功','html':html}
    except Exception, e:
        logger.debug(e)
        res = {'success':False,'msg':u'更新失败'}
    return JsonResponse(res)
