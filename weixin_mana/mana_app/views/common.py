# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import redirect, render
from itertools import chain

from ..config import APP_NAME
from ..credits_api import insert_cus_credits, query_cus_credits, \
    update_cus_credits
from ..logger import logger
from ..tools import get_menu


def login_check(view_func):
    def wrapper(request, *args, **kargs):
        manager_account = request.session.get('manager_account')
        logger.debug('MANAGER: %s', manager_account)
        if manager_account:
            return view_func(request, *args, **kargs)
        else:
            return redirect(APP_NAME + ':login')

    return wrapper


@login_check
def static(request, name):
    return render(request, APP_NAME + '/' + name + '.html')


@login_check
def todo(request):
    menu = get_menu(request.manager.manager_name)
    context = {
        'menu': menu,
    }
    return render(request, APP_NAME + '/todo.html', context)


def get_ordered_shops(shop_set):
    return shop_set.order_by('-trade_times').order_by('-status').order_by('-stick')


def update_or_insert_credits(idcardno, credits):
    cusno = '101' + idcardno
    if query_cus_credits(cusno):
        ret = update_cus_credits(cusno, 100 * credits)
    else:
        ret = insert_cus_credits(cusno, 100 * credits)
    return ret


def query_credits(idcardno):
    cus_info = query_cus_credits('101' + idcardno)
    ret_credits = round(cus_info[0].get('JFYE') * 0.01) if cus_info else 0
    return ret_credits
