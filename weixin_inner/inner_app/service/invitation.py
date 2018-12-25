# -*- coding: utf-8 -*-
import datetime

from django.db import connection
from django.db.models import Count

from ..credits_api import dictfetchall
from ..logger import logger
from ..models import CommonParam, Invitation, User
from ..tools import encrypt_name


def get_year_rank(user_id, year):
    logger.debug('user_id, year: %s, %s', user_id, year)
    ranking_sql = '''
        SELECT INVITER_ID, INVITATION_NUM, RANK FROM(
            SELECT INVITER_ID, COUNT(*) INVITATION_NUM, RANK() OVER(ORDER BY COUNT(*) DESC) RANK
            FROM NANXUN.INNER_APP_INVITATION
            WHERE TYPE = '注册邀请'
                AND TO_CHAR(CREATED_DATETIME, 'YYYY') = %s
            GROUP BY INVITER_ID
        )WHERE INVITER_ID = %s;
    '''
    res = None
    with connection.cursor() as c:
        c.execute(ranking_sql, (year, user_id))
        res = dictfetchall(c)
    logger.debug('RANK: %s', res)
    if res:
        return res[0].get('RANK')
    else:
        return -1


def get_month_rank(user_id, year_month):
    logger.debug('year_month %s', year_month)
    ranking_sql = '''
        SELECT INVITER_ID, INVITATION_NUM, RANK FROM(
            SELECT INVITER_ID, COUNT(*) INVITATION_NUM, RANK() OVER(ORDER BY COUNT(*) DESC) RANK
            FROM NANXUN.INNER_APP_INVITATION
            WHERE TYPE = '注册邀请'
                AND TO_CHAR(CREATED_DATETIME, 'YYYYMM') = %s
            GROUP BY INVITER_ID
        )WHERE INVITER_ID = %s;
    '''
    res = None
    with connection.cursor() as c:
        c.execute(ranking_sql, (year_month, user_id))
        res = dictfetchall(c)
    if res:
        return res[0].get('RANK')
    else:
        return -1


def register_page(openid):
    user = User.objects.get(openid=openid)
    invitations = Invitation.objects.filter(inviter=user).filter(type='注册邀请')
    all_num = invitations.count()
    gift_credits = int(CommonParam.objects.get(name='邀请注册赠送积分').value)
    credits = all_num * gift_credits
    today = datetime.date.today()
    invitations = invitations.filter(created_datetime__year=today.year)
    year_rank = get_year_rank(user.id, str(today.year))
    logger.debug(year_rank)
    month_rank = get_month_rank(user.id, today.strftime('%Y%m'))
    logger.debug(month_rank)
    return {'num': all_num, 'credits': credits, 'gift_credits': gift_credits, 'year_rank': year_rank, 'month_rank': month_rank}


def ranking_list(year=None, month=None):
    logger.debug('%s, %s', year, month)
    invitations = Invitation.objects.filter(type='注册邀请')
    if year:
        invitations = invitations.filter(created_datetime__year=year)
    if month:
        invitations = invitations.filter(created_datetime__month=month)
    logger.debug(invitations)
    ranking_list = invitations.values('inviter', 'inviter__name')\
        .annotate(invitation_num=Count('*')).order_by('-invitation_num')[0:20]
    #logger.debug(ranking_list)
    #ranking_list = list(ranking_list)
    #ranking_list.extend([{
    #    'inviter__name': u'张三',
    #    'invitation_num': 1,
    #}, {
    #    'inviter__name': u'李四',
    #    'invitation_num': 1,
    #}, {
    #    'inviter__name': u'王二宝',
    #    'invitation_num': 1,
    #}])
    ranking_list = [{
        'name': encrypt_name(person['inviter__name']),
        'invitation_num': person['invitation_num'],
    } for person in ranking_list]
    logger.debug(ranking_list)
    return {'success': True, 'ranking_list': ranking_list}
