# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import datetime
import json
import xlrd

from django.http import FileResponse  
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse,HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string


from .common import login_check
from ..config import APP_NAME, CUR_INST, PAGE_SIZE
from ..logger import logger
from ..models import Coupon, Manager, Shop, Term,LotteryRecord,UserCoupon,CouponSend,User,RepetitionExclude
from ..tools import get_menu, log_action,generate_orderno,transaction_detail_save,gen_excel


@login_check
def page(request):
    manager_account = request.session.get('manager_account')
    context = {
        'manager_account': manager_account,
        'cur_inst': CUR_INST,
        'menu': get_menu(manager_account),
        'coupons': Coupon.objects.all(),
        'shops': Shop.objects.all(),
        'terms': Term.objects.all(),
        'discount_types': Coupon.DISCOUNT_TYPES,
        'term_relations': Coupon.RELATIONS,
    }
    return render(request, APP_NAME + '/coupon.html', context)


@login_check
def query(request):
    logger.debug(request.GET)
    coupon_name = request.GET.get('coupon_name')
    try:
        coupons = Coupon.objects.all()
        if coupon_name:
            coupons = coupons.filter(name__contains=coupon_name)

        if not coupons:
            context = {'coupons': coupons}
        else:
            paginator = Paginator(coupons, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_coupons = paginator.page(page)
            context = {'coupons': p_coupons}

        html = render_to_string(APP_NAME + '/coupon_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)


@login_check
def add(request):
    logger.debug(request.FILES)
    logger.debug(request.body)
    try:
        data = json.loads(request.body)
        term1_id = data.get('term1')
        term1_qs = Term.objects.filter(id=int(term1_id))
        data['term1'] = term1_qs.first() if term1_qs.exists() else None
        term2_id = data.get('term2')
        term2_qs = Term.objects.filter(id=int(term2_id))
        data['term2'] = term2_qs.first() if term2_qs.exists() else None
        logger.debug('DATA:%s', data)
        if data.get('fixed_amount') == '':
            data['fixed_amount'] = 0
        if not data.get('shops'):
            shops = []
        elif isinstance(data.get('shops'), list):
            shops = data.pop('shops')
        else:
            shops = [data.pop('shops')]
        logger.debug('DATA:%s', data)
        with transaction.atomic():
            coupon = Coupon.objects.create(**data)
            coupon.shops = shops
            manager = Manager.objects.get(account=request.session.get('manager_account'))
            log_action(manager, 'add', coupon)
            response_data = {'success':True, 'msg':'优惠券新增成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'优惠券新增失败'}
    return JsonResponse(response_data)

@login_check
def send(request):
    telno = request.POST.get('send_phone')
    now = datetime.datetime.now()
    num = 1
    if User.objects.filter(telno = telno).exists() is False:
        return JsonResponse({"success":False,"msg":u'该号码不存在'})
    with transaction.atomic():
        user = User.objects.filter(telno = telno).first()
        orderno = generate_orderno(1)[0]
        coupon = Coupon.objects.get(id = request.POST.get('coupon_id'))
        coupon.soldnum += num
        coupon.leftnum -= num
        coupon.save()
        log = transaction_detail_save(user, None, 0, '赠送优惠卷', str(num) + '张' + coupon.name, orderno)
        for i in range(0, num):
            user_coupon = UserCoupon(user=user, coupon=coupon, status='未使用',in_log = log)
            user_coupon.save()
            opera = Manager.objects.get(account = request.session.get('manager_account'))
            CouponSend.objects.create(user_coupon=user_coupon,operations = opera,time=now)
        response_data = {"success":True}
    return JsonResponse(response_data)

@login_check
def coupon_send_recode_page(request):
    if request.method == 'GET':
        manager_account = request.session.get('manager_account')
        context = {
            #'lottery_records': LotteryRecord.objects.filter(type='实物'),
            'manager_account': manager_account,
            'cur_inst': CUR_INST,
            'menu': get_menu(manager_account),
        }
    return render(request, APP_NAME + '/coupon_send_recode.html', context) 

@login_check
def coupon_send_recode_query(request):
    try:
        awards = CouponSend.objects.all()
        start_date = request.GET.get('start_date')
        logger.debug('START_DATE: %s', type(start_date))
        if start_date:
            start_datetime = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            logger.debug(start_datetime)
            awards = awards.filter(time__gte=start_datetime)
        end_date = request.GET.get('end_date')
        logger.debug('END_DATE: %s', type(end_date))
        if end_date:
            end_datetime = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            logger.debug(end_datetime)
            awards = awards.filter(time__lte=end_datetime)
        mode = request.GET.get('mode')

        if mode == 'excel':
            headers = ['获取用户', '优惠卷名称', '发送时间', '操作人员', '状态']
            datas = []
            for award in awards:
                logger.debug(award.time)
                data = [award.user_coupon.user.name, award.user_coupon.coupon.name, award.time.strftime('%Y-%m-%d %H:%M:%S'),award.operations.name
                    , award.user_coupon.status]
                datas.append(data)
            return gen_excel(headers, datas, '赠送清单')

        if not awards:
            context = {'lottery_records': awards}
        else:
            paginator = Paginator(awards, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_awards = paginator.page(page)
            context = {'lottery_records': p_awards}
        html = render_to_string(APP_NAME + '/coupon_send_recode_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)

@login_check
def coupon_send_some_page(request):
    if request.method == 'GET':
        manager_account = request.session.get('manager_account')
        context = {
            'manager_account': manager_account,
            'cur_inst': CUR_INST,
            'menu': get_menu(manager_account),
        }
    return render(request, APP_NAME + '/coupon_send_some.html', context) 

@login_check
def coupon_send_some_query(request):
    logger.debug(request.GET)
    coupon_name = request.GET.get('coupon_name')
    try:
        coupons = Coupon.objects.all().filter(term1__description__isnull=True,term2__description__isnull=True)
        if coupon_name:
            coupons = coupons.filter(name__contains=coupon_name)

        if not coupons:
            context = {'coupons': coupons}
        else:
            paginator = Paginator(coupons, PAGE_SIZE)
            page = int(request.GET.get('page', 1))
            page = max(1, min(page, paginator.num_pages))
            p_coupons = paginator.page(page)
            context = {'coupons': p_coupons}

        html = render_to_string(APP_NAME + '/coupon_send_some_table.html', context)
        res = {'success': True, 'msg': u'查询成功', 'html': html}
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': u'查询失败'}
    return JsonResponse(res)

@login_check
def coupon_upload_send_some(request):
    path = "/tmp/csv/"
    if request.method == 'POST':
        myFile = request.FILES.get('myfile')
        if not myFile:
            res = {'success': False, 'msg': '未选择文件上传'}
            return JsonResponse(res)
        destination = open(os.path.join(path,myFile.name),'wb+')    # 打开特定的文件进行二进制的写操作
        for chunk in myFile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()    
        read_xml = path+myFile.name
        res = xml_import(read_xml,request)
    return JsonResponse(res)


def xml_import(read_xml,request):
    path = read_xml
    try:
        #此处读取excel文件并写入数据库
        excel=xlrd.open_workbook(path) 
        sheet = excel.sheet_by_index(0)
        cols_1=sheet.col_values(0)#第三行内容
        cols_2=sheet.col_values(1)#第二列内容
        cols_3=sheet.col_values(2)
        nos = []
        name = []
        num = []
        for inx, val in enumerate(cols_1):
            if inx !=0:
                name.append(val)
        for inx, val in enumerate(cols_2):
            if inx !=0:
                nos.append(val)
        for inx, val in enumerate(cols_3):
            if inx !=0:
                num.append(val)
        res = send_tool(nos,name,num,request)
    except Exception, e:
        logger.exception(e)
        res = {'success': False, 'msg': '批量赠送失败'}
    return res

def send_tool(nos,name,nums,request):
    try :
        for i in nos:
            if User.objects.filter(idcardno = i).exists() is False:
                return ({"success":False,"msg":'该身份证号不存在'})
        for i in name:
            if Coupon.objects.filter(name=i,term1__description__isnull=False).exists() or Coupon.objects.filter(name=i,term2__description__isnull=False).exists():
                return ({"success":False,"msg":'存在不符合赠送要求的优惠券'})
        for inx,val in enumerate(nos) :
            now = datetime.datetime.now()
            num = int(nums[inx])
            logger.debug(val)
            with transaction.atomic():
                user = User.objects.filter(idcardno = val).first()
                orderno = generate_orderno(1)[0]
                coupon = Coupon.objects.get(name = name[inx])
                coupon.soldnum += num
                coupon.leftnum -= num
                coupon.save()
                log = transaction_detail_save(user, None, 0, '赠送优惠卷', str(num) + '张' + coupon.name, orderno)
                for i in range(0, num):
                    user_coupon = UserCoupon(user=user, coupon=coupon, status='未使用',in_log = log)
                    user_coupon.save()
                    opera = Manager.objects.get(account = request.session.get('manager_account'))
                    CouponSend.objects.create(user_coupon=user_coupon,operations = opera,time=now)
        response_data  ={'success':True,'msg':'赠送成功'}
    except Exception,e:
        logger.exception(e)
        response_data  ={'success':False,'msg':'录入模板中存在未命名的优惠券'}
    return (response_data)

@login_check
def download_temp(request):
    file=open('/tmp/tmp_for_send.xls','rb')  
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="tmp_for_send.xls"'  
    return response 


@login_check
def delete(request):
    post_data = json.loads(request.body)
    logger.debug(post_data)
    coupon_id = post_data.get('coupon_id')
    if not Coupon.objects.filter(id=coupon_id).exists():
        response_data = {'success': False, 'msg': '优惠券不存在'}
        return JsonResponse(response_data)
    try:
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get("manager_account"))
            coupon = Coupon.objects.get(id=coupon_id)
            log_action(manager, 'delete', coupon)
            coupon.delete()
            response_data = {'success': True, 'msg': '优惠券删除成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg': '优惠券删除失败'}
    return JsonResponse(response_data)


@login_check
def update(request):
    data = json.loads(request.body)
    logger.debug('COUPON UPDATE: %s', data)
    try:
        coupon_id = data.pop('id')
        term1_id = data.get('term1')
        term1_qs = Term.objects.filter(id=int(term1_id))
        data['term1'] = term1_qs.first() if term1_qs.exists() else None
        term2_id = data.get('term2')
        term2_qs = Term.objects.filter(id=int(term2_id))
        data['term2'] = term2_qs.first() if term2_qs.exists() else None
        logger.debug('DATA:%s', data)
        if data.get('fixed_amount') == '':
            data['fixed_amount'] = 0
        if not data.get('shops'):
            shops = []
        elif isinstance(data.get('shops'), list):
            shops = data.pop('shops')
        else:
            shops = [data.pop('shops')]
        with transaction.atomic():
            manager = Manager.objects.get(account=request.session.get("manager_account"))
            Coupon.objects.filter(id=coupon_id).update(**data)
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.shops = shops
            log_action(manager, 'update', coupon, data.keys())
            response_data = {'success':True, 'msg':'优惠券更新成功'}
    except Exception, e:
        logger.exception(e)
        response_data = {'success': False, 'msg':'优惠券更新失败'}
    return JsonResponse(response_data)


#@login_check
#def detail(request):
#    logger.debug(request.GET)
#    coupon_id = request.GET.get('coupon_id')
#    logger.debug(coupon_id)
#    try:
#        coupon = Coupon.objects.get(id=coupon_id)
#        html = render_to_string(APP_NAME + '/coupon_detail_table.html', {'coupon': coupon})
#        response_data = {'success': True, 'html': html}
#    except Exception, e:
#        logger.exception(e)
#        response_data = {'success': False, 'msg': e}
#    return JsonResponse(response_data)


@login_check
def upload(request):
    logger.debug(request.FILES)
    logger.debug(request.POST)
    coupon_id = request.POST.get('coupon_id')
    img = request.FILES.get('img')
    logger.debug(img)
    #count = 0
    #if not isinstance(imgs, list):
    #    imgs = [imgs]
    #for img in imgs:
    #    count += 1
    #    index = str(count)
    path = APP_NAME + '/media/coupon/' + coupon_id + '.jpg'
    logger.debug('PATH: %s', path)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, img)
    return JsonResponse({'success': True})
