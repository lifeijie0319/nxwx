# -*- coding: utf-8 -*-
import django
import multiprocessing
import os
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weixin_inner.settings')
django.setup()

from inner_app.logger import logger
from inner_app.models import BankBranch, OnlineNumberTaking
from inner_app.web_client import WsdlClient


def refresh_list_count():
    logger.debug('refresh_list_count start')
    cli = WsdlClient()
    branches = BankBranch.objects.all()
    for branch in branches:
        logger.debug('branch: %s', branch.deptno)
        try:
            result = cli.get_list_count(branch.deptno)
            if result.get('success'):
                branch.waitman = int(result.get('LIST_COUNT'))
                branch.save(update_fields=['waitman'])
        except Exception, e:
            logger.exception(e)
            continue
    logger.debug('refresh_list_count end')


def refresh_num_taking_status():
    logger.debug('refresh_num_taking_status start')
    cli = WsdlClient()
    items = OnlineNumberTaking.objects.filter(status__in=('等待中', '正在处理中'))
    for item in items:
        logger.debug('listno: %s %s', item.listno, item.status)
        try:
            result = cli.get_isvalid(item.branch.deptno, item.listno)
            if result.get('success') and result.get('status') != item.status:
                item.status = result.get('status')
                items.save(update_fields=['status'])
        except Exception, e:
            logger.exception(e)
            continue
    logger.debug('refresh_num_taking_status end')


if __name__ == '__main__':
    p1 = multiprocessing.Process(target=refresh_list_count)
    p2 = multiprocessing.Process(target=refresh_num_taking_status)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
