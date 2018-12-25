# -*- coding:utf-8 -*-
import datetime

from django.db import transaction
from django.shortcuts import render

from .common import add_trade_detail, credits_usable, query_credits,\
transaction_detail_save, update_or_insert_credits
from ..logger import logger
from ..models import CommonParam, LotterySet, LotteryRecord, RepetitionExclude, User,Coupon,UserCoupon,CouponSend,CouponAward,CouponRule,BusiType,LotteryRule
from ..tools import generate_orderno, to_json, weight_choice


# 返回页面
def lottery_page(openid):
    credits = query_credits(openid, 'user')
    lottery_cost = CommonParam.objects.get(name=u'抽奖成本积分').value
    desc = LotteryRule.objects.all().order_by('value')
    data = []
    for i in desc:
        data.append(str(i.value)+'.'+i.text)
    return {'credits': credits, 'cost': lottery_cost,'desc':data}

#发放优惠卷
def add_coupon(openid,coupon_id,num,req_token):
    now = datetime.datetime.now()
    user = User.objects.get(openid=openid)
    coupon = Coupon.objects.get(id=coupon_id)
    num = int(num)
    with transaction.atomic():
        orderno = generate_orderno(1)[0]
        coupon.soldnum += num
        coupon.leftnum -= num
        coupon.save()
        log = transaction_detail_save(user, None, 0, '抽奖奖励优惠卷', str(num) + '张' + coupon.name, orderno)
        for i in range(0, num):
            user_coupon = UserCoupon(user=user, coupon=coupon, status='未使用', in_log=log)
            user_coupon.save()
            coupon_award = CouponAward(user_coupon = user_coupon,time=now)
            coupon_award.save()
        return coupon_award.id

#检验中奖次数
def check_num(openid,awards):
    '''
    如果中奖次数达到上限，则去除获取该奖励的可能性
    '''
    now = datetime.datetime.now()
    couponrule = CouponRule.objects.all()
    busitype = BusiType.objects.all()
    for busi in busitype:
        unin = couponrule.filter(busitype__id=busi.id)
        b_time = busi.l_time
        b_time = datetime.timedelta(seconds=b_time)
        b_num = busi.l_num
        for i in unin:
            recodes = LotteryRecord.objects.filter(user__openid=openid,created_datetime__gt=(now-b_time),type='优惠券',credits=i.coupon.id)
            if recodes.count()>=b_num:
                for j in unin:
                    awards= awards.exclude(credits=j.coupon.id,type='优惠券')
    for rule in couponrule:
        r_time = rule.l_time
        r_time = datetime.timedelta(seconds=r_time)
        r_num = rule.l_num
        recodes = LotteryRecord.objects.filter(user__openid=openid,created_datetime__gt=(now-r_time),type='优惠券',credits=rule.coupon.id)
        if recodes.count()>=r_num:
            awards= awards.exclude(credits=rule.coupon.id,type='优惠券')
    return awards


# 点击按钮后执行此路由，并将结果与数据存入数据库，并返回success。
def lottery_submit(openid, req_token):
    now = datetime.datetime.now()
    lottery_cost = int(CommonParam.objects.get(name=u'抽奖成本积分').value)
    user = User.objects.get(openid=openid)
    user_initial_credits = query_credits(openid, 'user')

    if user.is_new:
        return {'success': False, 'msg': u'您尚未绑定，无法抽奖, 请到个人信息页面绑定'}
    if user_initial_credits < lottery_cost:
        return {'success': False, 'msg': u'您的积分不足，无法参与抽奖'}
    if not credits_usable():
        return {'success': False, u'msg': u'积分维护中，请稍后再试'}
    awards = LotterySet.objects.all()
    awards = check_num(openid,awards)
    weight_list = [award.pro for award in awards]
    logger.debug('WEIGHT_LIST: %s', weight_list)
    award_index = weight_choice(weight_list)
    award = awards[award_index]
    logger.debug('AWARD: %s', award)
    award_json = {
        'index': award_index,
        'id': award.id,
        'dec': award.dec,
    }

    award_type = award.type
    if award_type == '积分':
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            orderno_list = generate_orderno(2)
            user.credits = user.credits - lottery_cost + award.credits
            user.save()
            transaction_detail_save(user, None, -lottery_cost, u'抽奖', u'扣除积分作为抽奖成本', orderno_list[0])
            transaction_detail_save(user, None, award.credits, u'中奖', u'中奖获得积分', orderno_list[1])
            LotteryRecord.objects.create(user=user, description=award.dec, type=award.type,\
                credits=award.credits, created_datetime=now)
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, award.credits - lottery_cost)
            add_trade_detail(u'抽奖', user.idcardno, user.name, lottery_cost, '-',\
                user_initial_credits - lottery_cost, orderno_list[0])
            add_trade_detail(u'中奖', user.idcardno, user.name,  award.credits, '+',\
                user_initial_credits - lottery_cost + award.credits, orderno_list[1])
    #当中奖结果不为积分时，中奖奖品会不同：
    #结果为优惠卷时
    elif award_type == '优惠券':
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            orderno = generate_orderno(1)[0]
            user.credits = user.credits - lottery_cost 
            user.save()
            transaction_detail_save(user,None, -lottery_cost,u'抽奖',u'扣除积分作为抽奖成本',orderno)
            #给用户添加优惠卷，根据优惠卷信息进行绑定
            user_coupon_id = add_coupon(openid,award.credits,1,req_token)
            LotteryRecord.objects.create(user=user,description= award.dec,type=award.type,\
                credits=award.credits, created_datetime=now,user_coupon_id =user_coupon_id,status='已发放')

        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno,award.credits - lottery_cost)
            add_trade_detail(u'抽奖',user.idcardno, user.name, lottery_cost,'-',\
                user_initial_credits - lottery_cost,orderno)
    else:
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            LotteryRecord.objects.create(user=user, description=award.dec, type=award.type,\
                credits=award.credits, created_datetime=now)
            orderno = generate_orderno(1)[0]
            user.credits -= lottery_cost
            user.save()
            transaction_detail_save(user, None, -lottery_cost, u'抽奖', u'扣除积分作为抽奖成本', orderno)
        with transaction.atomic(using='old_credits'):
            update_or_insert_credits(user.idcardno, -lottery_cost)
            add_trade_detail(u'抽奖', user.idcardno, user.name, lottery_cost, '-',\
                query_credits(openid, 'user'), orderno)
    return {'success': True, 'award': award_json, 'credits':query_credits(openid, 'user')}


def lottery_set(openid):
    awards = LotterySet.objects.exclude(pro=0).order_by('id')
    ret_awards = [{'dec': award.dec} for award in awards]
    return {'awards': ret_awards}


# 点击抽奖记录后通过此路由返回抽奖结果。
def lottery_detail(openid):
    lottery_record = LotteryRecord.objects.filter(user__openid=openid).filter(type__in = ('实物','优惠券')).order_by('-id')
    lottery_record_json = [{
        'description': record.description,
        'type': record.type,
        'credits': record.credits,
        'created_datetime': record.created_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'status': record.status,
    } for record in lottery_record]
    return {'lottery_records': lottery_record_json}
