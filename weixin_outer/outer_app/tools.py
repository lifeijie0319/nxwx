# -*- coding: utf-8 -*-
"""通用工具模块

该模块用于实现一些通用的工具函数
"""
#tools.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import base64
import datetime
import json
import os
import uuid

from binascii import b2a_hex, a2b_hex
from Crypto.Cipher import AES
from django.conf import settings
from django.core.serializers import serialize
from django.db import models
from django.db.models.query import QuerySet

from config import APPID, APP_NAME, BASE_URL


#命名规则转换
#帕斯卡：pascal
#驼峰：camel
#下划线: underline
#def naming_rule_trans(str_for_trans, from_rule='camel', to_rule='underline'):
#    if from_rule == 'camel':
#        if to_rule == 'underline':
#            underline_format = ''  
#            if isinstance(str_for_trans, str):  
#                for _s_ in str_for_trans:  
#                    underline_format += _s_ if _s_.islower() else '_'+_s_.lower()  
#            return underline_format
#    elif from_rule == 'underline':
#        if to_rule == 'camel':
#            camel_format = ''  
#            if isinstance(str_for_trans, str):  
#                for _s_ in str_for_trans.split('_'):  
#                    camel_format += _s_.capitalize()  
#            return camel_format
def gen_token():
    token = str(uuid.uuid4()).replace('-', '')
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    token = now + '-' + token
    return token


def to_json(obj):
    if isinstance(obj,QuerySet):
        return json.loads(serialize("json", obj))
    elif isinstance(obj,models.Model):
        return json.loads(serialize("json", [obj])[1:-1])


def get_and_delete(obj, name):
    ret = obj.get(name)
    if ret:
        del obj[name]
    return ret


class AESEncryption():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
     
    #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)
     
    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


def get_oauth_url(redirect_uri, state='1'):
    return 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + APPID + '&redirect_uri=' + BASE_URL + redirect_uri + '&response_type=code&scope=snsapi_base&state=' + state + '#wechat_redirect'


def get_img_path(photo_id, photo_type):
    print 'TYPE: ', photo_type, 'ID: ', photo_id
    #photo_type可能的值: shop, user
    photo_id = str(photo_id)
    img_path = '/static/' + APP_NAME + '/images/' + photo_type + '_default.jpg'
    dest_path = '/' + APP_NAME + '/media/' + photo_type + '/' + photo_id + '.jpg'
    print 'DEST_PATH:', dest_path
    print 'BASE_DIR:', settings.BASE_DIR
    print 'FILE EXIST: ', settings.BASE_DIR + dest_path
    if os.path.exists(settings.BASE_DIR + dest_path):
        img_path = dest_path + '?t=' + datetime.datetime.now().strftime('%Y%m%d%H%m%s')
    #print 'FILE EXIST: ', os.path.exists(dest_path)
    #if os.path.exists(dest_path):
    #    with open(dest_path, 'rb') as f:
    #        img = base64.b64encode(f.read())
    #    img_path = 'data:image/jpeg;base64,' + img
    return img_path


def get_img(photo_id, photo_type):
    photo_id = str(photo_id)
    img_path = APP_NAME + '/media/' + photo_type + '/' + photo_id + '.jpg'
    img = None
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            img = base64.b64encode(f.read())
    return img
