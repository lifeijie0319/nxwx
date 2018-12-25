# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, Manager, ManagerRegion
from ..tools import gen_excel, get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    manager = Manager.objects.get(account=manager_account)
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/manager_region.html', context)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    address_code = post_data.get('address_code')
    if ManagerRegion.objects.filter(address_code=address_code).exists():
        response_data = {'success': False, 'msg': '记录已存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            manager_account = post_data.get('manager_account')
            if not Manager.objects.filter(account=manager_account).exists():
                raise Exception('该身份证号对应的管理人员不存在')
            manager = Manager.objects.get(account=manager_account)
            if manager.role != '客户经理':
                raise Exception('该身份证号对应的管理人员不是客户经理')
            data = {
                'address_code': address_code,
                'manager': manager,
            }
            manager_region = ManagerRegion.objects.create(**data)
            #operator = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(operator, 'add', manager_region)
        response_data = {'success':True, 'msg':'记录新增成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录新增失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    address_code = post_data.get('address_code')
    try:
        manager_region = ManagerRegion.objects.get(address_code=address_code)
    except ObjectDoesNotExist:
        response_data = {'success': False, 'msg': '记录不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'delete', manager_region)
            manager_region.delete()
        response_data = {'success': True, 'msg': '记录删除成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '记录删除失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    address_code = data.get('address_code') 
    logger.debug(data)
    try:
        with transaction.atomic():
            manager_account = data.get('manager_account')
            if not Manager.objects.filter(account=manager_account).exists():
                raise Exception('该身份证号对应的管理人员不存在')
            manager = Manager.objects.get(account=manager_account)
            if manager.role != '客户经理':
                manager.role = '客户经理'
                manager.save()
            manager_region = ManagerRegion.objects.get(address_code=address_code)
            if manager_region.manager != manager:
                manager_region.manager = manager
                manager_region.save()
            #operator = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(operator, 'update', manager_region, ['manager'])
        response_data = {'success':True, 'msg':'记录更新成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录更新失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        address_code = request.GET.get('address_code')
        mode = request.GET.get('mode')
        if mode == 'excel':
            if address_code:
                manager_regions = ManagerRegion.objects.filter(address_code=address_code)\
                    .order_by('address_code')
            else:
                manager_regions = ManagerRegion.objects.all().order_by('address_code')
            headers = ['地址编码', '客户经理名称', '客户经理工号', '创建时间', '最后更新时间']
            datas = []
            for manager_region in manager_regions:
                data = [manager_region.address_code, manager_region.manager.name, manager_region.manager.account,
                    manager_region.add_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                    manager_region.mod_dtime.strftime('%Y-%m-%d %H:%M:%S')]
                datas.append(data)
            return gen_excel(headers, datas, '客户经理地址关系')

        count = ManagerRegion.objects.count()
        num_pages = count / PAGE_SIZE
        left_items = count % PAGE_SIZE
        num_pages = num_pages + 1 if left_items else num_pages
        page = int(request.GET.get('page', 1))
        page = max(1, min(page, num_pages))
        start_pos = (page - 1) * PAGE_SIZE
        end_pos = start_pos + PAGE_SIZE
        if address_code:
            p_manager_regions = ManagerRegion.objects.filter(address_code=address_code)\
                .order_by('address_code')[start_pos:end_pos]
        else:
            p_manager_regions = ManagerRegion.objects.all().order_by('address_code')[start_pos:end_pos]
        context = {'manager_regions': p_manager_regions, 'page': page, 'num_pages': num_pages, 'count': count}
        html = render_to_string(APP_NAME + '/manager_region_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败：' + str(e)}
    return JsonResponse(res)


def upload(request):
    upfile = request.FILES.get('upfile')
    path = APP_NAME + '/media/excel/%s' % upfile.name
    logger.debug('PATH: %s', path)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, upfile)
    wkbook = xlrd.open_workbook(path)
    sheet = wkbook.sheet_by_index(0)
    worklist = []
    for row in range(1, sheet.nrows):
        try:
            if row % 1000 == 0:
                logger.debug(row)
            manager_account = sheet.cell(row, 1).value.strip()
            if not Manager.objects.filter(account=manager_account).exists():
                raise Exception('该工号对应的管理人员不存在')
            manager = Manager.objects.get(account=manager_account)
            if manager.role != '客户经理':
                manager.role = '客户经理'
                manager.save(update_fields=['role'])
            address_code = sheet.cell(row, 0).value.strip()
            manager_region = ManagerRegion.objects.filter(address_code=address_code).first()
            if manager_region:
                if manager_region.manager != manager:
                    manager_region.manager = manager
                    manager_region.mod_dtime = datetime.datetime.now()
                    manager_region.save(update_fields=['manager', 'mod_dtime'])
            else:
                manager_region = ManagerRegion(address_code=address_code, manager=manager)
                worklist.append(manager_region)
                if len(worklist) >= 1000:
                    logger.debug(row)
                    ManagerRegion.objects.bulk_create(worklist)
                    worklist = []
            if row == sheet.nrows - 1 and len(worklist):
                ManagerRegion.objects.bulk_create(worklist)
        except Exception, e:
            logger.exception(e)
            start = str(max(1, row - 999))
            end = str(row + 1)
            res = {'success': False, 'msg': '从第' + start + '到第' + end + '行导入失败：' + str(e)}
            return JsonResponse(res)
    return JsonResponse({'success': True})
