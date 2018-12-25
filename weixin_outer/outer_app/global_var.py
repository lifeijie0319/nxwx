#-*- coding:utf-8 -*-
import json
import logging
import redis

from config import REDIS, AES_KEY
from tools import AESEncryption


redis_conn = redis.StrictRedis(host=REDIS.get('HOST'), port=REDIS.get('PORT'), db=0)
cryptor = AESEncryption(AES_KEY)
logger = logging.getLogger('developer')
