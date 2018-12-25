#-*- coding:utf-8 -*-
#外部使用Django ORM
import datetime
import os
import sys

from django.db import connections, transaction
from django.core.wsgi import get_wsgi_application
sys.path.append('/home/nanxun/weixin_mana')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_mana.settings")
application = get_wsgi_application()

from mana_app.config import RECONCILIATION_TIME, DEFAULT_PASSWORD
from mana_app.credits_api import add_cus_term, query_cus_term, query_trade_detail2,\
    query_ods_branch, query_ods_staff, update_cus_term
from mana_app.logger import logger
from mana_app.models import BankBranch, Group, Manager, ReconciliationAmendment, ReconciliationLog, Term, TransactionDetail


cursor = connections['old_credits'].cursor()


def sync_branch():
    cur_branches = BankBranch.objects.all()
    cur_branch_deptnoes = [branch.deptno for branch in cur_branches]
    logger.debug('cur_branch_deptnoes: %s', len(cur_branch_deptnoes))
    ods_branches = query_ods_branch()
    logger.debug('ods_branches: %s', len(ods_branches))
    mapping = {}
    added_branches = []
    for branch in ods_branches:
        if branch.get('ORCABRNO') not in cur_branch_deptnoes:
            data = {
                'deptno': branch.get('ORCABRNO').strip(),
                'name': branch.get('ORCANM30').strip(),
                'address': branch.get('ORCAADDR').strip(),
                'telno': branch.get('ORCATELN').strip(),
                'level': str(int(branch.get('ORCABRLV')) - 2),
            }
            added_branches.append(BankBranch(**data))
            mapping[branch.get('ORCABRNO').strip()] = branch.get('ORCCBRNO').strip()\
                if branch.get('ORCABRLV') == '4' else branch.get('ORCFBRNO').strip()
    with transaction.atomic():
        BankBranch.objects.bulk_create(added_branches)
        for branch in added_branches:
            branch = BankBranch.objects.get(deptno=branch.deptno)
            logger.debug('ADDED_BRANCH: %s', branch.id)
            parent_deptno = mapping.get(branch.deptno)
            parent = BankBranch.objects.get(deptno=parent_deptno)
            branch.parent = parent
            branch.save()


def sync_manager():
    cur_managers = Manager.objects.all()
    cur_manager_accounts = [manager.account for manager in cur_managers]
    if Group.objects.filter(name='temp').exists():
        group = Group.objects.get(name='temp')
    else:
        group = Group.objects.create(name='temp')
    ods_staff = query_ods_staff()
    for staff in ods_staff:
        staffno = staff.get('STCASTAF').strip()
        if Manager.objects.filter(account=staffno).exists():
            manager = Manager.objects.get(account=staffno)
            if manager.bankbranch.deptno != staff.get('STCABRNO').strip():
                manager.bankbranch = BankBranch.objects.get(deptno=staff.get('STCABRNO').strip())
                manager.save()
        else:
            data = {
                'account': staffno,
                'name': staff.get('STCANM20').strip(),
                'idcardno': staff.get('STCACFNO').strip(),
                'telno': staff.get('STCATELN').strip(),
                'bankbranch': BankBranch.objects.get(deptno=staff.get('STCABRNO').strip()),
            }
            manager = Manager(**data)
            manager.set_password(DEFAULT_PASSWORD)
            manager.save()
            manager.groups.add(group)


def sync_coupon_term():
    for term in Term.objects.all():
        start_date = term.start_date.isoformat() if term.start_date else ''
        end_date = term.end_date.isoformat() if term.end_date else ''
        if query_cus_term(term.code):
            print update_cus_term(term.code, start_date, end_date, term.arg_x, term.arg_y, term.arg_z)
        else:
            print add_cus_term(term.code, term.description, start_date, end_date, term.arg_x, term.arg_y, term.arg_z)


@transaction.atomic
def reconciliation(start_date, end_date):
    now = datetime.datetime.now()
    start_datetime = datetime.datetime.strptime(start_date.strftime('%Y-%m-%d')
        + ' ' + RECONCILIATION_TIME, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_date.strftime('%Y-%m-%d')
        + ' ' + RECONCILIATION_TIME, '%Y-%m-%d %H:%M:%S')
    logger.debug('START: %s', start_datetime)
    logger.debug('END: %s', end_datetime)
    transaction_details = TransactionDetail.objects.filter(need_reconciliation=True)\
        .filter(trade_datetime__gte=start_datetime).filter(trade_datetime__lt=end_datetime)
    trade_details = query_trade_detail2(start_datetime, end_datetime)
    transaction_details_set = set([detail.orderno for detail in transaction_details])
    trade_details_set = set([detail.get('TRADE_COMM1') for detail in trade_details])
    diff_set = transaction_details_set - trade_details_set
    logger.debug('TRANSACTION: %s', transaction_details_set)
    logger.debug('TRADE_DETAIL: %s', trade_details_set)
    if not diff_set:
        ReconciliationLog.objects.create(start_datetime=start_datetime, end_datetime=end_datetime,
            opt_datetime=now)
        return {'success': True}
    else:
        reconciliation_log = ReconciliationLog.objects.create(start_datetime=start_datetime,
            end_datetime=end_datetime, opt_datetime=now, result='失败')
        diff_transaction_details = TransactionDetail.objects.filter(orderno__in=diff_set)
        for detail in diff_transaction_details:
            ReconciliationAmendment.objects.create(reconciliation_log=reconciliation_log, transaction_detail=detail)
        return {'success': False, 'diff_set': diff_set}


if __name__ == '__main__':
    sync_coupon_term()
    sync_branch()
    sync_manager()
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=1)
    result = reconciliation(start_date, end_date)
    logger.debug('RESULT: %s', result)
