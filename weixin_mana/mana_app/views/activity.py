# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
from ..models import Activity, ActivityExt, ActivityStatistics, Manager
from ..tools import calc_page_division, gen_excel, get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'activity_types': Activity.TYPES,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/activity.html', context)


@login_check
def query(request):
    status = request.GET.get('status')
    try:
        logger.debug('QUERY GET:{}'.format(request.GET))
        if status:
            items = Activity.objects.filter(status=status)
        else:
            items = Activity.objects.all()
        paginator = Paginator(items, PAGE_SIZE)
        page = int(request.GET.get('page', 1))
        page = max(1, min(page, paginator.num_pages))
        context = {'items': paginator.page(page)}
        logger.debug('QUERY RESULT:{}'.format(context))
        html = render_to_string(APP_NAME + '/activity_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    data = json.loads(request.body)
    try:
        with transaction.atomic():
            item = Activity.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', item)
            res = {'success': True, 'msg': u'配置添加成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'配置添加失败'}
    return JsonResponse(res)


@login_check
def delete(request):
    logger.debug('CONFIG DELETE START')
    try:
        logger.debug('DELETE REQUEST:{}'.format(request.body))
        cur_item = Activity.objects.get(id=request.POST['id'])
        manager = Manager.objects.get(account=request.session.get('manager_account'))
        logger.debug('CONFIG DELETE TRANSACTION START')
        with transaction.atomic():
            log_action(manager, 'delete', cur_item)
            cur_item.delete()
            res = {'success': True, 'msg': u'配置删除成功'}
        logger.debug('CONFIG DELETE TRANSACTION END')
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'配置删除失败'}
    logger.debug('CONFIG DELETE END')
    return JsonResponse(res)


@login_check
def update(request):
    logger.debug('CONFIG UPDATE START')
    try:
        logger.debug('UPDATE REQUEST:{}'.format(request.body))
        cur_item = Activity.objects.get(id=request.POST['id'])
        manager = Manager.objects.get(account=request.session.get('manager_account'))
        logger.debug('CONFIG UPDATE TRANSACTION START')
        with transaction.atomic():
            if cur_item.status == '使用中':
                cur_item.status = '未使用'
            else:
                cur_item.status = '使用中'
            cur_item.save()
            log_action(manager, 'update', cur_item, 'status')
            res = {'success': True, 'msg': u'配置成功'}
        logger.debug('CONFIG UPDATE TRANSACTION END')
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'配置失败'}
    logger.debug('CONFIG UPDATE END')
    return JsonResponse(res)


@login_check
def upload(request):
    logger.debug(request.FILES)
    logger.debug(request.POST)
    activity_id = request.POST.get('activity_id')
    img = request.FILES.get('img')
    logger.debug(img)
    path = APP_NAME + '/media/activity/' + activity_id + '.jpg'
    logger.debug('PATH: %s', path)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, img)
    return JsonResponse({'success': True})


@login_check
def ext_query(request):
    try:
        logger.debug('QUERY GET:{}'.format(request.GET))
        items = ActivityExt.objects.filter(activity__id=request.GET['id'])
        context = {'items': items, 'activity_id': request.GET['id']}
        logger.debug('QUERY RESULT:{}'.format(context))
        html = render_to_string(APP_NAME + '/activity_ext_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
        if request.GET.get('init'):
            activity = Activity.objects.get(id=request.GET['id'])
            res['names'] = ActivityExt.MAP[activity.typ]
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def ext_add(request):
    try:
        logger.debug('REQUEST: {}'.format(request.body))
        data = json.loads(request.body)
        activity_id = data.pop('activity_id')
        logger.debug('activity_id({}): {}'.format(type(activity_id), activity_id))
        data['activity'] = Activity.objects.get(id=activity_id)
        with transaction.atomic():
            item = ActivityExt.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', item)
            res = {'success': True, 'msg': u'扩展信息添加成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'扩展信息添加失败'}
    return JsonResponse(res)


@login_check
def ext_delete(request):
    try:
        logger.debug('REQUEST: {}'.format(request.POST))
        with transaction.atomic():
            item = ActivityExt.objects.get(id=request.POST.get('id'))
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'delete', item)
            item.delete()
            res = {'success': True, 'msg': u'扩展信息删除成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'扩展信息删除失败'}
    return JsonResponse(res)


@login_check
def statistics_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'activities': Activity.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/activity_statistics.html', context)


@login_check
def statistics_query(request):
    try:
        logger.debug('QUERY GET:{}'.format(request.GET))
        activity_id = request.GET.get('activity_id')
        mode = request.GET.get('mode')
        req_page = request.GET.get('page', 1)
        if mode == 'excel':
            if activity_id:
                items = ActivityStatistics.objects.filter(activity__id=activity_id)
            else:
                items = ActivityStatistics.objects.all()
            headers = ['活动名称', '客户输入字段', '信息字段一', '信息字段二',
                       '信息字段三', '信息字段四', '信息字段五', '记录添加时间']
            data = []
            for item in items:
                activity = item.activity
                row = [activity.name, activity.key, item.col1, item.col2, item.col3,
                       item.col4, item.col5, item.add_dtime.isoformat()]
                data.append(row)
            return gen_excel(headers, data, '活动统计数据')

        if activity_id:
            count = ActivityStatistics.objects.filter(activity__id=activity_id).count()
            num_pages, cur_page, start_pos, end_pos = calc_page_division(count, req_page)
            items = ActivityStatistics.objects.filter(activity__id=activity_id)[start_pos: end_pos]
        else:
            count = ActivityStatistics.objects.count()
            num_pages, cur_page, start_pos, end_pos = calc_page_division(count, req_page)
            items = ActivityStatistics.objects.all()[start_pos: end_pos]

        context = {'items': items, 'count': count, 'num_pages': num_pages, 'page': cur_page}
        logger.debug('QUERY RESULT:{}'.format(context))
        html = render_to_string(APP_NAME + '/activity_statistics_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)
