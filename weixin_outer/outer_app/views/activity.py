# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import get_oauth_url, gen_token


@ensure_csrf_cookie
def index(request):
    """视图函数，返回json地址树"""
    logger.debug('request method: %s', request.method)
    if request.method == 'GET':
        openid = get_openid(request)
        activity_id = request.GET['activity_id']
        if not openid:
            origin_url = reverse(APP_NAME + ':activity') + '?activity_id=' + activity_id
            return redirect(get_oauth_url(origin_url))
        activity = send2serv({'path': 'activity.index', 'kargs': {'activity_id': activity_id}})
        ext_info = activity['ext_info']
        logger.debug('ACTIVITY_INFO RES:{}'.format(activity['ext_info'].keys()))
        context = {
            'activity_id': activity_id,
            'req_token': gen_token(),
        }
        if activity['typ'] == '信息登记':
            context['col1'] = ext_info.get(u'信息登记字段一')
            context['col2'] = ext_info.get(u'信息登记字段二')
            context['col3'] = ext_info.get(u'信息登记字段三')
        elif activity['typ'] == '盖楼':
            context['col1'] = '姓名'
            context['col2'] = '手机号'
            context['col3'] = '备注'
        logger.debug('ACTIVITY_INDEX RES:{}'.format(context))
        return render(request, APP_NAME + '/activity.html', context)
    elif request.method == 'POST':
        logger.debug('REQUEST:{}'.format(request.body))
        kwargs = {'openid': request.session.get('openid'), 'data': request.body}
        context = send2serv({'path': 'activity.submit', 'kargs': kwargs})
        return JsonResponse(context)


def index_check(request):
    logger.debug('REQUEST:{}'.format(request.GET))
    activity_id = request.GET.get('activity_id')
    kwargs = {'openid': request.session.get('openid'), 'activity_id': activity_id}
    context = send2serv({'path': 'activity.index_check', 'kargs': kwargs})
    return JsonResponse(context)
