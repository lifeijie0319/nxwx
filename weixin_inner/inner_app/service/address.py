# -*- coding: utf-8 -*-
"""地址应用模块

该模块用于从数据库取出地址树并作为数据源提供给前台。
"""
#address.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

import json

from django.db import transaction

from ..logger import logger
from ..models import Address, Shop, User, Region


def get_region_tree(start_node_code=u'330000000000', end_level=u'village'):
    """从数据库取出一棵地址树。

    通过递归实现，最终返回字典。
    """
    #logger.debug(u'CODE: %s', code)
    #logger.debug('END_LEVEL: %s', end_level)
    parent = Region.objects.get(code=start_node_code)
    parent_node = {u'name': parent.name, u'code': parent.code}
    if parent.level != end_level and parent.name != u'市辖区':
        parent_node[u'sub'] = []
        children = Region.objects.filter(parent=start_node_code)
        for child in children:
            child_node = get_region_tree(start_node_code=child.code, end_level=end_level)
            parent_node[u'sub'].append(child_node)
    return parent_node


def get_region_json(start_node_name, end_level):
    start_node = Region.objects.filter(name=start_node_name)
    if start_node.exists():
        start_node_code = start_node[0].code
        logger.debug('START_NODE: %s', start_node_code)
    else:
        start_node_code = '330102000000'
    tree = get_region_tree(start_node_code=start_node_code, end_level=end_level)
    #写json文件
    #data = json.dumps(tree, sort_keys=True, indent=4, ensure_ascii=False)
    #logger.debug(type(data))
    #f = codecs.open('./nanxun/region.json', 'w', 'utf-8')
    #f.write(data)
    #f.close()
    #如果使用下面的方法，可以存入文件，但是是中文是unicode的形式。
    #with open(u'region.json', u'w') as f:
    #    f.write(data)
    return tree


def modify_page(from_page, openid, start_node_code, end_level):
    if from_page == 'my_info':
        address = User.objects.get(openid=openid).address
    else:
        address = Shop.objects.get(seller__openid=openid).address
    logger.debug('ADDRESS: %s', address)
    address = address.get_str() if address else u'未设置'
    tree = get_region_tree(start_node_code, end_level)
    region_tree = json.dumps(tree, ensure_ascii=False, encoding='utf-8')
    return {u'region_tree': region_tree, 'current_address': address}


@transaction.atomic
def modify(from_page, openid, id, province, city, county, town, village, address_detail):
    if from_page == 'shop':
        old_address_id = Shop.objects.get(id=id).address.id
        logger.debug(old_address_id)
        old_address = Address.objects.filter(id=old_address_id)
        #logger.debug('old_address:', old_address)
        logger.debug('UPDATED ROW: %s', Address.objects.filter(id=old_address_id).update(province=province, city=city, county=county, town=town, village=village, detail=address_detail))
        #old_address.save(Province=province)
    else:
        user = User.objects.get(openid=openid)
        if user.address:
            Address.objects.filter(id=user.address.id).update(province=province, city=city, county=county, town=town, village=village, detail=address_detail)
        else:
            new_address = Address.objects.create(province=province, city=city, county=county, town=town, village=village, detail=address_detail)
            user.address = new_address
            user.save()
    return {'success': True}
