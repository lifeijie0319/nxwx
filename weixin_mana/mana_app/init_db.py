#-*- coding:utf-8 -*-
#外部使用Django ORM
import os
import sys
import xlrd
from django.core.wsgi import get_wsgi_application
from django.db import transaction
sys.path.append('/home/nanxun/weixin_mana')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_mana.settings")
application = get_wsgi_application()

from decimal import Decimal
from mana_app.models import Address, BankBranch, CommonParam, Coupon, Group, LotterySet,\
Manager, Menu, Region, Seller, Shop, ShopType, SignRule, Term


#读取的EXCEL格式：
#第一行是列名，数据从第二行开始
@transaction.atomic
def init_db_by_xls(model_obj, path, sheet_name='Sheet0'):
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name(sheet_name)
    headers = sheet.row_values(0)
    fields = {field.name: field.get_internal_type() for field in model_obj._meta.fields if field.name != 'id'}
    mapping = {field_name: headers.index(field_name.upper()) for field_name in fields.keys() if field_name.upper() in headers}
    values=[]
    for row in range(1, sheet.nrows):
        data = {}
        for field_name, col in mapping.items():
            cell = sheet.cell(row, col)
            final_v = cell.value
            if cell.ctype == 0:
                final_v = None
                if fields.get(field_name) == 'CharField':
                    final_v = ''
            elif cell.ctype == 2 and cell.value % 1 == 0:
                final_v = int(cell.value)
            elif cell.ctype == 3:
                final_v = xlrd.xldate.xldate_as_datetime(cell.value, 0)
                if fields.get(field_name) == 'DateField':
                    final_v = final_v.strftime('%Y-%m-%d')
            elif cell.ctype == 4:
                final_v = True if cell.value == 1 else False
            data[field_name] = final_v
        #print data
        data_obj = model_obj(**data)
        values.append(data_obj)
    model_obj.objects.bulk_create(values)
    return values


@transaction.atomic
def create_admin_manager(name, password, idcardno, telno=''):
    admin_group = Group.objects.create(name='admin')
    admin_group.menus = Menu.objects.all()
    manager = Manager(account='admin', name=name, idcardno=idcardno, telno=telno,\
        role=u'总行管理员')
    manager.set_password(password)
    manager.save()
    manager.groups.add(admin_group)
    
    
@transaction.atomic
def init_menu():
    menu_root = Menu.objects.create(name='管理菜单', level=1)
    menu_sys = Menu.objects.create(name='系统管理', level=2, parent=menu_root)
    menu_arg = Menu.objects.create(name='系统参数', level=2, parent=menu_root)
    menu_shop = Menu.objects.create(name='商户管理', level=2, parent=menu_root)
    menu_coupon = Menu.objects.create(name='优惠券管理', level=2, parent=menu_root)
    menu_reservation = Menu.objects.create(name='预约设置', level=2, parent=menu_root)
    return Menu.objects.bulk_create([
        Menu(name='用户管理', url_name='manager_page', level=3, parent=menu_sys),
        Menu(name='用户组管理', url_name='group_page', level=3, parent=menu_sys),
        Menu(name='基础参数设置', url_name='param_page', level=3, parent=menu_arg),
        Menu(name='网点录入', url_name='branch_page', level=3, parent=menu_arg),
        Menu(name='签到规则配置', url_name='signin_rule_page', level=3, parent=menu_arg),
        Menu(name='抽奖参数配置', url_name='lottery_page', level=3, parent=menu_arg),
        Menu(name='合作商户设置', url_name='shop_page', level=3, parent=menu_shop),
        Menu(name='商户提现审核', url_name='withdraw_application_page', level=3, parent=menu_shop),
        Menu(name='优惠券条件设置', url_name='coupon_term_page', level=3, parent=menu_coupon),
        Menu(name='优惠券基本设置', url_name='coupon_page', level=3, parent=menu_coupon),
        Menu(name='预约假期配置', url_name='reservation_date_page', level=3, parent=menu_reservation),
        Menu(name='预约限制次数配置', url_name='reservation_setting_page', level=3, parent=menu_reservation)
    ])


@transaction.atomic
def init_shops():
    seller_list = [
        Seller.objects.create(openid='fakeopenid1', name='星河影院老板', telno='17749775781', account='6228480031607933411'),
        Seller.objects.create(openid='fakeopenid2', name='郑南林', telno='17749775782', account='6228480031607933412'),
        Seller.objects.create(openid='fakeopenid3', name='车骑士', telno='17749775783', account='6228480031607933413'),
        Seller.objects.create(openid='fakeopenid4', name='张力威', telno='17749775784', account='6228480031607933414'),
        Seller.objects.create(openid='fakeopenid5', name='环球时代老板', telno='17749775785', account='6228480031607933415'),
        Seller.objects.create(openid='fakeopenid6', name='小龙', telno='17749775786', account='6228480031607933416'),
    ]
    address_list = [
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='嘉业路与适园路交叉口西北角新世界大厦5楼'),
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='南林路与人瑞路交叉口往南300米'),
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='浔东新村二期东南华府对面'),
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='大中路芦荡桥头'),
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='嘉业南路与向阳路交叉口，全民健身中心3号楼1楼'),
        Address.objects.create(province='浙江省', city='湖州市', county='南浔区', detail='常增路浔溪秀城门口'),
    ]
    type_movie = ShopType.objects.get(en_name='movie')
    type_car = ShopType.objects.get(en_name='car')
    type_hotel = ShopType.objects.get(en_name='hotel')
    print [type_movie, type_car, type_hotel]
    print 'SELLERS: ', seller_list
    print 'ADDRESS_LIST: ', address_list
    print [type_movie, seller_list[0].id, address_list[0].id]
    shop = Shop(name='南浔星河影院', type=type_movie, seller=seller_list[0], address=address_list[0])
    print shop
    Shop.objects.bulk_create([
        Shop(name='南浔星河影院', type=type_movie, seller=seller_list[0], address=address_list[0]),
        Shop(name='南林假日酒店', type=type_hotel, seller=seller_list[1], address=address_list[1]),
        Shop(name='车骑士', type=type_car, seller=seller_list[2], address=address_list[2]),
        Shop(name='力威之家俱乐部', type=type_car, seller=seller_list[3], address=address_list[3]),
        Shop(name='环球时代影城', type=type_movie, seller=seller_list[4], address=address_list[4]),
        Shop(name='小龙汽车养护俱乐部', type=type_car, seller=seller_list[5], address=address_list[5]),
    ])


def sync_staff(path):
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name('柜员信息')
    print sheet.cell(0,0).value
    for row in range(0, sheet.nrows):
        print sheet.cell(row, 0).value
        bank = BankBranch.objects.get(deptno=sheet.cell(row, 0).value)
        role_num = sheet.cell(row, 5).value
        print 'ROLE_NUM', role_num, type(role_num), bool(int(role_num))
        data = {
            'account': sheet.cell(row, 1).value,
            'name': sheet.cell(row, 2).value,
            'idcardno': sheet.cell(row, 3).value,
            'telno': sheet.cell(row, 4).value,
            'role': '客户经理' if int(role_num) else '柜面人员',
            'bankbranch': bank,
        }
        manager = Manager.objects.create(**data)
        manager.set_password('12345678')
        manager.save()

    
if __name__ == '__main__':
    sync_staff('doc/origin_staff.xlsx')
    #print '插入基础数据'
    #print init_db_by_xls(BankBranch, 'doc/INNER_APP_BANKBRANCH.xls')
    #print init_db_by_xls(ShopType, 'doc/INNER_APP_SHOPTYPE.xls')
    #print init_db_by_xls(Term, 'doc/INNER_APP_TERM.xls')
    #print init_db_by_xls(CommonParam, 'doc/MANA_COMMONPARAM.xls')
    #print init_db_by_xls(LotterySet, 'doc/MANA_LOTTERYSET.xls')
    #print init_db_by_xls(Region, 'doc/MANA_REGION.xls')
    #print init_db_by_xls(SignRule, 'doc/MANA_SIGNRULE.xls')
    #print '创建管理端菜单和默认管理员'
    #print init_menu()
    #print create_admin_manager('系统默认管理员', '12345678', '111111222222333333')
    #print '插入测试数据'
    #print init_db_by_xls(Coupon, 'doc/INNER_APP_COUPON.xls')
    #init_shops()
