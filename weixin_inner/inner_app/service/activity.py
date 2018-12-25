# -*- coding: utf-8 -*-
import json

from django.db import transaction

from ..logger import logger
from ..models import Activity, ActivityExt, ActivityStatistics, RepetitionExclude


def single_activity(item):
    context = {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'typ': item.typ,
        'key': item.key,
        'status': item.status
    }
    activity_exts = ActivityExt.objects.filter(activity=item) \
        .filter(name__in=ActivityExt.MAP[item.typ])
    context['ext_info'] = {ext.name: ext.value for ext in activity_exts}
    return context


def index(activity_id):
    item = Activity.objects.get(id=activity_id)
    return single_activity(item)


def index_check(activity_id, openid):
    activity = Activity.objects.get(id=activity_id)
    item = ActivityStatistics.objects.filter(activity=activity, openid=openid)
    if len(item) > 1:
        msg = '服务器错误，您在活动' + activity.name + '的记录数多于1条，请联系管理员'
        return {'success': False, 'msg': msg}
    elif len(item) == 1:
        item = item.first()
        data = {
            'col1': item.col1,
            'col2': item.col2,
            'col3': item.col3,
        }
        if activity.typ == '盖楼':
            if item.col5:
                if item.col1:
                    msg = '您已经为该活动中奖填写个人信息，继续填写将更新之前的信息，请确认'
                    return {'success': True, 'msg': msg, 'data': data, 'num': 1}
                else:
                    return {'success': True, 'num': 1}
            else:
                msg = '您尚未中奖，无须填写个人信息，请确认'
                return {'success': True, 'msg': msg, 'data': data, 'num': 1}
        elif activity.typ == '信息登记':
            msg = '您在活动' + activity.name + '已有记录，继续填写将更新之前的信息，请确认'
            return {'success': True, 'msg': msg, 'data': data, 'num': 1}
        else:
            raise Exception('未知的活动')
    else:
        if activity.typ == '信息登记':
            return {'success': True, 'num': 0}
        elif activity.typ == '盖楼':
            msg = '您在盖楼活动' + activity.name + '未有记录，请确定是否参与'
            return {'success': False, 'msg': msg}


def config(key=None):
    item = Activity.objects.filter(key=key, status='使用中')
    if len(item) == 1:
        item = item.first()
        context = single_activity(item)
        context['matched'] = True
    elif len(item) == 0:
        items = Activity.objects.filter(status='使用中')
        context = {
            'matched': False,
            'items': [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'typ': item.typ,
                'key': item.key,
                'status': item.status
            } for item in items],
        }
    else:
        raise Exception('键值为' + key + '的活动有两个，请检查')
    return context


def submit(openid, data):
    logger.debug('ACTIVITY SUBMIT: OPENID:{}, {}'.format(openid, data))
    data = json.loads(data)
    activity_id = data.pop('activity_id')
    check_rtn = index_check(activity_id, openid)
    if not check_rtn['success']:
        return check_rtn
    activity = Activity.objects.get(id=activity_id)
    with transaction.atomic():
        req_token = data.pop('req_token')
        RepetitionExclude.objects.create(req_token=req_token)
        if activity.typ == '盖楼':
            ActivityStatistics.objects.filter(activity=activity, openid=openid)\
                .update(**data)
        elif activity.typ == '信息登记':
            if int(check_rtn['num']) == 0:
                data['openid'] = openid
                data['activity'] = activity
                ActivityStatistics.objects.create(**data)
            else:
                ActivityStatistics.objects.filter(activity=activity, openid=openid)\
                    .update(**data)
    return {'success': True}


# 盖楼活动增加中奖纪录
def post_award_add(openid, activity_id, level, award=''):
    activity = Activity.objects.get(id=activity_id)
    item = ActivityStatistics.objects.filter(activity=activity, openid=openid)
    if len(item) > 1:
        msg = '服务器错误，您在活动' + activity.name + '的中奖记录数多于1条，请联系管理员'
        return {'success': False, 'msg': msg}
    elif len(item) == 1:
        msg = '您已经参加过' + activity.name + '活动，无法重复参加该活动'
        return {'success': False, 'msg': msg}
    else:
        data = {
            'openid': openid,
            'activity': Activity.objects.get(id=activity_id),
            'col4': level,
            'col5': award,
        }
        ActivityStatistics.objects.create(**data)
        return {'success': True}
