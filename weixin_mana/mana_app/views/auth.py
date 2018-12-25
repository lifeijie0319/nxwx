# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from .common import login_check
from ..config import APP_NAME, CUR_INST
from ..tools import get_menu, log_action
from ..logger import logger
from ..models import Manager


def login(request):
    if request.method == 'POST':
        manager_account = request.POST.get('manager_account', None)
        password = request.POST.get('password', None)
        try:
            manager = Manager.objects.get(account=manager_account)
        except:
            response_data = {'success': False, 'msg': u'用户不存在'}
            return JsonResponse(response_data)
        else:
            if manager.check_password(password):
                request.session['manager_account'] = manager.account
                url = '/' + APP_NAME + '/index/'
                response_data = {'success': True, 'msg': u'登录成功', 'url': url}
            else:
                response_data = {'success': False, 'msg': u'密码错误'}
            return JsonResponse(response_data)
    return render(request, APP_NAME + '/login.html')


def is_manager_exist(request):
    manager_account = request.POST.get('manager_account')
    logger.debug(manager_account)
    exist_flag = Manager.objects.filter(account=manager_account).exists()
    logger.debug('EXIST: %s', exist_flag)
    return JsonResponse({'exist_flag': exist_flag})


@login_check
def logout(request):
    del request.session['manager_account']
    return HttpResponseRedirect('/mana_app/login/')


@login_check
def index(request):
    manager_account = request.session.get('manager_account')
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    logger.debug(context)
    return render(request, APP_NAME + '/index.html', context)


@login_check
def password_change(request):
    logger.debug(request.POST)
    old_password = request.POST.get('base_old_passwd')
    new_passwd_1 = request.POST.get('base_new_passwd')
    new_passwd_2 = request.POST.get('base_new_passwd_confirm')
    if new_passwd_1 != new_passwd_2:
        response_data = {'success': False, 'msg': u'新密码不一致，请检查!'}
        return JsonResponse(response_data)
    try:
        manager_account = request.session.get('manager_account')
        manager = Manager.objects.get(account=manager_account)
        if manager.check_password(old_password):
            with transaction.atomic():
                manager.set_password(new_passwd_1)
                manager.save()
                log_action(manager, 'update', manager, ['password'])
                response_data = {'success': True, 'msg': u'密码更新成功'}
        else:
            response_data = {'success': False, 'msg': u'原密码错误，请检查!'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': u'密码更新失败'}
    return JsonResponse(response_data)
