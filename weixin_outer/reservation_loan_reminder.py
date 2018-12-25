#-*- coding:utf-8 -*-
import os
import sys

from django.core.wsgi import get_wsgi_application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","weixin_outer.settings")
application = get_wsgi_application()

from outer_app.global_var import logger, redis_conn
from outer_app.socket_client import send2serv
from outer_app.template_msg import loan_overtime_reminder


def call_overtime_check(busi_type):
    context = send2serv({'path':'reservation_inter.overtime_check','kargs':{'busi_type': busi_type}})
    reminder_list = context.get('reminder_list')
    for reminder in reminder_list:
        try:
            loan_overtime_reminder(reminder)
        except Exception, e:
            logger.exception(e)
            continue


if __name__ == '__main__':
    call_overtime_check('贷款预约')
    call_overtime_check('快抵贷')
