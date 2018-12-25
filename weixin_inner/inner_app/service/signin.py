# coding:utf-8
import datetime

from django.db import transaction

from .common import add_trade_detail, credits_usable, query_credits,\
transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import CommonParam, RepetitionExclude, SignData, SignRecord, SignRule, User
from ..tools import generate_orderno


def sign_page(openid):
    rules = SignRule.objects.all().order_by('day')
    ret_rules = [{'day': rule.day, 'credits': rule.credits} for rule in rules]
    return {'credits': query_credits(openid, 'user'), 'sign_rules': ret_rules}


# 获取今日是否签到，总签到次数，总签到积分
def get_signin(openid):
    now = datetime.datetime.now()
    this_month = int(now.strftime('%m'))
    today_index = int(now.strftime('%d'))
    signed_dates = SignData.objects.filter(user__openid=openid).filter(datetime__month=this_month)
    signed_dates_index = [int(signed_date.datetime.strftime('%d')) - 1 for signed_date in signed_dates]
    all_gift_credits = sum([signed_date.credits for signed_date in signed_dates])
    today_is_signed = 'true' if (today_index - 1) in signed_dates_index else 'false'
    return {'signed_dates': signed_dates_index, 'credits': all_gift_credits, 'today_is_signed': today_is_signed}


# 点击签到按钮后，执行签到操作
def signin(openid, req_token):
    now = datetime.datetime.now()
    today = datetime.date.today()
    next_day = today + datetime.timedelta(days=1)
    today_index = int(today.strftime('%d'))
    this_month = today.strftime('%m')
    user = User.objects.get(openid=openid)
    today_is_signed = SignData.objects.filter(user=user).filter(datetime__range=(today, next_day)).exists()
    if user.is_new:
        return {'success': False, 'msg': u'您尚未绑定，无法签到, 请到个人信息页面绑定'}
    if today_is_signed:
        return {'success': False, 'msg': u'今天已经签过到,一天只能签到一次'}
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    with transaction.atomic():
        RepetitionExclude.objects.create(req_token=req_token)
        if SignRecord.objects.filter(user=user).exists():
            record = SignRecord.objects.get(user=user)
            if record.month != int(this_month):
                record.month = int(this_month)
                record.num = 0
            record.num += 1
            record.save()
        else:
            SignRecord.objects.create(user=user, month=int(this_month), num=1)
        added_credits = calcu_gift_credits(openid)
        SignData.objects.create(user=user, datetime=now, credits=added_credits)
        user.credits += added_credits
        user.save()
        orderno = generate_orderno(1)[0]
        transaction_detail_save(user, None, added_credits, '签到', '签到获得积分', orderno)
    with transaction.atomic(using='old_credits'):
        update_or_insert_credits(user.idcardno, added_credits)
        add_trade_detail(u'签到', user.idcardno, user.name, added_credits, '+',\
            query_credits(openid, 'user'), orderno)
    context = {
        'success': True,
        'today_index': today_index,
        'added_credits': added_credits,
        'new_credits': query_credits(openid, 'user'),
    }
    return context


def calcu_gift_credits(openid):
    base_gift_credits = int(CommonParam.objects.get(name=u'签到基础赠送积分').value)
    rules = SignRule.objects.all()
    signed_days = SignRecord.objects.get(user__openid=openid).num
    ex_gift_credits = 0
    for rule in rules:
        if rule.day == signed_days:
            ex_gift_credits = rule.credits
            break
    return base_gift_credits + ex_gift_credits
