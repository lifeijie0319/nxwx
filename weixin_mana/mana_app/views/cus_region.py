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
from ..models import BankBranch, Manager, CusRegion
from ..tools import get_menu, log_action, write_csv


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    manager = Manager.objects.get(account=manager_account)
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/cus_region.html', context)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    cusno = post_data.get('cusno')
    if CusRegion.objects.filter(cusno=cusno).exists():
        response_data = {'success': False, 'msg': '记录已存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            cus_region = CusRegion.objects.create(**post_data)
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'add', cus_region)
        response_data = {'success':True, 'msg':'记录新增成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录新增失败'}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    cusno = post_data.get('cusno')
    try:
        cus_region = CusRegion.objects.get(cusno=cusno)
    except ObjectDoesNotExist:
        response_data = {'success': False, 'msg': '记录不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'delete', cus_region)
            cus_region.delete()
        response_data = {'success': True, 'msg': '记录删除成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '记录删除失败'}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    cusno = data.get('cusno') 
    logger.debug(data)
    try:
        with transaction.atomic():
            cus_region = CusRegion.objects.get(cusno=cusno)
            address_code = data.get('address_code')
            if cus_region.address_code != address_code:
                cus_region.address_code = address_code
                cus_region.save()
                #manager = Manager.objects.get(account=request.session.get('manager_account'))
                #log_action(manager, 'update', cus_region, ['address_code'])
        response_data = {'success':True, 'msg':'记录更新成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录更新失败'}
    return JsonResponse(response_data)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        cusno = request.GET.get('cusno')
        mode = request.GET.get('mode')
        if mode == 'excel':
            if cusno:
                cus_regions = CusRegion.objects.filter(cusno=cusno).order_by('cusno')
            else:
                cus_regions = CusRegion.objects.all().order_by('cusno')
            data = [['客户号', '地址编码', '创建时间', '最后更新时间']]
            for cus_region in cus_regions:
                data.append(['\t' + cus_region.cusno, cus_region.address_code,
                    cus_region.add_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                    cus_region.mod_dtime.strftime('%Y-%m-%d %H:%M:%S')])
            return write_csv(data, '客户归属地区')

        count = CusRegion.objects.count()
        num_pages = count / PAGE_SIZE
        left_items = count % PAGE_SIZE
        num_pages = num_pages + 1 if left_items else num_pages
        page = int(request.GET.get('page', 1))
        page = max(1, min(page, num_pages))
        start_pos = (page - 1) * PAGE_SIZE
        end_pos = start_pos + PAGE_SIZE
        if cusno:
            p_cus_regions = CusRegion.objects.filter(cusno=cusno).order_by('cusno')[start_pos:end_pos]
        else:
            p_cus_regions = CusRegion.objects.all().order_by('cusno')[start_pos:end_pos]
        context = {'cus_regions': p_cus_regions, 'page': page, 'num_pages': num_pages, 'count': count}
        html = render_to_string(APP_NAME + '/cus_region_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
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
    now = datetime.datetime.now()
    worklist = []
    for row in range(1, sheet.nrows):
        try:
            if row % 1000 == 0:
                logger.debug(row)
            cusno = sheet.cell(row, 0).value.strip()
            address_code = sheet.cell(row, 1).value.strip()
            cus_region = CusRegion.objects.filter(cusno=cusno).first()
            if cus_region:
                if cus_region.address_code != address_code:
                    cus_region.address_code = address_code
                    cus_region.mod_dtime = datetime.datetime.now()
                    cus_region.save(update_fields=['address_code', 'mod_dtime'])
            else:
                cus_region = CusRegion(cusno=cusno, address_code=address_code)
                worklist.append(cus_region)
                if len(worklist) >= 1000:
                    CusRegion.objects.bulk_create(worklist)
                    worklist = []
            if row == sheet.nrows - 1 and len(worklist):
                CusRegion.objects.bulk_create(worklist)
        except Exception, e:
            logger.exception(e)
            logger.debug('ERROR ROW:%s', row)
            start = str(max(1, row - 999))
            end = str(row + 1)
            res = {'success': False, 'msg': '从第' + start + '到第' + end + '行导入失败，' + str(e)}
            return JsonResponse(res)
    return JsonResponse({'success': True})
