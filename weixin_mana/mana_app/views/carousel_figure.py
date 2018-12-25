# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.files.storage import default_storage
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .common import login_check
from ..config import APP_NAME, CUR_INST
from ..logger import logger
from ..models import CarouselFigure
from ..tools import get_menu, log_action


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'figures': CarouselFigure.objects.all(),
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
    }
    return render(request, APP_NAME + '/carousel_figure.html', context)


@login_check
def update(request):
    logger.debug(request.POST)
    figure_name = request.POST.get('figure_name')
    logger.debug(request.FILES)
    img = request.FILES.get('img')
    logger.debug(img)
    #count = 0 
    #if not isinstance(imgs, list):
    #    imgs = [imgs]
    #for img in imgs:
    #    count += 1
    #    index = str(count)
    path = APP_NAME + '/media/carousel_figure/' + figure_name + '.jpg'
    logger.debug('path: %s', path)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, img)
    return JsonResponse({'success': True})
