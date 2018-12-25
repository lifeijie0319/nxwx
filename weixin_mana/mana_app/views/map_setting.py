# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, DEFAULT_PASSWORD
from ..logger import logger
from ..models import *
from ..tools import get_menu, log_action


@login_check
def page(request):
    setting = BankBranch.objects.all()
    context = {
        "data": setting
    }
    return render(request, APP_NAME + '/branch_setting.html', context)


@login_check
def query(request):
    setting_name = request.GET.get("setting_name")
    try:
        if setting_name:
            setting = BankBranch.objects.all().filter(user_name=setting_name)
        else:
            setting = BankBranch.objects.all()
        context = {"datas": setting}
        html = render_to_string(request, APP_NAME + "/branch_setting.html", context)
        res = {"success": True, "msg": u'查询成功', "html": html}
    except Exception e:
        logger.debug(e)
        res = {"success": False, "msg": u"查询失败"}
    return JsonResponse(res)


@login_check
def add(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    manager = Manager.objects.get(account=request.session.get("manager_account"))
    try:
        data = {
                "manager": manager,
                "num": post_data.get("num"),
                "deptno": post_data.get("deptno"),
                "address": post_data.get("address"),
                "telno": post_data.get("telno"),
                "officehours": post_data.get("officehours")
            }
        setting = BankBranch(**data)
        setting.save()
        settings = BankBranch.objects.all()
        context = {"datas": settings}
        html = render_to_string(APP_NAME + "/branch_setting.html", context)
        res = {"success": True, "msg": u"记录添加成功", "response_data": html}
    except Exception e:
        logger.debug(e)
        res = {"success": False, "msg": u"记录添加失败"}
    return JsonResponse(res)


@login_check
def delete(request):
    post_data = json.loads(request.body)
    id = post_data.get("id")
    try:
        if not BankBranch.objects.filter(id=id).exists():
            res = {"success": False, "msg": u"记录不存在"}
        else:
            setting = BankBranch.objects.get(id=id)
            setting.delete()
            settings = BankBranch.objects.all()
            context = {"datas": settings}
            html = render_to_string(APP_NAME + "/branch_setting.html", context)
            res = {"success": True, "msg": u"删除成功", "html": html}
    except Exception e:
        logger.debug(e)
        res = {"success": False, "msg": u"记录删除失败"}
    return JsonResponse(res)


@login_check
def update(request):
    post_data = json.loads(request.body)
    id = post_data.get('id')
    manager = Manager.objects.get(account=request.seesion.get("manager_account"))
    try:
        if not BankBranch.objects.filter(id=id).exists():
            res = {"success": False, "msg": u"记录不存在"}
        else:
            data = {
                "manager": manager,
                "num": post_data.get("num"),
                "deptno": post_data.get("deptno"),
                "address": post_data.get("address"),
                "telno": post_data.get("telno"),
                "officehours": post_data.get("officehours")
            }
            BankBranch.objects.filter(id=post_data.get("id")).update(**data)
            settings = BankBranch.objects.all()
            context = {"datas": settings}
            html = render_to_string(APP_NAME + "/branch_setting.html", context)
            res = {"success": True, "msg": u"更新成功", "html": html}
    except Exception e:
        logger.debug(e)
        res = {"success": False, "msg": u"记录更新失败"}
    return JsonResponse(res)
