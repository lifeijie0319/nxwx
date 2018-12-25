#-*- coding:utf-8 -*-
import datetime
import jieba
import json
import time

from decimal import Decimal
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

from .common import get_manager_user
from ..config import RESERVATION_PAGE_SIZE
from ..logger import logger
from ..models import BankBranch, CommonParam, CommunityAssess, CusRegion, ETCReservation, LoanReservation,\
    Manager, ManagerRegion, MicroCreditContract, NumberTakingReservation, OpenAccountReservation,\
    PreCreditLine, RepetitionExclude, Reservation, ReservationForbidenDate, ReservationDGKH, ReservationKDD,\
    User, WithdrawalReservation
from ..tools import generate_orderno, to_json
from ..web_client import WsdlClient


def kdd_page():
    banks = BankBranch.objects.filter(is_loan=True).order_by('deptno')
    context = {
        'banks': [{
            'id': bank.id,
            'name': bank.name,
        } for bank in banks],
        'house_properties': [house_property[0] for house_property in ReservationKDD.HOUSE_PROPERTIES],
        'house_regions': [house_region[0] for house_region in ReservationKDD.HOUSE_REGIONS],
    }
    return context


def dgkh_page():
    banks = BankBranch.objects.filter(is_dgkh=True).order_by('deptno')
    context = {
        'banks': [{
            'id': bank.id,
            'name': bank.name,
            'telno': bank.telno.strip(),
        } for bank in banks],
        'subtypes': [subtype[0] for subtype in ReservationDGKH.SUBTYPES],
    }
    return context


def dgkh_nearest_branch(lat, lng):
    def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
        """ 
        Calculate the great circle distance between two points  
        on the earth (specified in decimal degrees) 
        """  
        # 将十进制度数转化为弧度  
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  
      
        # haversine公式  
        dlon = lon2 - lon1   
        dlat = lat2 - lat1   
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2  
        c = 2 * asin(sqrt(a))   
        r = 6371 # 地球平均半径，单位为公里  
        return c * r * 1000
    lat = Decimal(lat)
    lng = Decimal(lng)
    banks = BankBranch.objects.filter(is_dgkh=True)
    nearest = banks.first()
    min_distance = haversine(lng, lat, nearest.longitude, nearest.latitude)
    for bank in banks:
        diatance = haversine(lng, lat, bank.longitude, bank.latitude)
        if diatance < min_distance:
            nearest = bank
            min_distance = diatance
    return {'branch_id': nearest.id, 'branch_name': nearest.name}


def load_bank(url):
    logger.debug(url)
    if url =='/reservation_open_account.html':
        banks = BankBranch.objects.filter(is_oppen_account = True).order_by('deptno')
    elif url =='/reservation_loan.html':
        banks = BankBranch.objects.filter(is_loan = True).order_by('deptno')
    elif url =='/reservation_num_taking.html' :
        banks = BankBranch.objects.filter(is_num_taking = True).order_by('deptno')
    elif url =='/reservation_etc.html' :
        banks = BankBranch.objects.filter(is_etc = True).order_by('deptno')
    elif url == '/reservation_withdrawal.html':
        banks = BankBranch.objects.filter(is_withdrawal = True).order_by('deptno')
    else:
        banks = BankBranch.objects.all().order_by('deptno')
    context = {'banks': [{
        'id': bank.id,
        'name': bank.name,
        'waitman': bank.waitman,
    } for bank in banks]}
    return context


def is_working_time(dtime):
    logger.debug(dtime)
    dtime = dtime.strip()
    if len(dtime) == 16:
        dtime = datetime.datetime.strptime(dtime, '%Y-%m-%dT%H:%M')
    else:
        dtime = datetime.datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%S')
    if dtime.date() <= datetime.date.today():
        return {'success': False, 'msg': '预约不能早于下一个工作日'}
    elif ReservationForbidenDate.objects.filter(date=dtime.date()).exists():
        return {'success': False, 'msg': '该日期是节假日，无法预约'}
    elif dtime.time() < datetime.time(8, 30) or dtime.time() > datetime.time(15, 30):
        return {'success': False, 'msg': '超出营业时间'}
    else:
        return {'success': True, 'dtime': dtime}


def get_receivers(branch, busi_type, handler=None):
    logger.debug('%s, %s, %s', branch, busi_type, handler)
    managers = Manager.objects.filter(bankbranch=branch, status='normal')
    logger.debug('%s', managers)
    if busi_type in ('取号预约', '取现预约'):
        managers = managers.filter(role='柜面人员')
    elif busi_type == '对公开户预约':
        managers = managers.filter(role='柜面人员').filter(subrole='对公账管专员')
    elif busi_type == '贷款预约' and handler:
        managers = list(managers.filter(role='支行管理员'))
        managers.append(handler)
        logger.debug('%s', managers)
    else:
        managers = managers.filter(role__in=('客户经理', '支行管理员'))
    users = get_manager_user(managers)
    openids = [user.openid for user in users]
    return {'managers': managers, 'users': users, 'openids': openids}


def check_reservation_num(openid, busi_type):
    now = datetime.datetime.now()
    interval_limit = int(CommonParam.objects.get(name='最短预约提交间隔').value)
    interval_limit = datetime.timedelta(seconds=interval_limit)
    if Reservation.objects.filter(user__openid=openid, apply_dtime__gt=(now-interval_limit))\
        .filter(busi_type=busi_type).exists():
        return {'success': False, 'msg': '短时间内不允许重复提交'}
    today_start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    today_reservations = Reservation.objects.filter(user__openid=openid, apply_dtime__gt=today_start)
    if busi_type == '取号预约':
        day_count = today_reservations.filter(busi_type='取号预约').count()
        day_limit = int(CommonParam.objects.get(name='预约取号单日提交上限').value)
        if day_count >= day_limit:
            return {'success': False, 'msg': '单日预约取号不能超过' + str(day_limit) + '次'}
    else:
        day_count = today_reservations.filter(busi_type=busi_type).count()
        day_limit = int(CommonParam.objects.get(name='普通预约单日提交上限').value)
        if day_count >= day_limit:
            return {'success': False, 'msg': '单日' + busi_type + '不能超过' + str(day_limit) + '次'}
    return {'success': True}


def reservation(openid, data, busi_type):
    data = json.loads(data)
    logger.debug('DATA:%s', data)
    req_token = data.pop('req_token')
    user = User.objects.get(openid=openid)
    bank_id = data.get('branch')
    branch = BankBranch.objects.get(id=bank_id)

    reservation_num_result = check_reservation_num(openid, busi_type)
    if not reservation_num_result.get('success'):
        return reservation_num_result

    openids = get_receivers(branch, busi_type).get('openids')
    if not openids:
        return {'success': False, 'msg': '该机构没有合适的处理人员'}

    data['user'] = user
    data['branch'] = branch
    data['busi_type'] = busi_type
    data['status'] = '未受理'
    data['orderno'] = generate_orderno(1)[0]
    logger.debug(data)
    with transaction.atomic():
        if busi_type == '开户预约':
            RepetitionExclude.objects.create(req_token=req_token)
            OpenAccountReservation.objects.create(**data)
        elif busi_type == '对公开户预约':
            RepetitionExclude.objects.create(req_token=req_token)
            data.pop('vcode')
            ReservationDGKH.objects.create(**data)
        elif busi_type == 'ETC预约':
            RepetitionExclude.objects.create(req_token=req_token)
            ETCReservation.objects.create(**data)
        elif busi_type == '快抵贷':
            RepetitionExclude.objects.create(req_token=req_token)
            data['house_area'] = int(float(data['house_area']))
            ReservationKDD.objects.create(**data)
        elif busi_type == '取现预约':
            dtime = data.get('withdrawaltime')
            is_working_result = is_working_time(dtime)
            if is_working_result.get('success'):
                data['withdrawaltime'] = is_working_result.get('dtime')
                RepetitionExclude.objects.create(req_token=req_token)
                WithdrawalReservation.objects.create(**data)
            else:
                return is_working_result
        elif busi_type == '取号预约':
            taking_time = data.get('taking_time')
            is_working_result = is_working_time(taking_time)
            if not is_working_result.get('success'):
                return is_working_result
            taking_time = is_working_result.get('dtime')
            ahead_minutes = int(CommonParam.objects.get(name='预约叫号提前时间').value)
            start_time = taking_time - datetime.timedelta(minutes=ahead_minutes)
            delay_minutes = int(CommonParam.objects.get(name='预约叫号延后时间').value)
            end_time = taking_time + datetime.timedelta(minutes=delay_minutes)
            cli = WsdlClient()
            appoint_result = cli.get_appointment(start_time, end_time, user.idcardno, branch.deptno)
            if appoint_result.get('success'):
                data['status'] = '已受理'
                RepetitionExclude.objects.create(req_token=req_token)
                NumberTakingReservation.objects.create(**data)
            else:
                return appoint_result
    reservation = {
        'user_name': user.name,
        'busi_type': busi_type,
        'user_mobile': user.telno,
    }
    return {'success': True, 'openids': openids, 'reservation': reservation}


def get_loan_mode(idcardno):
    micro_credit_contract = MicroCreditContract.objects.filter(cusno='101'+idcardno).first()
    if micro_credit_contract:
        manager = micro_credit_contract.manager
        m_user = User.objects.filter(idcardno=manager.idcardno).first()
        if m_user:
            return {
                'mode': 'micro_credit_contract',
                'manager': manager,
                'm_user': m_user,
                'limit': micro_credit_contract.limit
            }
    pre_credit_line = PreCreditLine.objects.filter(cusno='101'+idcardno).first()
    if pre_credit_line:
        manager = pre_credit_line.manager
        m_user = User.objects.filter(idcardno=manager.idcardno).first()
        if m_user:
            return {
                'mode': 'pre_credit_line',
                'manager': manager,
                'm_user': m_user,
                'limit': pre_credit_line.limit,
            }
    cus_region = CusRegion.objects.filter(cusno='101'+idcardno).first()
    if cus_region:
        manager_region = ManagerRegion.objects.filter(address_code=cus_region.address_code).first()
        if manager_region:
            manager = manager_region.manager
            m_user = User.objects.filter(idcardno=manager.idcardno).first()
            if m_user:
                return {'mode': 'grid', 'manager': manager, 'm_user': m_user}
    return {'mode': 'default'}


def reservation_loan(openid, data):
    data = json.loads(data)
    req_token = data.pop('req_token')
    user = User.objects.get(openid=openid)
    bank_id = data.get('branch')
    branch = BankBranch.objects.get(id=bank_id)

    reservation_num_result = check_reservation_num(openid, '贷款预约')
    if not reservation_num_result.get('success'):
        return reservation_num_result

    data['user'] = user
    data['branch'] = branch
    data['busi_type'] = '贷款预约'
    data['status'] = '未受理'
    data['orderno'] = generate_orderno(1)[0]

    loan_mode_res = get_loan_mode(user.idcardno)
    loan_mode = loan_mode_res.get('mode')
    with transaction.atomic():
        if loan_mode == 'default':
            openids = get_receivers(branch, '贷款预约').get('openids')
            if not openids:
                return {'success': False, 'msg': '该机构没有合适的处理人员'}
            RepetitionExclude.objects.create(req_token=req_token)
            LoanReservation.objects.create(**data)
            res_data = {
                'user_name': user.name,
                'busi_type': '贷款预约',
                'user_mobile': user.telno,
                'mode': 'default', 
            }
            return {'success': True, 'openids': openids, 'res_data': res_data}
        else:
            handler = loan_mode_res.get('manager')
            handler_user = loan_mode_res.get('m_user')
            openids = get_receivers(handler.bankbranch, '贷款预约', handler).get('openids')
            data['handler'] = handler
            data['branch'] = handler.bankbranch
            RepetitionExclude.objects.create(req_token=req_token)
            loan_reservation = LoanReservation.objects.create(**data)
            res_data = {
                'user_name': user.name,
                'busi_type': '贷款预约',
                'user_mobile': user.telno,
                'apply_dtime': loan_reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                'limit': loan_mode_res.get('limit', 0),
                'handler_name': handler_user.name,
                'handler_mobile': handler_user.telno,
                'mode': loan_mode,
            }
            return {'success': True, 'openids': openids, 'res_data': res_data}


def reservation_status_list(openid, st, page=1):
    user = User.objects.get(openid=openid)
    reservations = Reservation.objects.filter(user=user, status=st).order_by("-apply_dtime")
    paginator = Paginator(reservations, RESERVATION_PAGE_SIZE)
    page = max(1, min(page, paginator.num_pages))
    ret_page = -1 if page == paginator.num_pages else page
    logger.debug('%s, %s, %s, %s', reservations.count(), page, paginator.num_pages, ret_page)
    reservations = paginator.page(page)
    ret_reservations = []
    for reservation in reservations:
        data = {
            'orderno': reservation.orderno,
            'status': reservation.status,
            'apply_dtime': reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
            'busi_type': reservation.busi_type,
            'branch_name': reservation.branch.name,
            'branch_telno': reservation.branch.telno,
        }
        if reservation.handler and reservation.busi_type != '取号预约':
            data['manager_name'] = reservation.handler.name
            m_user = User.objects.get(idcardno=reservation.handler.idcardno)
            data['manager_telno'] = m_user.telno
        if reservation.busi_type == 'ETC预约':
            data['plate_num'] = reservation.etcreservation.platenum
        elif reservation.busi_type == '快抵贷':
            data['orgname'] = reservation.reservationkdd.orgname
            data['house_property'] = reservation.reservationkdd.house_property
            #data['house_region'] = reservation.reservationkdd.house_region
            data['house_location'] = reservation.reservationkdd.house_location
            data['assess_price'] = int(reservation.reservationkdd.assess_price) if reservation.reservationkdd.assess_price else None
        elif reservation.busi_type == '取现预约':
            data['withdrawal_balance'] = reservation.withdrawalreservation.withdrawalnum
            data['withdrawal_dtime'] = reservation.withdrawalreservation.withdrawaltime.strftime('%Y-%m-%d %H:%M:%S')
        elif reservation.busi_type == '取号预约':
            data['taking_time'] = reservation.numbertakingreservation.taking_time.strftime('%Y-%m-%d %H:%M:%S')
        elif reservation.busi_type == '对公开户预约':
            data['liscence'] = reservation.reservationdgkh.liscence
            data['orgname'] = reservation.reservationdgkh.orgname
            data['subtype'] = reservation.reservationdgkh.subtype
            data['due_date'] = reservation.reservationdgkh.due_date.isoformat()
            data['remark'] = reservation.reservationdgkh.remark
        ret_reservations.append(data)
    return {'reservations': ret_reservations, 'page': ret_page}


def reservation_deal_list(openid, st, page=1):
    user = User.objects.get(openid=openid)
    manager = Manager.objects.get(idcardno=user.idcardno)
    reservations = Reservation.objects.filter(branch=manager.bankbranch, status=st).order_by("-apply_dtime")
    if manager.role == '客户经理':
        Q1 = Q(busi_type__in=('ETC预约', '取号预约', '开户预约', '快抵贷'))
        Q2 = Q(busi_type='贷款预约')&Q(handler__isnull=True)
        Q3 = Q(busi_type='贷款预约')&Q(handler=manager)
        reservations = reservations.filter(Q1|Q2|Q3)
    elif manager.role == '柜面人员':
        if manager.subrole == '对公账管专员':
            reservations = reservations.filter(busi_type__in=('取现预约', '取号预约', '对公开户预约'))
        else:
            reservations = reservations.filter(busi_type__in=('取现预约', '取号预约'))

    paginator = Paginator(reservations, RESERVATION_PAGE_SIZE)
    page = max(1, min(page, paginator.num_pages))
    ret_page = -1 if page == paginator.num_pages else page
    logger.debug('%s, %s, %s, %s', reservations.count(), page, paginator.num_pages, ret_page)
    reservations = paginator.page(page)

    ret_reservations = []
    for reservation in reservations:
        data = {
            'orderno': reservation.orderno,
            'status': reservation.status,
            'apply_dtime': reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
            'busi_type': reservation.busi_type,
            'branch_name': reservation.branch.name,
            'branch_telno': reservation.branch.telno,
            'user_name': reservation.user.name,
            'user_telno': reservation.user.telno,
            'user_idcardno': reservation.user.idcardno
        }
        if reservation.handler and reservation.busi_type != '取号预约':
            data['manager_name'] = reservation.handler.name
            m_user = User.objects.get(idcardno=reservation.handler.idcardno)
            data['manager_telno'] = m_user.telno
        if reservation.deal_dtime and reservation.busi_type != '取号预约':
            data['deal_dtime'] = reservation.deal_dtime.strftime('%Y-%m-%d %H:%M:%S')
        if reservation.busi_type == 'ETC预约':
            data['plate_num'] = reservation.etcreservation.platenum
        elif reservation.busi_type == '快抵贷':
            data['orgname'] = reservation.reservationkdd.orgname
            data['house_property'] = reservation.reservationkdd.house_property
            #data['house_region'] = reservation.reservationkdd.house_region
            data['house_location'] = reservation.reservationkdd.house_location
            data['assess_price'] = int(reservation.reservationkdd.assess_price) if reservation.reservationkdd.assess_price else None
        elif reservation.busi_type == '取现预约':
            data['withdrawal_balance'] = reservation.withdrawalreservation.withdrawalnum
            data['withdrawal_dtime'] = reservation.withdrawalreservation.withdrawaltime.strftime('%Y-%m-%d %H:%M:%S')
        elif reservation.busi_type == '取号预约':
            data['taking_time'] = reservation.numbertakingreservation.taking_time.strftime('%Y-%m-%d %H:%M:%S')
        elif reservation.busi_type == '对公开户预约':
            data['user_name'] = reservation.user_name + reservation.reservationdgkh.get_gender_display()
            data['user_telno'] = reservation.user_mobile
            data['liscence'] = reservation.reservationdgkh.liscence
            data['orgname'] = reservation.reservationdgkh.orgname
            data['subtype'] = reservation.reservationdgkh.subtype
            data['due_date'] = reservation.reservationdgkh.due_date.isoformat()
            data['remark'] = reservation.reservationdgkh.remark
        ret_reservations.append(data)
    logger.debug(ret_reservations)
    return {'reservations': ret_reservations, 'page': ret_page}


def reservation_deal_submit(openid, orderno):
    reservation = Reservation.objects.get(orderno=orderno)
    if reservation.status == '已受理':
        return {'success': False, 'msg': u'该预约已经被其他人员处理'}
    handler_user = User.objects.get(openid=openid)
    now = datetime.datetime.now()
    with transaction.atomic():
        if reservation.busi_type == '贷款预约' and reservation.handler:
            res = {'success': True}
        else:
            handler = Manager.objects.get(idcardno=handler_user.idcardno)
            res_data = {
                'openid': reservation.user.openid,
                'user_name': reservation.user.name,
                'apply_dtime': reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
                'busi_type': reservation.busi_type,
                'handler_name': handler_user.name,
                'handler_mobile': handler_user.telno,
            }
            res = {'success': True, 'res_data': res_data}
            reservation.handler = handler
        reservation.status = '已受理'
        reservation.deal_dtime = now
        reservation.save()
    return res


def overtime_check(busi_type):
    now = datetime.datetime.now()
    an_hour_ago = now - datetime.timedelta(hours=1)
    reservations = Reservation.objects.filter(deal_dtime__isnull=True, busi_type=busi_type,
        apply_dtime__lte=an_hour_ago)
    logger.debug(reservations)
    reminder_list = []
    for reservation in reservations:
        if busi_type == '贷款预约' and reservation.handler:
            receivers = get_receivers(reservation.handler.bankbranch, busi_type, reservation.handler).get('users')
        else:
            receivers = get_receivers(reservation.branch, busi_type).get('users')
        logger.debug(receivers)
        res_data = {
            'user_name': reservation.user.name,
            'apply_dtime': reservation.apply_dtime.strftime('%Y-%m-%d %H:%M:%S'),
            'overtime': str(now - reservation.apply_dtime),
            'receiver': [{
                'openid': receiver.openid,
                'receiver_name': receiver.name,
            } for receiver in receivers],
        }
        if reservation.overtime_status == '未超时':
            reservation.overtime_status = '超时一阶段'
            reservation.save(update_fields=['overtime_status'])
            reminder_list.append(res_data)
        else:
            reminder_line = datetime.timedelta(hours=2, minutes=30*(reservation.stage_count+1))
            if now - reservation.apply_dtime >= reminder_line:
                reservation.stage_count += (now - reservation.apply_dtime - reminder_line).total_seconds()/1800 + 1
                if reservation.overtime_status == '超时一阶段':
                    reservation.overtime_status = '超时二阶段'
                    reservation.save(update_fields=['overtime_status', 'stage_count'])
                else:
                    reservation.save(update_fields=['stage_count'])
                reminder_list.append(res_data)
    return {'reminder_list': reminder_list}


def kdd_param():
    context = {
        'house_regions': CommonParam.objects.get(name='快抵贷房屋坐落地区').value.split('|'),
        'house_properties': CommonParam.objects.get(name='快抵贷房屋性质').value.split('|'),
    }
    return context


def kdd_search(keywords):
    del_list = ['浙江省', '浙江', '湖州市', '湖州', '南浔区', '南浔']
    communities = CommunityAssess.objects.filter(community__contains=keywords)
    #logger.debug(communities)
    if not communities:
        #logger.debug('分词')
        keyword_list = [word for word in jieba.cut(keywords)]
        final_Q = Q()
        for keyword in keyword_list:
            if keyword not in del_list:
                final_Q |= Q(community__contains=keyword)
                communities = CommunityAssess.objects.filter(final_Q)
                #logger.debug(communities.query)
    context = {
        'suggestions': [{
            'value': community.community,
            'data': int(community.price * 100),
        } for community in communities]
    }
    return context
