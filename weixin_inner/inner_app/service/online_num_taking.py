#-*- coding:utf-8 *-
import datetime

from django.core.paginator import Paginator

from ..logger import logger
from ..models import BankBranch, CommonParam, OnlineNumberTaking, RepetitionExclude, User
from ..web_client import WsdlClient


def waitman():
    banks = BankBranch.objects.filter(is_use=True, is_map=True).order_by('deptno')
    context = {'banks': [{
        'id': bank.id,
        'name': bank.name,
        'waitman': bank.waitman,
    } for bank in banks]}
    return context


def submit(openid, branch, req_token):
    user = User.objects.get(openid=openid)
    branch = BankBranch.objects.get(id=branch)
    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    today_num = OnlineNumberTaking.objects.filter(user=user).filter(created_dtime__gte=today_start).count()
    day_limit = int(CommonParam.objects.get(name='在线取号单日提交上限').value)
    if today_num >= day_limit:
        return {'success': False, 'msg': '单日在线取号不能超过' + day_limit + '次'}
    #logger.debug('%s, %s', type(now.time()), type(datetime.time(8, 30)))
    if now.time() < datetime.time(8, 30) or now.time() > datetime.time(15, 30):
        return {'success': False, 'msg': '不在正常营业时间范围内'}
    cli = WsdlClient()
    result = cli.get_listno(branch.deptno)
    if result.get('success'):
        listno = result.get('LIST_NO')
        with transaction.atomic():
            RepetitionExclude.objects.create(req_token=req_token)
            OnlineNumberTaking.objects.create(user=user, branch=branch, listno=listno)
        return {'success': True}
    else:
        return result


def status_list(openid, st, page=1):
    user = User.objects.get(openid=openid)
    items = OnlineNumberTaking.objects.filter(user=user)
    if st == '未完成':
        items = items.filter(status__in=('等待中', '正在处理中')).order_by('-created_dtime')
    else:
        items = items.filter(status__in=('无此号码', '处理完毕', '已过期')).order_by('-created_dtime')
    paginator = Paginator(items, 5)
    page = max(1, min(page, paginator.num_pages))
    ret_page = -1 if page == paginator.num_pages else page
    items = paginator.page(page)
    items = [{
        'listno': item.listno,
        'status': item.status,
        'branch_name': item.branch.name,
        'created_dtime': item.created_dtime.strftime('%Y-%m-%d %H:%M:%S'),
    } for item in items]
    return {'items': items, 'page': ret_page}
