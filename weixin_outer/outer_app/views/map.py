# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, is_manager_check, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv


@ensure_csrf_cookie
@user_register_check
@is_manager_check
def page(request):
    return render(request, APP_NAME + '/map.html')


def branch_data(request):
    context = send2serv({'path': 'map.branch_data', 'kargs':{}})
    return JsonResponse(context)
