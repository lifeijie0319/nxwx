# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core.paginator import Paginator
from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..credits_api import dictfetchall
from ..logger import logger
from ..models import Coupon, LotteryRecord, LotterySet, Manager, UserCoupon, BusiType, CouponRule, CommonParam, \
    TransactionDetail, CouponAward
from ..tools import gen_excel, get_menu, log_action


@login_check
def set_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'lottery_awards': LotterySet.objects.all(),
        'award_types': LotterySet.AWARD_TYPES,
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
        'coupons': Coupon.objects.all().filter(term1=None, term2=None),
    }
    return render(request, APP_NAME + '/lottery_award_set.html', context)


@login_check
def rule_set_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'lottery_awards': CouponRule.objects.all(),
        'busi_types': BusiType.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
        'coupons': Coupon.objects.all().filter(),
    }
    return render(request, APP_NAME + '/lottery_award_rule_set.html', context)


@login_check
def rule_add(request):
    data = json.loads(request.body)
    try:
        with transaction.atomic():
            data['coupon'] = Coupon.objects.get(id=data['coupon'])
            data['busitype'] = BusiType.objects.get(id=data['busitype'])
            lottery_award = CouponRule.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', lottery_award)
            context = {'lottery_awards': CouponRule.objects.all(), }
            html = render_to_string(APP_NAME + '/lottery_award_rule_set_table.html', context)
            res = {'success': True, 'msg': u'奖品添加成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'奖品添加失败'}
    return JsonResponse(res)


@login_check
def rule_delete(request):
    post_data = json.loads(request.body)
    lottery_award_id = post_data.get('lottery_award_id')
    try:
        if not CouponRule.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'规则不存在'}
        with transaction.atomic():
            lottery_set = CouponRule.objects.get(id=lottery_award_id)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'delete', lottery_set)
            lottery_set.delete()
            context = {'lottery_awards': CouponRule.objects.all(),
                       'coupons': Coupon.objects.all().filter(term1=None, term2=None), }
            html = render_to_string(APP_NAME + '/lottery_award_rule_set_table.html', context)
            res = {'success': True, 'msg': u'规则删除成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'规则删除失败'}
    return JsonResponse(res)


@login_check
def rule_update(request):
    data = json.loads(request.body)
    lottery_award_id = data.pop('lottery_award_id')
    try:
        if not CouponRule.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'规则不存在'}
        else:
            with transaction.atomic():
                data['coupon'] = Coupon.objects.get(id=data['coupon'])
                data['busitype'] = BusiType.objects.get(id=data['busitype'])
                CouponRule.objects.filter(id=lottery_award_id).update(**data)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                for lottery_set in CouponRule.objects.filter(id=lottery_award_id):
                    log_action(manager, 'update', lottery_set, data.keys())
                context = {'lottery_awards': CouponRule.objects.all(),
                           'coupons': Coupon.objects.all().filter(term1=None, term2=None), }
                html = render_to_string(APP_NAME + '/lottery_award_rule_set_table.html', context)
                res = {'success': True, 'msg': u'规则更新成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'规则更新失败'}
    return JsonResponse(res)


@login_check
def rule2_set_page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'lottery_awards': BusiType.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/lottery_award_rule2_set.html', context)


@login_check
def rule2_add(request):
    data = json.loads(request.body)
    try:
        with transaction.atomic():
            lottery_award = BusiType.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', lottery_award)
            context = {'lottery_awards': BusiType.objects.all(), }
            html = render_to_string(APP_NAME + '/lottery_award_rule2_set_table.html', context)
            res = {'success': True, 'msg': u'奖品添加成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'奖品添加失败'}
    return JsonResponse(res)


@login_check
def rule2_delete(request):
    post_data = json.loads(request.body)
    lottery_award_id = post_data.get('lottery_award_id')
    try:
        if not BusiType.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'奖品不存在'}
        else:
            with transaction.atomic():
                lottery_set = BusiType.objects.get(id=lottery_award_id)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                log_action(manager, 'delete', lottery_set)
                lottery_set.delete()
                context = {'lottery_awards': BusiType.objects.all(), }
                html = render_to_string(APP_NAME + '/lottery_award_rule2_set_table.html', context)
                res = {'success': True, 'msg': u'奖品删除成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'奖品删除失败'}
    return JsonResponse(res)


@login_check
def rule2_update(request):
    data = json.loads(request.body)
    lottery_award_id = data.pop('lottery_award_id')
    try:
        if not BusiType.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'奖品不存在'}
        else:
            with transaction.atomic():
                BusiType.objects.filter(id=lottery_award_id).update(**data)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                for lottery_set in BusiType.objects.filter(id=lottery_award_id):
                    log_action(manager, 'update', lottery_set, data.keys())
                context = {'lottery_awards': BusiType.objects.all(), }
                html = render_to_string(APP_NAME + '/lottery_award_rule2_set_table.html', context)
                res = {'success': True, 'msg': u'奖品更新成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'奖品更新失败'}
    return JsonResponse(res)


# @login_check
# def query(request):
#    setting_name = request.GET.get('sign_name')
#    try:
#        if setting_name:
#            setting =  LotterySet.objects.all().filter(user_name = setting_name)
#        else :
#            setting = LotterySet.objects.all()
#        context = {'datas':setting}
#        html = render_to_string(APP_NAME+ '/lottery_table.html',context)
#        res = {'success':True,'msg':u'查询成功','html':html}
#    except Exception ,e:
#        logger.debug(e)
#        res = {'success':False,'msg':u'查询失败'}
#    return JsonResponse(res)


@login_check
def add(request):
    data = json.loads(request.body)
    try:
        with transaction.atomic():
            lottery_award = LotterySet.objects.create(**data)
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', lottery_award)
            context = {'lottery_awards': LotterySet.objects.all(),
                       'coupons': Coupon.objects.all().filter(term1=None, term2=None), }
            html = render_to_string(APP_NAME + '/lottery_award_set_table.html', context)
            res = {'success': True, 'msg': u'奖品添加成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'奖品添加失败'}
    return JsonResponse(res)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    lottery_award_id = post_data.get('lottery_award_id')
    try:
        if not LotterySet.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'奖品不存在'}
        else:
            with transaction.atomic():
                lottery_set = LotterySet.objects.get(id=lottery_award_id)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                log_action(manager, 'delete', lottery_set)
                lottery_set.delete()
                context = {'lottery_awards': LotterySet.objects.all(),
                           'coupons': Coupon.objects.all().filter(term1=None, term2=None), }
                html = render_to_string(APP_NAME + '/lottery_award_set_table.html', context)
                res = {'success': True, 'msg': u'奖品删除成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'奖品删除失败'}
    return JsonResponse(res)


@login_check
def update(request):
    data = json.loads(request.body)
    lottery_award_id = data.pop('lottery_award_id')
    try:
        if not LotterySet.objects.filter(id=lottery_award_id).exists():
            res = {'success': False, 'msg': u'奖品不存在'}
        else:
            with transaction.atomic():
                LotterySet.objects.filter(id=lottery_award_id).update(**data)
                manager = Manager.objects.get(account=request.session.get('manager_account'))
                for lottery_set in LotterySet.objects.filter(id=lottery_award_id):
                    log_action(manager, 'update', lottery_set, data.keys())
                context = {'lottery_awards': LotterySet.objects.all(),
                           'coupons': Coupon.objects.all().filter(term1=None, term2=None), }
                html = render_to_string(APP_NAME + '/lottery_award_set_table.html', context)
                res = {'success': True, 'msg': u'奖品更新成功', 'html': html}
    except Exception, e:
        logger.debug(e)
        res = {'success': False, 'msg': u'奖品更新失败'}
    return JsonResponse(res)


@login_check
def distribute(request):
    if request.method == 'GET':
        manager_account = request.session.get('manager_account')
        context = {
            # 'lottery_records': LotteryRecord.objects.filter(type='实物'),
            'manager_account': manager_account,
            'cur_inst': CUR_INST,
            'menu': get_menu(manager_account),
        }
        return render(request, APP_NAME + '/lottery_award_distribute.html', context)
    try:
        with transaction.atomic():
            now = datetime.datetime.now()
            logger.debug(request.POST)
            manager_account = request.POST.get('manager_account')
            manager = Manager.objects.get(account=manager_account)
            lottery_record_id = request.POST.get('lottery_record_id')
            lottery_record = LotteryRecord.objects.filter(id=lottery_record_id).update(status='已发放',
                                                                                       sent_datetime=now,
                                                                                       sent_manager=manager)
            for record in LotteryRecord.objects.filter(id=lottery_record_id):
                log_action(manager, 'update', record, ['status', 'sent_datetime', 'sent_manager'])
            res = {'success': True, 'msg': u'奖品发放成功'}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'奖品发放失败'}
    return JsonResponse(res)


@login_check
def distribute_query(request):
    try:
        awards = LotteryRecord.objects.filter(type='实物')
        status = request.GET.get('status')
        if status:
            awards = awards.filter(status=status)
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        if start_date:
            start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            logger.debug(start_datetime)
            awards = awards.filter(created_datetime__gte=start_datetime)
        end_date = request.GET.get('end_date')
        logger.debug('END_DATE: %s', type(end_date))
        if end_date:
            end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            logger.debug(end_datetime)
            awards = awards.filter(created_datetime__lte=end_datetime)

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['用户', '地址', '奖品名称', '获奖时间', '状态']
            datas = []
            for award in awards:
                address = award.user.address
                address = address.get_str() if address else None
                data = [award.user.name, address, award.description,
                        award.created_datetime.isoformat(), award.status]
                datas.append(data)
            return gen_excel(headers, datas, '奖品发货清单')

        if not awards:
            context = {'lottery_records': awards}
        else:
            paginator = Paginator(awards, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_awards = paginator.page(page)
            context = {'lottery_records': p_awards, }
        html = render_to_string(APP_NAME + '/lottery_award_distribute_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def use_page(request):
    if request.method == 'GET':
        manager_account = request.session.get('manager_account')
        context = {
            'manager_account': manager_account,
            'cur_inst': CUR_INST,
            'menu': get_menu(manager_account, )
        }
        return render(request, APP_NAME + '/lottery_use.html', context)


@login_check
def use_query(request):
    try:
        logger.debug('REQUEST: %s', request.GET)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        date_filter = ''
        if start_date:
            date_filter = "AND TRADE_DATETIME >= to_date('{}','yyyy-mm-dd')".format(start_date)
        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')
            date_filter += " AND TRADE_DATETIME < to_date('{}','yyyy-mm-dd')".format(end_date)

        sql = '''
            SELECT td.TRADE_DATE, p.NAME, SUM(CASE "TYPE" WHEN '抽奖' THEN 1 ELSE 0 END) AS NUM,
                SUM(CASE "TYPE" WHEN '抽奖' THEN td.CREDITS ELSE 0 END) AS COST,
                SUM(CASE "TYPE" WHEN '中奖' THEN td.CREDITS ELSE 0 END) AS AWARD
            FROM(
                SELECT CREDITS, "TYPE", to_char(TRADE_DATETIME, 'yyyy-mm-dd') AS TRADE_DATE, TRADER_ID
                FROM INNER_APP_TRANSACTIONDETAIL
                WHERE "TYPE" IN ('抽奖', '中奖') {}
            ) td
            JOIN INNER_APP_PERSON p ON td.TRADER_ID = p.ID
            GROUP BY p.NAME, td.TRADE_DATE
            ORDER BY td.TRADE_DATE;
        '''.format(date_filter)
        with connection.cursor() as c:
            c.execute(sql)
            items = dictfetchall(c)
        logger.debug('ITEMS: %s', items)

        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['抽奖日期', '抽奖客户', '抽奖次数', '花费积分', '抽中积分']
            data = [
                [item['TRADE_DATE'], item['NAME'], item['NUM'], item['COST'], item['AWARD']]
                for item in items]
            return gen_excel(headers, data, '抽奖花费情况表')
        if not items:
            context = {'lottery_records': items}
        else:
            paginator = Paginator(items, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_awards = paginator.page(page)
            context = {'lottery_records': p_awards}
        html = render_to_string(APP_NAME + '/lottery_use_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}

    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def coupon_reward_page(request):
    if request.method == 'GET':
        manager_account = request.session.get('manager_account')
        context = {
            'manager_account': manager_account,
            'cur_inst': CUR_INST,
            'menu': get_menu(manager_account),
        }
        return render(request, APP_NAME + '/coupon_award.html', context)


@login_check
def coupon_reward_query(request):
    try:
        awards = LotteryRecord.objects.filter(type='优惠券')

        status = request.GET.get('status')
        if status:
            awards = awards.filter(status=status)
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        if start_date:
            start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            logger.debug(start_datetime)
            awards = awards.filter(created_datetime__gte=start_datetime)
        end_date = request.GET.get('end_date')
        logger.debug('END_DATE: %s', type(end_date))
        if end_date:
            end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            logger.debug(end_datetime)
            awards = awards.filter(created_datetime__lte=end_datetime)

        items = []
        for i in awards:
            for j in (CouponAward.objects.filter(id=i.user_coupon_id)):
                item = {
                    'user_name': j.user_coupon.user.name,
                    'coupon_status': j.user_coupon.status,
                    'coupon_name': j.user_coupon.coupon.name,
                    'seller_name': '',
                    'use_time': '',
                }
                if j.user_coupon.status == '已使用':
                    item['seller_name'] = j.user_coupon.out_log.opposite.name
                    item['use_time'] = j.user_coupon.out_log.trade_datetime.strftime('%Y-%m-%d %H:%M:%S')
                items.append(item)
        mode = request.GET.get('mode')
        if mode == 'excel':
            headers = ['中奖人', '优惠券状态', '优惠券名称', '核销商户', '核销时间']
            data = []
            for item in items:
                row = [item['user_name'], item['coupon_status'], item['coupon_name'], item['seller_name'],
                       item['use_time']]
                data.append(row)
            return gen_excel(headers, data, '优惠券使用情况表')

        if not items:
            context = {'lottery_records': items}
        else:
            paginator = Paginator(items, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_awards = paginator.page(page)
            context = {'lottery_records': p_awards}
        html = render_to_string(APP_NAME + '/coupon_award_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}

    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)
