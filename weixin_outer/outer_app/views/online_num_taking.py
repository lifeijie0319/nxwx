#-*- coding:utf-8 -*-
import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, is_manager_check, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import gen_token


@ensure_csrf_cookie
@user_register_check
@is_manager_check
def page(request):
    openid = get_openid(request)
    context = {}
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/online_num_taking.html', context)


def waitman(request):
    openid = request.session.get('openid')
    context = send2serv({'path': 'online_num_taking.waitman', 'kargs': {}})
    return JsonResponse(context)


def submit(request):
    '''申请排队号
    根据选择的银行获取排队号，
    并存入排队号信息
    '''
    data = json.loads(request.body)
    openid = get_openid(request)
    data['openid'] = openid
    logger.debug(data)
    context = send2serv({'path': 'online_num_taking.submit', 'kargs': data})
    return JsonResponse(context)


@ensure_csrf_cookie
@user_register_check
@is_manager_check
def status_page(request):
    return render(request, APP_NAME + '/online_num_taking_status.html')


def status_list(request):
    kargs = {
        'openid': get_openid(request),
        'st': request.GET.get('st'),
        'page': int(request.GET.get('page')),
    }
    context = send2serv({'path': 'online_num_taking.status_list', 'kargs': kargs})
    html = render_to_string(APP_NAME + '/online_num_taking_status_list.html', context)
    new_context = {'html': html.strip(), 'page': context.get('page')}
    return JsonResponse(new_context)
