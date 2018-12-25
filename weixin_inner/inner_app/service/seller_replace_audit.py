#-*- coding:utf-8 -*-
from django.db import transaction
from ..models import BankBranch, Manager, Seller, Shop, SellerReplace, User


def page(openid):
    def get_replacement_dict(replacements):
        return [{
            'id': replacement.id,
            'apply_datetime': replacement.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'shop_name': replacement.shop.name,
            'shop_address': replacement.shop.address.get_str(),
            'seller_name': replacement.shop.seller.name,
            'seller_old_telno': replacement.shop.seller.telno,
            'seller_new_telno': replacement.telno,
            'status': replacement.get_status(),
        } for replacement in replacements]
    user = User.objects.get(openid=openid)
    manager = Manager.objects.get(idcardno=user.idcardno)
    if manager.role == u'总行管理员':
        apply_uncompleted = get_replacement_dict(SellerReplace.objects.filter(status__in=[u'待审核', u'总行复核']))
        apply_completed = get_replacement_dict(SellerReplace.objects\
            .filter(status__in=(u'分配给支行', u'分配给客户经理', u'通过', u'驳回')))
        allocation = [{
            'id': bankbranch.id,
            'name': bankbranch.name,
        } for bankbranch in BankBranch.objects.filter(level__in=['2', '3']).order_by('deptno')]
    elif manager.role == u'支行管理员':
        bankbranch = manager.bankbranch
        apply_uncompleted = get_replacement_dict(SellerReplace.objects.filter(bankbranch=bankbranch).filter(status=u'分配给支行'))
        apply_completed = get_replacement_dict(SellerReplace.objects.filter(bankbranch=bankbranch)\
            .filter(status__in=(u'分配给客户经理', u'通过', u'驳回')))
        client_managers = Manager.objects.filter(bankbranch=bankbranch).filter(role='客户经理', status='normal')
        allocation = [{
            'id': client_manager.id,
            'name': client_manager.name,
        } for client_manager in client_managers]
    elif manager.role == u'客户经理':
        bankbranch = manager.bankbranch
        apply_uncompleted = get_replacement_dict(SellerReplace.objects\
            .filter(bankbranch=bankbranch).filter(status=u'分配给客户经理').filter(client_manager=manager))
        apply_completed = get_replacement_dict(SellerReplace.objects.filter(bankbranch=bankbranch)\
            .filter(status__in=(u'通过', u'驳回')))
        allocation = []
    else:
        return {'success': False, 'msg': u'没有匹配的角色'}
    context = {
        'success': True,
        'apply_uncompleted': apply_uncompleted,
        'apply_completed': apply_completed,
        'allocation': allocation,
        'role': manager.role,
    }
    return context


@transaction.atomic
def head_admin(apply_id, branch_id):
    bankbranch = BankBranch.objects.get(id=branch_id)
    replacement = SellerReplace.objects.get(id=apply_id)
    if replacement.status != u'待审核':
        return {'success': False, 'msg': '该申请已经被其他总行管理员处理，请勿重复操作'}

    branch_admins = Manager.objects.filter(role=u'支行管理员').filter(bankbranch=bankbranch, status='normal')
    branch_admins_openid = []
    for branch_admin in branch_admins:
        branch_admin_user = User.objects.filter(idcardno=branch_admin.idcardno)
        if len(branch_admin_user) == 1:
            branch_admins_openid.append(branch_admin_user.first().openid)
    if not branch_admins_openid:
        return {'success': False, 'msg': bankbranch.name + '不存在可以处理请求的支行管理员'}

    replacement.bankbranch = bankbranch
    replacement.status = u'分配给支行'
    replacement.save()
    data = {
        'name': replacement.shop.seller.name,
        'info': '申请更换店铺' + replacement.shop.name + '绑定的微信号',
        'apply_datetime': replacement.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }   
    return {'success': True, 'branch_admins_openid': branch_admins_openid, 'data': data}


@transaction.atomic
def branch_admin(apply_id, client_manager_id):
    client_manager = Manager.objects.get(id=client_manager_id)
    replacement = SellerReplace.objects.get(id=apply_id)
    if replacement.status != u'分配给支行':
        return {'success': False, 'msg': '该申请已经被本支行其它管理员处理，请勿重复操作'}

    if not User.objects.filter(idcardno=client_manager.idcardno).exists():
        return {'success': False, 'msg': '该客户经理没有注册公众号，无法向其发送消息'}
    client_manager_openid = User.objects.get(idcardno=client_manager.idcardno).openid
    data = { 
        'name': replacement.shop.seller.name,
        'info': '申请更换店铺' + replacement.shop.name + '绑定的微信号',
        'apply_datetime': replacement.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }

    replacement.client_manager = client_manager
    replacement.status = u'分配给客户经理'
    replacement.save()
    return {'success': True, 'client_manager_openid': (client_manager_openid,), 'data': data} 


@transaction.atomic
def client_manager(apply_id, operation):
    replacement = SellerReplace.objects.get(id=apply_id)
    if replacement.status != u'分配给客户经理':
        return {'success': False, 'msg': '该申请已经被本支行其它客户经理处理，请勿重复操作'}
    if operation == u'pass':
        head_admins = Manager.objects.filter(role=u'总行管理员', status='normal')
        head_admins_openid = []
        for head_admin in head_admins:
            head_admin_user = User.objects.filter(idcardno=head_admin.idcardno)
            if len(head_admin_user) == 1:
                head_admins_openid.append(head_admin_user.first().openid)
        if not head_admins_openid:
            return {'success': False, 'msg': '不存在可以处理请求的总行管理员'}
        replacement.status = u'总行复核'
        replacement.save()
        data = {
            'name': replacement.shop.seller.name,
            'info': '申请更换店铺' + replacement.shop.name + '绑定的微信号',
            'apply_datetime': replacement.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return {'success': True, 'head_admins_openid': head_admins_openid, 'data': data}
    else:
        replacement.status = u'驳回'
        replacement.save()
    return {'success': True}


@transaction.atomic
def recheck(apply_id, operation):
    replacement = SellerReplace.objects.get(id=apply_id)
    if replacement.status != u'总行复核':
        return {'success': False, 'msg': '该申请已经被其它总行管理员处理，请勿重复操作'}
    if operation == u'pass':
        replacement.status = u'通过'
        replacement.save()
        seller = replacement.shop.seller
        seller.openid = replacement.openid
        if replacement.telno:
            seller.telno = replacement.telno
        seller.save()
    else:
        replacement.status = u'驳回'
        replacement.save()
    return {'success': True}
