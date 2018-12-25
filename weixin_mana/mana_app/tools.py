# -*- coding: utf-8 -*-
import codecs
import csv
import datetime
import json
import random
import StringIO
import xlwt

from django.http import HttpResponse
from django.utils.http import urlquote

from .config import PAGE_SIZE
from .logger import logger
from .models import Group, LogInfo, Manager, Menu, TransactionDetail


def get_menu(manager_account):
    groups = Manager.objects.get(account=manager_account).groups.all()
    logger.debug(groups)
    menu_set = set()
    set_lv3 = set()
    set_lv2 = set()
    set_lv1 = set()
    for group in groups:
        menu_set |= set(group.menus.all())
    logger.debug(menu_set)
    for menu in menu_set:
        if menu.level == 1:
            set_lv1.add(menu)
        elif menu.level == 2:
            set_lv2.add(menu)
        elif menu.level == 3:
            set_lv3.add(menu)
    logger.debug('%s\n%s\n%s', set_lv3, set_lv2, set_lv1)
    menu = construct_menu(set_lv3, set_lv2, set_lv1)
    logger.debug(menu)
    return menu


def construct_menu(set_lv3, set_lv2, set_lv1):
    menu_list = list(set_lv1)
    for menu_lv1 in set_lv1:
        menu_lv1.sub = []
        for menu_lv2 in set_lv2:
            if menu_lv2.parent == menu_lv1:
                menu_lv1.sub.append(menu_lv2)
    for menu_lv2 in set_lv2:
        menu_lv2.sub = []
        for menu_lv3 in set_lv3:
            if menu_lv3.parent == menu_lv2:
                menu_lv2.sub.append(menu_lv3)
    return menu_list


def get_menu_jstree_json(group_id):
    menu_all = Menu.objects.all()
    menu_owned = Menu.objects.filter(group__id=group_id)
    logger.debug(menu_owned)
    ret_menu = {'data': []}
    for menu in menu_all:
        ret_menu['data'].append({
            'id': 'node' + str(menu.id),
            'parent': 'node' + str(menu.parent.id) if menu.parent else '#',
            'text': menu.name,
            'state': {
                'opened': menu.level < 3,
                'selected': menu.level == 3 and menu in menu_owned,
            },
        })
    logger.debug(json.dumps(ret_menu, indent=2))
    return ret_menu


def log_action(operator, operation, obj, update_fields=[]):
    now = datetime.datetime.now()
    model_name = obj.__class__.__name__
    if operation == 'add':
        info = operator.account + '为' + model_name + '表增加一条id为' + str(obj.id) + '的新记录'
    elif operation == 'delete':
        info = operator.account + '删除' + model_name + '表一条id为' + str(obj.id) + '的记录'
    elif operation == 'update' and update_fields:
        info = operator.account + '更新' + model_name + '表id为' + str(obj.id) + '的记录，更新字段为' + str(update_fields)
    else:
        info = '违法操作记录'
    data = {
        'opt_datetime': now,
        'operator': operator,
        'model': model_name,
        'operation': operation,
        'related_id': obj.id,
        'info': info,
    }
    LogInfo.objects.create(**data)


def get_authorized_banks(bank):
    logger.debug(bank)
    ret = set()
    if bank.level == 3:
        ret = set([bank])
    elif bank.level == 2:
        ret = sorted(set([bank]) | set(bank.bankbranch_set.all()), key=lambda x: x.deptno)
    else:
        children = bank.bankbranch_set.all()
        grand_children = set()
        for child in children:
            grand_children |= set(child.bankbranch_set.all())
        ret = sorted(set([bank]) | set(children) | grand_children, key=lambda x: x.deptno)
    return ret


def generate_orderno(num):
    if num <= 0:
        return []
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    integrity = str(random.randint(0, 99)).zfill(2)  # 本次获取的订单号具有相同的标识，用于寻找同一次交易的不同交易记录
    randcode_list = [random.randint(100000, 999999) for i in range(0, num)]
    orderno_list = ['wx' + now + str(randcode) + integrity for randcode in randcode_list]
    return orderno_list


def parse_time_from_orderno(orderno):
    datetime_str = orderno[2:22]
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S%f')
    return datetime_obj


def transaction_detail_save(trader, opposite, credits, trade_type, info, orderno, coupon=None):
    """存储一条交易明细记录"""
    trade_datetime = parse_time_from_orderno(orderno)
    data = {
        'trader': trader,
        'opposite': opposite,
        'credits': credits,
        'type': trade_type,
        'info': info,
        'coupon': coupon,
        'trade_datetime': trade_datetime,
        'orderno': orderno,
        'need_reconciliation': True if hasattr(trader, 'user') and not trader.is_new else False,
    }
    logger.debug('data: %s, %s', type(data), data)
    return TransactionDetail.objects.create(**data)


def dtime_minus(end, start):
    interval = str(end - start)
    interval = ':'.join(interval.split(':')[:2])
    return interval


def gen_excel(headers, datas=[], filename='未命名报表'):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet(filename)
    for index, value in enumerate(headers):
        sheet.write(0, index, headers[index])
    row = 1
    for data in datas:
        for col in range(0, len(headers)):
            sheet.write(row, col, data[col])
        row += 1
    output = StringIO.StringIO()
    workbook.save(output)
    output.seek(0)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    filename = urlquote(filename + '.xls')
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    response.write(output.getvalue())
    return response


def write_csv(data=[], filename='未命名报表'):
    response = HttpResponse(content_type='text/csv', charset='gbk')
    # response.write(codecs.BOM_UTF8)
    filename = urlquote(filename + '.csv')
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    writer = csv.writer(response)
    for i in range(0, len(data)):
        for j in range(0, len(data[0])):
            data[i][j] = str(data[i][j]).decode().encode('gbk')
    # logger.debug('data: %s, %s', type(data), data)
    writer.writerows(data)
    return response


def calc_page_division(count, req_page):
    num_pages = count / PAGE_SIZE
    left_items = count % PAGE_SIZE
    num_pages = num_pages + 1 if left_items else num_pages
    page = max(1, min(int(req_page), num_pages))
    start_pos = (page - 1) * PAGE_SIZE
    end_pos = start_pos + PAGE_SIZE
    return num_pages, page, start_pos, end_pos
