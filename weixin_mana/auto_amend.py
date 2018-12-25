#-*- coding:utf-8 -*-
#外部使用Django ORM
import datetime
import logging
import os
import sys
import time

from collections import OrderedDict
from django.db import connections, transaction
from django.core.wsgi import get_wsgi_application
sys.path.append(os.environ['WXBANK_HOME'] + '/weixin_mana')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_mana.settings")
application = get_wsgi_application()

from mana_app.credits_api import insert_trade_detail, query_sync_status, query_trade_detail2
from mana_app.models import BankBranch, Group, Manager, Term, TransactionDetail
from mana_app.views.common import query_credits, update_or_insert_credits


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_fh = logging.handlers.TimedRotatingFileHandler(os.environ['WXBANK_HOME'] + '/log/django/auto_amend.log', when='midnight', backupCount=30)
logger.addHandler(log_fh)


def amend(trade_detail):
    if query_sync_status('I_SC_KHJFYEB'):
        with transaction.atomic(using='old_credits'):
            trader = trade_detail.trader.user
            update_or_insert_credits(trader.idcardno, trade_detail.credits)
            new_credits = query_credits(trader.idcardno)
            now = datetime.datetime.now()
            info = OrderedDict({
                'DATE_ID': now.strftime('%Y%m%d'),
                'TRADE_TYPE': trade_detail.type,
                'CUST_NO': '101' + trader.idcardno,
                'CUST_NAME': trader.name,
                'TRADE_TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
                'TRADE_SCORE': 100 * abs(trade_detail.credits),
                'TRADE_DIREC': '+' if trade_detail.credits >= 0 else '-',
                'NEW_CREDITS': 100 * new_credits,
                'GOODS_NAME': trade_detail.coupon.name if trade_detail.coupon else None,
                'GOODS_COST': trade_detail.coupon.credits if trade_detail.coupon else None,
                'TRADE_MARK': '轮询补录',
                'TRADE_COMM1': trade_detail.orderno,
            })
            #logger.debug(info)
            insert_trade_detail(**info)


def reconciliation(start, end):
    logger.debug('START %s, END %s', start, end)
    transaction_details = TransactionDetail.objects.filter(need_reconciliation=True)\
        .filter(trade_datetime__gte=start).filter(trade_datetime__lt=end)
    trade_details = query_trade_detail2(start, end)
    logger.debug('transaction_details %s', len(transaction_details))
    logger.debug('trade_details %s', len(trade_details))
    transaction_details_set = set([detail.orderno for detail in transaction_details])
    trade_details_set = set([detail.get('TRADE_COMM1') for detail in trade_details])
    diff_set = transaction_details_set - trade_details_set
    if not diff_set:
        return {'success': True}
    else:
        diff_transaction_details = TransactionDetail.objects.filter(orderno__in=diff_set)
        for detail in diff_transaction_details:
            try:
                amend(detail)
            except Exception, e:
                logger.debug('Exception: %s', e)
                continue
        return {'success': False, 'diff_set': diff_set}


if __name__ == '__main__':
    while 1:
        now = datetime.datetime.now()
        logger.debug('now: %s', now)
        start = now - datetime.timedelta(seconds=90)
        end = now - datetime.timedelta(seconds=30)
        logger.debug(reconciliation(start, end))
        time.sleep(30)
