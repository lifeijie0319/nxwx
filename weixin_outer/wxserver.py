#-*- coding:utf-8 -*-

#外部使用Django ORM
import os
import sys
from django.core.wsgi import get_wsgi_application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","weixin_outer.settings")
application = get_wsgi_application()

import json
#import multiprocessing
import requests
import time

from django.urls import reverse
from outer_app.config import ACCESS_TOKEN_KEY, APP_NAME, JSAPI_TICKET_KEY
from outer_app.global_var import logger, redis_conn
from outer_app.tools import get_oauth_url
from outer_app.wx import weixin_access_token, Menu


MENU={
    'button': [
        {
            'name': u'幸福快贷',
            'sub_button':[
                {
                    'type': 'view',
                    'name': u'幸福快贷申请',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_loan_page'))
                },
                {
                    'type': 'view',
                    'name': u'快抵贷申请',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_kdd_index'))
                },
            ],
        },
        {
            'name': u'预约服务',
            'sub_button':[
                {
                    'type': 'view',
                    'name': u'开户办卡预约',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_open_account_page'))
                },
                {
                    'type': 'view',
                    'name': u'ETC预约',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_etc_page'))
                },
                {
                    'type': 'view',
                    'name': u'大额取现预约',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_withdrawal_page'))
                },
                {
                    'type': 'view',
                    'name': u'对公开户预约',
                    'url': get_oauth_url(reverse(APP_NAME+':reservation_dgkh_page'))
                },
                {
                    'type': 'view',
                    'name': u'预约进度查询',
                    'url': get_oauth_url(reverse(APP_NAME+':staticfile', kwargs={'name': 'reservation_status'}))
                },
            ]
        },
        {
            'name': u'我的',
            'sub_button':[
                {
                    'type': 'view',
                    'name': u'我的信息',
                    'url': get_oauth_url(reverse(APP_NAME + ':user_info_page'))
                },
                {
                    'type': 'view',
                    'name': u'我的积分',
                    'url': get_oauth_url(reverse(APP_NAME + ':credits_page'))
                },
                {
                    'type': 'view',
                    'name': u'我是商家',
                    'url': get_oauth_url(reverse(APP_NAME + ':seller_page'))
                },
            ]
        },
    ]
}


def update_access_token():
    logger.debug('accessing the access_token')
    access_token, expires_in = weixin_access_token()
    if access_token:
        logger.debug('%s, %s', access_token, expires_in)
        url='https://api.weixin.qq.com/cgi-bin/ticket/getticket'
        params={'access_token': access_token, 'type': 'jsapi'}
        res=requests.get(url, params, verify=False)
        redis_conn.set(JSAPI_TICKET_KEY, res.json().get('ticket'))
    else:
        count = 0
        while not access_token and count < 3:
            time.sleep(60)
            access_token, expires_in = weixin_access_token()
            logger.debug('这是第%d次重新获取access_token' %(count + 1))
            count += 1
        if count == 3:
            logger.debug("多次获取access_token失败，请排查错误")
            exit()
    redis_conn.set(ACCESS_TOKEN_KEY, access_token)


def worker():
    logger.debug(json.dumps(MENU, indent=2))
    #name = multiprocessing.current_process().name
    #logger.debug('%s, Starting', name)
    update_access_token()
    access_token = redis_conn.get(ACCESS_TOKEN_KEY)
    menu = Menu()
    menu_json = json.dumps(MENU, ensure_ascii=False)
    menu.delete(access_token)
    menu.create(menu_json, access_token)
    while True:
        time.sleep(7200)
        update_access_token()


if __name__ == '__main__':
    print json.dumps(MENU, indent=2)
    #worker = multiprocessing.Process(name='worker', target=worker)
    #worker.start()
    worker()
