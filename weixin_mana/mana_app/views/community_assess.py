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
from ..models import BankBranch, Manager, CommunityAssess
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
    return render(request, APP_NAME + '/community_assess.html', context)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    community = post_data.get('community')
    if CommunityAssess.objects.filter(community=community).exists():
        response_data = {'success': False, 'msg': '记录已存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            community_assess = CommunityAssess.objects.create(**post_data)
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'add', community_assess)
        response_data = {'success':True, 'msg':'记录新增成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录新增失败'}
    return JsonResponse(response_data)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    community = post_data.get('community')
    try:
        community_assess = CommunityAssess.objects.get(community=community)
    except ObjectDoesNotExist:
        response_data = {'success': False, 'msg': '记录不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            #manager = Manager.objects.get(account=request.session.get('manager_account'))
            #log_action(manager, 'delete', community_assess)
            community_assess.delete()
        response_data = {'success': True, 'msg': '记录删除成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '记录删除失败'}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    community = data.get('community') 
    logger.debug(data)
    try:
        with transaction.atomic():
            community_assess = CommunityAssess.objects.get(community=community)
            price = data.get('price')
            if community_assess.price != price:
                community_assess.price = price
                community_assess.save()
                #manager = Manager.objects.get(account=request.session.get('manager_account'))
                #log_action(manager, 'update', community_assess, ['price'])
        response_data = {'success':True, 'msg':'记录更新成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'记录更新失败'}
    return JsonResponse(response_data)


@login_check
def query(request):
    logger.debug(request.GET)
    try:
        community = request.GET.get('community')
        mode = request.GET.get('mode')
        if mode == 'excel':
            if community:
                community_assesses = CommunityAssess.objects.filter(community=community).order_by('community')
            else:
                community_assesses = CommunityAssess.objects.all().order_by('community')
            data = [['小区名', '评估价格（万元）', '创建时间', '最后更新时间']]
            for community_assess in community_assesses:
                data.append(['\t' + community_assess.community, community_assess.price,
                    community_assess.add_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                    community_assess.mod_dtime.strftime('%Y-%m-%d %H:%M:%S')])
            return write_csv(data, '小区价格评估')

        count = CommunityAssess.objects.count()
        num_pages = count / PAGE_SIZE
        left_items = count % PAGE_SIZE
        num_pages = num_pages + 1 if left_items else num_pages
        page = int(request.GET.get('page', 1))
        page = max(1, min(page, num_pages))
        start_pos = (page - 1) * PAGE_SIZE
        end_pos = start_pos + PAGE_SIZE
        if community:
            p_community_assesses = CommunityAssess.objects.filter(community=community).order_by('community')[start_pos:end_pos]
        else:
            p_community_assesses = CommunityAssess.objects.all().order_by('community')[start_pos:end_pos]
        context = {'community_assesses': p_community_assesses, 'page': page, 'num_pages': num_pages, 'count': count}
        html = render_to_string(APP_NAME + '/community_assess_table.html', context)
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
            community = sheet.cell(row, 0).value.strip()
            price = sheet.cell(row, 1).value
            community_assess = CommunityAssess.objects.filter(community=community).first()
            if community_assess:
                if community_assess.price != price:
                    community_assess.price = price
                    community_assess.mod_dtime = datetime.datetime.now()
                    community_assess.save(update_fields=['price', 'mod_dtime'])
            else:
                community_assess = CommunityAssess(community=community, price=price)
                worklist.append(community_assess)
                if len(worklist) >= 1000:
                    CommunityAssess.objects.bulk_create(worklist)
                    worklist = []
            if row == sheet.nrows - 1 and len(worklist):
                CommunityAssess.objects.bulk_create(worklist)
        except Exception, e:
            logger.exception(e)
            logger.debug('ERROR ROW:%s', row)
            start = str(max(1, row - 999))
            end = str(row + 1)
            res = {'success': False, 'msg': '从第' + start + '到第' + end + '行导入失败，' + str(e)}
            return JsonResponse(res)
    return JsonResponse({'success': True})
