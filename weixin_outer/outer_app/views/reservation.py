#coding:utf-8
import json
import time
import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie

from .common import certified_cus_check, get_openid, is_manager_check, user_register_check
from ..config import APP_NAME
from ..global_var import logger
from ..socket_client import send2serv
from ..tools import gen_token
from ..template_msg import application_feedback, reservation_apply


@ensure_csrf_cookie
@user_register_check
def reservation_page(request,url):
    context = send2serv({'path':'reservation_inter.load_bank','kargs':{'url':url}})
    context['req_token'] = gen_token()
    #logger.debug(context)
    return render(request, APP_NAME + url, context)


def reservation_ETC_page(request):
    url = '/reservation_etc.html'
    return reservation_page(request, url)


def reservation_loan_page(request):
    url = '/reservation_loan.html'
    return reservation_page(request, url)


@ensure_csrf_cookie
@user_register_check
@is_manager_check
def dgkh_page(request):
    context = send2serv({'path': 'reservation_inter.dgkh_page', 'kargs': {}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/reservation_dgkh.html', context)


@ensure_csrf_cookie
@user_register_check
@is_manager_check
def kdd_index(request):
    return render(request, APP_NAME + '/reservation_kdd_index.html')


def kdd_page(request):
    context = send2serv({'path': 'reservation_inter.kdd_page', 'kargs': {}})
    context['req_token'] = gen_token()
    return render(request, APP_NAME + '/reservation_kdd.html', context)


@is_manager_check
def reservation_num_taking_page(request):
    url = '/reservation_num_taking.html'
    return reservation_page(request, url)


def reservation_open_account_page(request):
    url = '/reservation_open_account.html'
    return reservation_page(request, url)


def reservation_withdrawal_page(request):
    url = '/reservation_withdrawal.html'
    return reservation_page(request, url)


def reservation(request, busi_type):
#   发送消息给管理员
    openid = get_openid(request)
    logger.debug(request.body)
    kargs = {
        'data': request.body,
        'openid': openid,
        'busi_type':busi_type
    }
    context = send2serv({'path': 'reservation_inter.reservation', 'kargs': kargs})
    if context.get('success'):
        openids = context.get('openids')
        reservation = context.get('reservation')
        reservation_apply(reservation, openids)
    logger.debug('RESERVATION RES: %s', context)
    return JsonResponse(context)


def reservation_open_account(request):
    return reservation(request, '开户预约')


def reservation_ETC(request):
    return reservation(request, 'ETC预约')


def get_loan_msg(data):
    mode = data.get('mode')
    if mode == 'micro_credit_contract':
        limit = round(int(data.get('limit'))/10000, 2)
        msg = '尊敬的%s先生/女士，恭喜您已获得南浔银行贷款授信%s万元,' +\
            '本行贷款支持手机银行（丰收互联）线上放款，如有需要请点击详情下载，' + \
            '打开丰收互联，点击“我要贷款”，轻松一点，即刻到账。如您需要提升贷款额度，' +\
            '请联系本行客户经理%s，联系电话%s！'
        msg = msg % (data.get('user_name'), limit, data.get('handler_name'), data.get('handler_mobile'))
    elif mode == 'pre_credit_line':
        limit = round(int(data.get('limit'))/10000, 2)
        msg = '尊敬的%s先生/女士，恭喜您获得南浔银行预授信额度%s万元，' +\
            '正式授信额度以本行客户经理实地调查后反馈为准。如有需要，' +\
           ' 请联系本行客户经理%s，联系电话%s！'
        msg = msg % (data.get('user_name'), limit, data.get('handler_name'), data.get('handler_mobile'))
    elif mode == 'grid':
        msg = '尊敬的%s先生/女士，您还未获得南浔银行贷款授信额度，' +\
            '本行客户经理%s，联系电话%s会及时与您取得联系！'
        msg = msg % (data.get('user_name'), data.get('handler_name'), data.get('handler_mobile'))
    else:
        msg = ''
    return msg


def reservation_loan(request):
    openid = get_openid(request)
    kargs = {
        'data': request.body,
        'openid': openid,
    }
    context = send2serv({'path': 'reservation_inter.reservation_loan', 'kargs': kargs})
    logger.debug(context)
    if context.get('success'):
        data = context.get('res_data')
        reservation_apply(data, context.get('openids'))
        if data.get('mode') != 'default':
            data['openid'] = openid
            data['msg'] = get_loan_msg(data)
            application_feedback(data)
    return JsonResponse(context)


def kdd_param(request):
    context = context = send2serv({'path': 'reservation_inter.kdd_param', 'kargs': {}})
    return JsonResponse(context)


def kdd_search(request):
    kargs = {
        'keywords': request.GET.get('query'),
    }
    context = send2serv({'path': 'reservation_inter.kdd_search', 'kargs': kargs})
    context['query'] = 'Unit'
    return JsonResponse(context)


def kdd_submit(request):
    return reservation(request, '快抵贷')


def dgkh_nearest_branch(request):
    logger.info(request.GET)
    context = send2serv({'path': 'reservation_inter.dgkh_nearest_branch', 'kargs': request.GET})
    return JsonResponse(context)


def dgkh_submit(request):
    data = json.loads(request.body)
    logger.debug(data)
    vcode = data.pop('vcode')
    real_vcode = request.session.get('vcode')
    logger.info('real_vcode: %s', real_vcode)
    if not real_vcode:
        return JsonResponse({'success': False, 'msg': u'未获取验证码'})
    if int(vcode) != int(real_vcode):
        return JsonResponse({'success': False, 'msg': u'验证码不匹配'})
    return reservation(request, '对公开户预约')


def reservation_withdrawal(request):
    return reservation(request, '取现预约')


def reservation_num_taking(request):
    return reservation(request, '取号预约')


def reservation_status_list(request):
    kargs = {
        'openid': get_openid(request),
        'st': request.GET.get('st'),
        'page': int(request.GET.get('page')),
    }
    context = send2serv({'path': 'reservation_inter.reservation_status_list', 'kargs': kargs})
    logger.debug(context)
    html = render_to_string(APP_NAME + '/reservation_status_list.html', context)
    new_context = {'html': html, 'page': context.get('page')}
    return JsonResponse(new_context)


def reservation_deal_list(request):
    openid = get_openid(request) 
    kargs = {
        'openid': get_openid(request),
        'st': request.GET.get('st'),
        'page': int(request.GET.get('page')),
    }
    context = send2serv({'path': 'reservation_inter.reservation_deal_list', 'kargs': kargs})
    html = render_to_string(APP_NAME + '/reservation_deal_list.html', context)
    new_context = {'html': html, 'page': context.get('page')}
    return JsonResponse(new_context)


def reservation_deal_submit(request):
    openid = get_openid(request)
    logger.debug(request.POST)
    orderno = request.POST.get('orderno')
    kargs = {
        'openid': openid,
        'orderno': orderno,
    }
    context = send2serv({'path': 'reservation_inter.reservation_deal_submit', 'kargs': kargs})
    data = context.get('res_data')
    logger.debug(data)
    if data:
        busi_type = data.get('busi_type')
        if busi_type == '贷款预约':
            data['mode'] = 'grid'
            data['msg'] = get_loan_msg(data)
        else:
            data['msg'] = '您的' + busi_type + '申请已受理，请联系' + data.get('handler_name') + '，联系方式'\
                + data.get('handler_mobile')
        application_feedback(data)
    return JsonResponse(context)
