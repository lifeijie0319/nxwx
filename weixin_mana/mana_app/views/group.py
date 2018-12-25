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
from ..models import Group, Menu, Manager
from ..tools import get_menu, get_menu_jstree_json, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'groups': Group.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/group.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    group_name = request.GET.get('group_name')
    try:
        groups = Group.objects.all()
        if group_name:
            groups = groups.filter(name__contains=group_name)
        logger.debug(groups)
        context = {'groups': groups}
        html = render_to_string(APP_NAME + '/group_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except:
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    group_name = post_data.get('group_name')
    if Group.objects.filter(name = group_name).exists():
        response_data = {'success': False, 'msg': '用户组已存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            group = Group.objects.create(name=group_name)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', group)
            context = {'groups': Group.objects.all()}
            html = render_to_string(APP_NAME + '/group_table.html', context)
            response_data = {'success':True, 'msg':'用户组新增成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'用户组新增失败'}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    group_id = post_data.get('group_id')
    if not Group.objects.filter(id = group_id).exists():
        response_data = {'success': False, 'msg': '用户组不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            group = Group.objects.get(id = group_id)
            if group.name in [u'admin']:
                response_data = {'success': False, 'msg': '用户组禁止删除'}
                return JsonResponse(response_data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'delete', group)
            group.delete()
            context = {'groups': Group.objects.all()}
            html = render_to_string(APP_NAME + '/group_table.html', context)
            response_data = {'success': True, 'msg': '用户组删除成功', 'html': html}
    except:
        response_data = {'success': False, 'msg': '用户组删除失败'}
    return JsonResponse(response_data)


@login_check
def update(request):
    logger.debug(request.body)
    post_data = json.loads(request.body)
    group_id = post_data.get('group_id')
    group_name = post_data.get('group_name')
    if not Group.objects.filter(id=group_id).exists():
        response_data = {'success': False, 'msg': '用户组不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            Group.objects.filter(id=group_id).update(name=group_name)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            for group in Group.objects.filter(id=group_id):
                log_action(manager, 'update', group, ['name'])
            context = {'groups': Group.objects.all()}
            html = render_to_string(APP_NAME + '/group_table.html', context)
            response_data = {'success':True, 'msg':'用户组更新成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'用户组更新失败'}
    return JsonResponse(response_data)    


@login_check
def menu(request):
    post_data = json.loads(request.body)
    group_id = post_data.get('group_id')
    logger.debug(group_id)
    menu = get_menu_jstree_json(group_id)
    return JsonResponse(menu)


@login_check
def menu_update(request):
    logger.debug(request.body)
    post_data = json.loads(request.body)
    group_id = post_data.get('group_id')
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            group = Group.objects.get(id=group_id)
            menu_ids = post_data.get('menu')
            menus = Menu.objects.filter(id__in=menu_ids)
            logger.debug(menus)
            group.menus.set(menus)
            log_action(manager, 'update', group, ['menus'])
            response_data = {'success': True, 'msg': '用户组菜单权限设置完成'}
    except:
        response_data = {'success': False, 'msg': '用户组菜单权限设置失败'}
    return JsonResponse(response_data)

