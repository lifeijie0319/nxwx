#-*- coding:utf-8 -*-
"""地址获取模块

该模块用于从国家统计局获取行政区划数据，存入数据库
"""
#load_region.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

#外部使用Django ORM
import os
import sys
from django.core.wsgi import get_wsgi_application
sys.path.append('/home/nanxun/weixin_mana')
os.environ.setdefault("DJANGO_SETTINGS_MODULE","weixin_mana.settings")
application = get_wsgi_application()

import codecs
import json
import requests

from lxml import etree
from pyquery import PyQuery as pq

from inner_app.models import Region
from logger import logger


def load_region_node(parentNode, url):
    """递归获取地址数据

    函数依据国家统计局地址规划网站的html结构，顺着当前html和链接
    逐步深入，递归加入子节点到all_nodes列表中。
    """

    logger.debug('URL: %s', url)
    global all_nodes
    page = requests.get(url, headers={'user-agent': 'pyquery'})
    #logger.debug(type(page.status_code))
    if page.status_code != 200:
        return None
    #encoding = page.apparent_encoding
    decodedPage = page.content.decode('gbk')
    doc = pq(decodedPage)
    table = doc('table:last')
    table.make_links_absolute(base_url=url)
    level = table.attr('class')[:-5]
    logger.debug('LEVEL: %s', level)
    trs = table('tr')
    for tr in trs.items():
        if tr.hasClass(level + 'tr'):
            regionNode = parse_tr(level, tr)
            storedNode = {u'code': regionNode.get('code'), u'name': regionNode.get('name'), u'level': level, u'parent': parentNode.get('code')}
            if regionNode.get('url'):
                load_region_node(storedNode, regionNode.get('url'))
            all_nodes.append(Region(**storedNode))


def parse_tr(level, tr):
    """解析网站中的单个节点"""

    code = tr('td:first').text()
    name = tr('td:last').text()
    #logger.debug(type(name))
    if level == u'county' and name == u'市辖区' or level == u'village':
        url = None
    else:
        url = tr('td:first a').attr('href')
    node = {u'code': code, u'name': name, u'url': url}
    return node


if __name__ == '__main__':
    startNode = {u'code': u'330000000000', u'name': u'浙江省', u'level': u'province', u'parent': u''}
    startNode1 = {u'code': u'330100000000', u'name': u'杭州市', u'level': u'city', u'parent': u'330000000000'}
    startNode2 = {u'code': u'330500000000', u'name': u'湖州市', u'level': u'city', u'parent': u'330000000000'}
    all_nodes = [Region(**startNode), Region(**startNode1), Region(**startNode2)]
    load_region_node(startNode1, u'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2015/33/3301.html')
    load_region_node(startNode2, u'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2015/33/3305.html')
    Region.objects.bulk_create(all_nodes)
    #写入json文件
    #logger.debug(type(all_nodes))
    #data = json.dumps(all_nodes, sort_keys=True, indent=4, ensure_ascii=False)
    #f = codecs.open('region.json', 'w', 'utf-8')
    #f.write(data)
    #f.close()
