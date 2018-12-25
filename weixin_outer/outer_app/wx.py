#-*- coding:utf-8 -*-
"""微信模块

该模块用于处理一些和微信服务器的交互
"""
#wx.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import hashlib
import json
import multiprocessing
import random
import redis
import requests
import string
import time
import urllib

from datetime import datetime
from django.http import HttpResponse, JsonResponse

from .config import APPID, APPSECRET, JSAPI_TICKET_KEY, TOKEN, ACCESS_TOKEN_KEY
from .global_var import logger, redis_conn


def weixin_check(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')
    l=sorted([timestamp, nonce, TOKEN])
    s=hashlib.sha1()
    for t in l:
        s.update(t)
    dig=s.digest().encode('hex')
    if signature==dig:
        return HttpResponse(echostr)
    else:
        logger.debug(u'check signature fail: %s vs %s' %(signature, dig))
        return HttpResponse('')


def weixin_access_token():
    url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPID, APPSECRET)
    res=requests.get(url, verify=False)
    if res:
        res=res.json()
        return res.get('access_token'), res.get('expires_in')
    else:
        return None, None


def check_user_subscribed(openid):
    access_token = redis_conn.get(ACCESS_TOKEN_KEY)
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)
    res=requests.get(url, verify=False).json()
    #logger.debug(res)
    if res.get('errcode'):
        return res.get('errmsg')
    else:
        return res.get('subscribe')


def send_template_msg(openid, template_id, url, content):
    access_token = redis_conn.get(ACCESS_TOKEN_KEY)
    logger.debug('OPENID: %s, %s', openid, type(openid))
    post_data = {
        "touser": openid,
        "template_id": template_id,
        "url": url,
        "data": content,
    }
    post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % access_token
    post_data = json.dumps(post_data).encode('utf-8')
    logger.debug('POST: %s', post_data)
    resp = urllib.urlopen(url=post_url, data=post_data)
    logger.debug('RESP: %s', resp.read())


def oauth_get_openid(code, state='1'):
    url='https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(APPID, APPSECRET, code)
    res=requests.get(url, verify=False)
    res=res.json()
    logger.info('OAUTH_GET_OPENID RES: %s', res)
    if res:
        openid = res.get('openid')
        return openid
    else:
        return None


def sign(jsapi_ticket, url):
    """jssdk签名函数"""
    logger.debug('ENTER SIGN')
    nonceStr=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
    timestamp=int(time.time())
    ret = {
        'nonceStr':nonceStr,
        'jsapi_ticket':jsapi_ticket,
        'timestamp':timestamp,
        'url':url
    }
    secret_str = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
    ret['signature'] = hashlib.sha1(secret_str).hexdigest()
    return ret


def weixin_jssdk(url):
    logger.debug('START: %s', datetime.now())
    jsapi_ticket = redis_conn.get(JSAPI_TICKET_KEY)
    logger.debug('TIMETAG1: %s', datetime.now())
    if jsapi_ticket == None:
        return {'success': False, 'msg': 'failed to get jsapi_ticket'}
    ret = sign(jsapi_ticket, url)
    logger.debug('TIMETAG2: %s', datetime.now())
    logger.debug('RETURN: %s', ret)
    if ret == None:
        return {'success': False, 'msg': 'failed to sign'}
    logger.debug('END: %s', datetime.now())
    return {'success': True, 'config': ret}


def get_tmp_media(mediaid):
    access_token = redis_conn.get(ACCESS_TOKEN_KEY)
    logger.debug(mediaid)
    logger.debug(access_token)
    url = 'https://file.api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s' %(access_token, mediaid)
    res = requests.get(url, verify=False)
    logger.debug(res.headers)
    return res


class Menu(object):
    def __init__(self):
        pass

    def create(self, post_data, access_token):
        post_url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % access_token
        if isinstance(post_data, unicode):
            post_data = post_data.encode('utf-8')
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def query(self, access_token):
        post_url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s" % access_token
        urlResp = urllib.urlopen(url=post_url)
        logger.debug(json.dumps(json.loads(urlResp.read()), indent=2))

    def delete(self, access_token):
        post_url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" % access_token
        urlResp = urllib.urlopen(url=post_url)
        logger.debug(urlResp.read())


class ConditionalWXMenu(object):
    def __init__(self):
        pass

    def create(self, post_data, access_token):
        post_url = "https://api.weixin.qq.com/cgi-bin/menu/addconditional?access_token=%s" % access_token
        if isinstance(post_data, unicode):
            post_data = post_data.encode('utf-8')
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def delete(self, menuid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/menu/delconditional?access_token=%s' % access_token
        logger.debug('%s %s', type(tagid), tagid)
        post_data = {
            'menuid': menuid,
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())


class WXUser(object):
    def __init__(self):
        pass

    def tag(self, openid_list, tagid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/members/batchtagging?access_token=%s' % access_token
        logger.debug('%s %s', type(tagid), tagid)
        post_data = {
            'openid_list': openid_list,
            'tagid': tagid,
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def untag(self, openid_list, tagid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/members/batchuntagging?access_token=%s' % access_token
        post_data = {
            'openid_list': openid_list,
            'tagid': tagid,
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def get_tagids(self, openid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/getidlist?access_token=%s' % access_token
        post_data = {
            'openid': openid,
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())


class WXTag(object):
    def __init__(self):
        pass

    def create(self, tagname, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/create?access_token=%s' % access_token
        post_data = {
            'tag': {
                'name': tagname,
            }
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def query(self, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/get?access_token=%s' % access_token
        urlResp = urllib.urlopen(url=post_url)
        logger.debug(urlResp.read())

    def delete(self, tagid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/delete?access_token=%s' % access_token
        post_data = {
            'tag': {
                'id': tagid,
            }
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def update(self, tagid, tagname, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/tags/update?access_token=%s' % access_token
        post_data = {
            'tag': {
                'id': tagid,
                'name': tagname,
            }
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())

    def get_menbers(self, tagid, first_openid, access_token):
        post_url = 'https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token=%s' % access_token
        post_data = {
            'tagid': tagid,
            'next_openid': first_openid,
        }
        post_data = json.dumps(post_data, ensure_ascii=False)
        urlResp = urllib.urlopen(url=post_url, data=post_data)
        logger.debug(urlResp.read())
