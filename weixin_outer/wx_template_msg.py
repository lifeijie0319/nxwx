#-*- coding:utf-8 -*-
import base64
import datetime
import hashlib
import json
import os
import random
import requests
import sys
import time

from django.core.wsgi import get_wsgi_application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","weixin_outer.settings")
application = get_wsgi_application()

from outer_app.global_var import logger, redis_conn
from outer_app.wx import send_template_msg


if __name__ == '__main__':
    while True:
        try:
            data = json.loads(redis_conn.brpop('QUEUE:WX:TEMPLATE_MSG')[1])
            send_template_msg(**data)
        except Exception, e:
            logger.exception(e)
            continue
