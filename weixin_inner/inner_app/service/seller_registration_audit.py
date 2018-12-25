#-*- coding:utf-8 -*-
from django.db import transaction
from ..models import BankBranch, Manager, Seller, Shop, SellerRegister, User


def page(openid):
    def get_registration_dict(registrations):
        return [{
            'id': registration.id,
            'apply_datetime': registration.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'name': registration.name,
            'accountno': registration.accountno,
            'telno': registration.telno,
            'shop_name': registration.shop_name,
            'shop_type': registration.shop_type.name,
            'shop_address': registration.shop_address.get_str(),
            'status': registration.get_status(),
        } for registration in registrations]
    user = User.objects.get(openid=openid)
    manager = Manager.objects.get(idcardno=user.idcardno)
    if manager.role == u'总行管理员':
        apply_uncompleted = get_registration_dict(SellerRegister.objects.filter(status=u'待审核'))
        apply_completed = get_registration_dict(SellerRegister.objects\
            .filter(status__in=(u'分配给支行', u'分配给客户经理', u'通过', u'驳回')))
        allocation = [{
            'id': bankbranch.id,
            'name': bankbranch.name,
        } for bankbranch in BankBranch.objects.filter(level__in=['2', '3']).order_by('deptno')]
    elif manager.role == u'支行管理员':
        bankbranch = manager.bankbranch
        apply_uncompleted = get_registration_dict(SellerRegister.objects.filter(bankbranch=bankbranch).filter(status=u'分配给支行'))
        apply_completed = get_registration_dict(SellerRegister.objects.filter(bankbranch=bankbranch)\
            .filter(status__in=(u'分配给客户经理', u'通过', u'驳回')))
        client_managers = Manager.objects.filter(bankbranch=bankbranch).filter(role='客户经理', status='normal')
        allocation = [{
            'id': client_manager.id,
            'name': client_manager.name,
        } for client_manager in client_managers]
    elif manager.role == u'客户经理':
        bankbranch = manager.bankbranch
        apply_uncompleted = get_registration_dict(SellerRegister.objects\
            .filter(bankbranch=bankbranch).filter(status=u'分配给客户经理').filter(client_manager=manager))
        apply_completed = get_registration_dict(SellerRegister.objects.filter(bankbranch=bankbranch)\
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
    registration = SellerRegister.objects.get(id=apply_id)
    if registration.status != u'待审核':
        return {'success': False, 'msg': '该申请已经被其他总行管理员处理，请勿重复操作'}

    branch_admins = Manager.objects.filter(role=u'支行管理员').filter(bankbranch=bankbranch, status='normal')
    branch_admins_openid = []
    for branch_admin in branch_admins:
        branch_admin_user = User.objects.filter(idcardno=branch_admin.idcardno)
        if len(branch_admin_user) == 1:
            branch_admins_openid.append(branch_admin_user.first().openid)
    if not branch_admins_openid:
        return {'success': False, 'msg': bankbranch.name + '不存在可以处理请求的支行管理员'}

    registration.bankbranch = bankbranch
    registration.status = u'分配给支行'
    registration.save()
    data = {
        'name': registration.name,
        'info': u'在' + registration.shop_address.get_str() + u'开一家' + registration.shop_name,
        'apply_datetime': registration.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }   
    return {'success': True, 'branch_admins_openid': branch_admins_openid, 'data': data}


@transaction.atomic
def branch_admin(apply_id, client_manager_id):
    client_manager = Manager.objects.get(id=client_manager_id)
    registration = SellerRegister.objects.get(id=apply_id)
    if registration.status != u'分配给支行':
        return {'success': False, 'msg': '该申请已经被本支行其它管理员处理，请勿重复操作'}

    if not User.objects.filter(idcardno=client_manager.idcardno).exists():
        return {'success': False, 'msg': '该客户经理没有注册公众号，无法向其发送消息'}
    client_manager_openid = User.objects.get(idcardno=client_manager.idcardno).openid
    data = { 
        'name': registration.name,
        'info': u'在' + registration.shop_address.get_str() + u'开一家' + registration.shop_name,
        'apply_datetime': registration.apply_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    }   

    registration.client_manager = client_manager
    registration.status = u'分配给客户经理'
    registration.save()
    return {'success': True, 'client_manager_openid': (client_manager_openid,), 'data': data} 


@transaction.atomic
def client_manager(openid, apply_id, operation):
    registration = SellerRegister.objects.get(id=apply_id)
    if registration.status != u'分配给客户经理':
        return {'success': False, 'msg': '该申请已经被本支行其它客户经理处理，请勿重复操作'}
    if operation == u'pass':
        registration.status = u'通过'
        seller_data = {
            'openid': registration.openid,
            'name': registration.name,
            'telno': registration.telno,
            'account': registration.accountno,
        }
        seller = Seller.objects.create(**seller_data)
        user = User.objects.get(openid=openid)
        manager = Manager.objects.get(idcardno=user.idcardno)
        shop_data = {
            'name': registration.shop_name,
            'type': registration.shop_type,
            'seller': seller,
            'address': registration.shop_address,
            'bank': manager.bankbranch,
        }
        shop = Shop.objects.create(**shop_data)
    else:
        registration.status = u'驳回'
    registration.save()
    return {'success': True}
