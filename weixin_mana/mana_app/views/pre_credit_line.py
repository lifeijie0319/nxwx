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
from ..models import BankBranch, Manager, PreCreditLine
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
    return render(request, APP_NAME + '/pre_credit_line.html', context)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    cusno = post_data.get('cusno')
    if PreCreditLine.objects.filter(cusno=cusno).exists():
        response_data = {'success': False, 'msg': '记录已存在'}
        return JsonResponse(response_data)
    manager_account = post_data.get('manager_account')
    if not Manager.objects.filter(account=manager_account).exists():
        response_data = {'success': False, 'msg': '该工号对应的管理人员不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=manager_account)
            if manager.role != '客户经理':
                manager.role = '客户经理'
                manager.save()
            data = {
                'cusno': cusno,
                'limit': int(post_data.get('limit')),
                'manager': manager,
            }
            pre_credit_line = PreCreditLine.objects.create(**data)
            #operator = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(operator, 'add', pre_credit_line)
        response_data = {'success':True, 'msg':'记录新增成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录新增失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    cusno = post_data.get('cusno')
    try:
        pre_credit_line = PreCreditLine.objects.get(cusno=cusno)
    except ObjectDoesNotExist:
        response_data = {'success': False, 'msg': '记录不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'delete', pre_credit_line)
            pre_credit_line.delete()
        response_data = {'success': True, 'msg': '记录删除成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '记录删除失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    cusno = data.pop('cusno') 
    logger.debug(data)
    manager_account = data.get('manager_account')
    if not Manager.objects.filter(account=manager_account).exists():
        response_data = {'success': False, 'msg': '该工号对应的管理人员不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=manager_account)
            if manager.role != '客户经理':
                manager.role = '客户经理'
                manager.save()
            pre_credit_line = PreCreditLine.objects.get(cusno=cusno)
            pre_credit_line.limit = int(data.get('limit'))
            pre_credit_line.manager = manager
            pre_credit_line.save()
            #operator = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(operator, 'update', pre_credit_line, ['limit', 'manager'])
        response_data = {'success':True, 'msg':'记录更新成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录更新失败：' + str(e)}
    return JsonResponse(response_data)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        cusno = request.GET.get('cusno')
        mode = request.GET.get('mode')
        if mode == 'excel':
            if cusno:
                pre_credit_lines = PreCreditLine.objects.filter(cusno=cusno).order_by('cusno')
            else:
                pre_credit_lines = PreCreditLine.objects.all().order_by('cusno')
            data = [['客户号', '预授信额度', '客户经理姓名', '客户经理工号', '创建时间', '最后更新时间']]
            for pre_credit_line in pre_credit_lines:
                data.append(['\t' + pre_credit_line.cusno, pre_credit_line.limit,
                    pre_credit_line.manager.name, pre_credit_line.manager.account,
                    pre_credit_line.add_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                    pre_credit_line.mod_dtime.strftime('%Y-%m-%d %H:%M:%S')])
            return write_csv(data, '客户预授信额度')

        count = PreCreditLine.objects.count()
        num_pages = count / PAGE_SIZE
        left_items = count % PAGE_SIZE
        num_pages = num_pages + 1 if left_items else num_pages
        page = int(request.GET.get('page', 1))
        page = max(1, min(page, num_pages))
        start_pos = (page - 1) * PAGE_SIZE
        end_pos = start_pos + PAGE_SIZE
        if cusno:
            p_pre_credit_lines = PreCreditLine.objects.filter(cusno=cusno).order_by('cusno')[start_pos:end_pos]
        else:
            p_pre_credit_lines = PreCreditLine.objects.all().order_by('cusno')[start_pos:end_pos]
        context = {'pre_credit_lines': p_pre_credit_lines, 'page': page, 'num_pages': num_pages, 'count': count}
        html = render_to_string(APP_NAME + '/pre_credit_line_table.html', context)
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
            manager_account = sheet.cell(row, 2).value.strip()
            if not Manager.objects.filter(account=manager_account).exists():
                raise Exception('该工号对应的管理人员不存在')
            manager = Manager.objects.get(account=manager_account)
            update_fields = []
            if manager.role != '客户经理':
                update_fields.append('role')
                manager.role = '客户经理'
            manager.save(update_fields=update_fields)
            cusno = sheet.cell(row, 0).value.strip()
            limit = int(sheet.cell(row, 1).value)
            pre_credit_line = PreCreditLine.objects.filter(cusno=cusno).first()
            if pre_credit_line:
                update_fields = []
                if pre_credit_line.limit != limit:
                    pre_credit_line.limit = limit
                    update_fields.append('limit')
                if pre_credit_line.manager != manager:
                    pre_credit_line.manager = manager
                    update_fields.append('manager')
                if update_fields:
                    pre_credit_line.mod_dtime = datetime.datetime.now()
                    update_fields.append('mod_dtime')
                pre_credit_line.save(update_fields=update_fields)
            else:
                pre_credit_line = PreCreditLine(cusno=cusno, limit=limit, manager=manager)
                worklist.append(pre_credit_line)
                if row >= 1000:
                    logger.debug(row)
                    PreCreditLine.objects.bulk_create(worklist)
                    worklist = []
            if row == sheet.nrows - 1 and len(worklist):
                PreCreditLine.objects.bulk_create(worklist)
        except Exception, e:
            logger.exception(e)
            start = str(max(1, row - 999))
            end = str(row + 1)
            res = {'success': False, 'msg': '从第' + start + '到第' + end + '行导入失败：' + str(e)}
            return JsonResponse(res)
    return JsonResponse({'success': True})
