# -*- coding: utf-8 -*-
import datetime
import json
import os
import random

from django.core.serializers import serialize
from django.db import models
from django.db.models.query import QuerySet
from logger import logger


def to_json(obj):
    if isinstance(obj,QuerySet):
        return json.loads(serialize("json", obj))
    elif isinstance(obj,models.Model):
        return json.loads(serialize("json", [obj])[1:-1])


def generate_orderno(num):
    if num <= 0:
        return []
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    integrity = str(new_randint(0, 99)).zfill(2)#本次获取的订单号具有相同的标识，用于寻找同一次交易的不同交易记录
    randcode_list = new_randint(100000, 999999, num)
    if num == 1:
        randcode_list = [randcode_list]
    orderno_list = ['wx' + now + str(randcode) + integrity for randcode in randcode_list]
    return orderno_list


def parse_time_from_orderno(orderno):
    datetime_str = orderno[2:22]
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S%f')
    return datetime_obj


def weight_choice(weight):
    """
    :param weight: list对应的权重序列
    :return:选取的值在原列表里的索引
    """
    t = new_randint(0, sum(weight) - 1)
    logger.debug('RAND: %s', t)
    for index, value in enumerate(weight):
        t -= value
        if t < 0:
            logger.debug('INDEX: %s', index)
            return index


def new_randint(start=1, end=100, num=1):
    random.seed()
    rand_data = [random.randint(start, end) for i in range(0, num)]
    if num == 1:
        rand_data = rand_data[0]
    return rand_data


def encrypt_name(name):
    if len(name) == 2:
        name = '*' + name[1]
    elif len(name) >=3:
        name = name[0] + '*' * (len(name) - 2) + name[-1]
    return name
