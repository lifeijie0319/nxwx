# -*- coding: utf-8 -*-
"""自定义中间件

该模块用于自定义中间件，拦截http请求和返回值
"""
#middleware.py
#
#Copyright (C) 2017 YINSHO(Shanghai) SoftWare Technology Co., Ltd.
#All rights reserved
#
__author__  = "lifeijie <lifeijie@yinsho.com>"

from __future__ import unicode_literals

from django.http import HttpResponse
from global_var import logger


def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        #限制请求来自于微信浏览器
        user_agent = request.META.get('HTTP_USER_AGENT')
        #logger.debug('USER_AGENT: %s', user_agent)
        if user_agent and not 'MicroMessenger' in request.META.get('HTTP_USER_AGENT'):
            return HttpResponse(u'请在微信客户端打开链接')
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
