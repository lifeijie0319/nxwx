#-*- coding:utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import get_openid, repitition_deny, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..template_msg import seller_replace_apply_msg


@ensure_csrf_cookie
@user_register_check
def page(request):
    request.session['handle_flag'] = False
    openid = get_openid(request)
    context = send2serv({'path': 'seller_replace_audit.page', 'kargs': {'openid': openid}})
    return render(request, APP_NAME + '/seller_replace_audit.html', context)


@repitition_deny
def head_admin(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    context = send2serv({'path': 'seller_replace_audit.head_admin', 'kargs': request.POST})
    if context.get('success'):
        branch_admins_openid = context.get('branch_admins_openid')
        data = context.get('data')
        seller_replace_apply_msg(branch_admins_openid, data)
    return JsonResponse(context)


@repitition_deny
def branch_admin(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    context = send2serv({'path': 'seller_replace_audit.branch_admin', 'kargs': request.POST})
    if context.get('success'):
        client_manager_openid = context.get('client_manager_openid')
        data = context.get('data')
        seller_replace_apply_msg(client_manager_openid, data)
    return JsonResponse(context) 


@repitition_deny
def client_manager(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    kargs = request.POST.copy()
    context = send2serv({'path': 'seller_replace_audit.client_manager', 'kargs': kargs})
    if context.get('success'):
        head_admins_openid = context.get('head_admins_openid')
        data = context.get('data')
        seller_replace_apply_msg(head_admins_openid, data)
    return JsonResponse(context)


@repitition_deny
def recheck(request):
    logger.debug('POST: %s', request.POST)
    logger.debug('BODY: %s', request.body)
    kargs = request.POST.copy()
    context = send2serv({'path': 'seller_replace_audit.recheck', 'kargs': kargs})
    return JsonResponse(context)
