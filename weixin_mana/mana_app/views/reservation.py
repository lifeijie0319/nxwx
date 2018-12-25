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
from ..models import *
from ..tools import get_menu, log_action


def date_get(dtstr):
    return datetime.datetime.strptime(dtstr,'%Y-%m-%d').date()


@login_check
def page(request):
    setting = ReservationForbidenDate.objects.all()
    manager_account = request.session.get('manager_account')
    context = {
        'datas': setting,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/reservation_date_setting.html', context)


@login_check
def query(request):
    manager_name = request.GET.get('manager_name')
    try:
        settings = ReservationForbidenDate.objects.all().order_by('date')
        if manager_name:
            settings = settings.filter(manager__name__contains=manager_name)

        if not settings:
            context = {'settings': settings}
        else:
            paginator = Paginator(settings, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_settings = paginator.page(page)
            context = {'settings': p_settings}

        html = render_to_string( APP_NAME + '/reservation_date_setting_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    manager = Manager.objects.get(account=request.session.get('manager_account'))
    try:
        with transaction.atomic():
            data = {
                    'manager': manager,
                    'date':date_get(post_data.get('date')),
                    'dec':post_data.get('dec')
                }
            setting = ReservationForbidenDate(**data)
            setting.save()
            log_action(manager, 'add', setting)
            res = {'success': True, 'msg': u'记录添加成功'}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录添加失败'}
    return JsonResponse(res)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    id = post_data.get('id')
    try:
        if not ReservationForbidenDate.objects.filter(id=id).exists():
            res = {'success': False, 'msg': u'记录不存在'}
        else:
            with transaction.atomic():
                setting = ReservationForbidenDate.objects.get(id=id)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                log_action(manager, 'delete', setting)
                setting.delete()
                res = {'success': True, 'msg': u'删除成功'}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录删除失败'}
    return JsonResponse(res)


@login_check
def update(request):
    post_data = json.loads(request.body)
    id = post_data.get('id')
    manager = Manager.objects.get(account=request.session.get('manager_account'))
    try:
        if not ReservationForbidenDate.objects.filter(id=id).exists():
            res = {'success': False, 'msg': u'记录不存在'}
        else:
            with transaction.atomic():
                data = {
                    'manager': manager,
                    'date': date_get(post_data.get('date')),
                    'dec':post_data.get('dec')
                }
                ReservationForbidenDate.objects.filter(id=post_data.get('id')).update(**data)
                res = {'success': True, 'msg': u'更新成功'}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录更新失败'}
    return JsonResponse(res)




#设置预约页面的连续不可用次数
@login_check
def setting_page(request):
    setting = ReservationNum.objects.all()
    manager_account = request.session.get('manager_account')
    context = {
        'datas': setting,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/reservation_second_setting.html', context)


@login_check
def setting_query(request):
    setting_name = request.GET.get('sign_name')
    try:
        if setting_name:
            setting = ReservationNum.objects.all().filter(manager__account=setting_name)
        else:
            setting = ReservationNum.objects.all()
        context = {'datas': setting}
        html = render_to_string( APP_NAME + '/reservation_second_setting_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception ,e:
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def setting_add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    manager = Manager.objects.get(account=request.session.get('manager_account'))
    try:
        data = {
            'manager': manager,
            'year': 0,
            'num': post_data.get('num'),
            'month':0,
            'day': 0,
            'hour': 0,
            'mintue':0,
            'second': post_data.get('second')
            }
        setting = ReservationNum(**data)
        setting.save()
        settings = ReservationNum.objects.all()
        context = {'datas': settings}
        html = render_to_string(APP_NAME + '/reservation_second_setting_table.html', context)
        res = {'success': True, 'msg': u'记录添加成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录添加失败'}
    return JsonResponse(res)


@login_check
def setting_delete(request):
    post_data = json.loads(request.body)
    id = post_data.get('id')
    try:
        if not ReservationNum.objects.filter(id=id).exists():
            res = {'success': False, 'msg': u'记录不存在'}
        else:
            setting = ReservationNum.objects.get(id=id)
            setting.delete()
            settings = ReservationNum.objects.all()
            context = {'datas': settings}
            html = render_to_string(APP_NAME + '/reservation_second_setting_table.html', context)
            res = {'success': True, 'msg': u'删除成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录删除失败'}
    return JsonResponse(res)


@login_check
def setting_update(request):
    post_data = json.loads(request.body)
    id = post_data.get('id')
    manager = Manager.objects.get(account=request.session.get('manager_account'))
    try:
        if not ReservationNum.objects.filter(id=id).exists():
            res = {'success': False, 'msg': u'记录不存在'}
        else:
            with transaction.atomic():
                data = {
                    'manager': manager,
                    'year': 0,
                    'num': post_data.get('num'),
                    'month': 0,
                    'day': 0,
                    'hour': 0,
                    'mintue':0,
                    'second':post_data.get('second')
                }
                ReservationNum.objects.filter(id=post_data.get('id')).update(**data)
                for item in ReservationNum.objects.filter(id=post_data.get('id')):
                    log_action(manager, 'update', item, data.keys())
                settings = ReservationNum.objects.all()
                context = {'datas': settings}
                html = render_to_string(APP_NAME + '/reservation_second_setting_table.html', context)
                res = {'success': True, 'msg': u'更新成功', 'html': html}
    except Exception ,e:
        logger.debug(e)
        res = {'success': False, 'msg': u'记录更新失败'}
    return JsonResponse(res)
