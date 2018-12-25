# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.db import models


class ExtInfo(models.Model):
    name = models.CharField(max_length=32, help_text='扩展信息名称')
    value = models.CharField(max_length=255, help_text='扩展信息内容')
    remark = models.CharField(max_length=255, help_text='扩展信息备注')

    class Meta:
        abstract = True


class Menu(models.Model):
    name = models.CharField(max_length=24)
    url_name = models.CharField(max_length=48, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    level = models.IntegerField()

    def __str__(self):
        return str(self.level) + self.name

    class Meta:
        db_table = 'MANA_MENU'


class Group(models.Model):
    name = models.CharField(max_length=24, unique=True)
    menus = models.ManyToManyField(Menu, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'MANA_GROUP'


class Manager(models.Model):
    ROLES = (
        (u'总行管理员', u'总行管理员'),
        (u'支行管理员', u'支行管理员'),
        (u'客户经理', u'客户经理'),
        (u'柜面人员', u'柜面人员'),
    )
    STATUS = (
        ('normal', '正常'),
        ('resigned', '离职'),
    )
    account = models.CharField(max_length=18, unique=True)
    name = models.CharField(max_length=24, blank=True)
    password = models.CharField(max_length=128)
    idcardno = models.CharField(max_length=18, unique=True)
    telno = models.CharField(max_length=12, blank=True)
    role = models.CharField(max_length=24, blank=True, choices=ROLES)
    subrole = models.CharField(max_length=24, blank=True, default='')
    bankbranch = models.ForeignKey('BankBranch', null=True, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    status = models.CharField(max_length=24, choices=STATUS, default='normal')

    def __str__(self):
        return self.role + ':' + self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'MANA_MANAGER'


class LogInfo(models.Model):
    OPERATIONS = (
        (u'add', u'增'),
        (u'delete', u'删'),
        (u'update', u'改'),
    )
    opt_datetime = models.DateTimeField()
    operator = models.ForeignKey(Manager)
    model = models.CharField(max_length=32)
    operation = models.CharField(max_length=8, choices=OPERATIONS)
    related_id = models.IntegerField()
    info = models.TextField()

    class Meta:
        db_table = 'MANA_LOGINFO'

    def __str__(self):
        return self.info


class CommonParam(models.Model):
    name = models.CharField(max_length=48, unique=True)
    value = models.CharField(max_length=16)
    remark = models.TextField(default=u'没有备注信息')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'MANA_COMMONPARAM'


class Region(models.Model):
    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=48)
    level = models.CharField(max_length=24)
    parent = models.CharField(max_length=12)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'MANA_REGION'


class SignRule(models.Model):
    day = models.IntegerField(unique=True)
    credits = models.IntegerField(default=0)
    dec = models.TextField(default='')

    def __str__(self):
        return self.dec

    class Meta:
        db_table = 'MANA_SIGNRULE'


class LotterySet(models.Model):
    AWARD_TYPES = (
        ('积分', '积分'),
        ('实物', '实物'),
        ('谢谢参与', '谢谢参与'),
        ('优惠券', '优惠券'),
    )
    dec = models.CharField(max_length=32, unique=True)
    credits = models.IntegerField(default=0)
    type = models.CharField(max_length=32, choices=AWARD_TYPES)
    pro = models.IntegerField(default=0)

    def __str__(self):
        return self.dec

    class Meta:
        db_table = 'MANA_LOTTERYSET'


class ReservationForbidenDate(models.Model):
    date = models.DateField()
    dec = models.TextField(default='')
    manager = models.ForeignKey(Manager, default=1)

    class Meta:
        db_table = 'MANA_RESERVATIONFORBIDENDATE'


class ReconciliationLog(models.Model):
    RESULTS = (
        ('成功', '成功'),
        ('失败', '失败'),
        ('失败但已补录', '失败但已补录'),
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    opt_datetime = models.DateTimeField()
    result = models.CharField(max_length=32, choices=RESULTS, default='成功')

    def __str__(self):
        return self.opt_datetime.strftime('%Y-%m-%d %H:%M:%S:') + '核对' + self.start_datetime.strftime(
            '%Y-%m-%d %H:%M:%S') \
               + '到' + self.end_datetime.strftime('%Y-%m-%d %H:%M:%S') + '之间的账目，结果：' + self.result

    class Meta:
        db_table = 'MANA_RECONCILIATION_LOG'


class ReconciliationAmendment(models.Model):
    AMENDSTATUS = (
        ('未补录', '未补录'),
        ('自动补录', '自动补录'),
        ('手动补录', '手动补录'),
    )
    reconciliation_log = models.ForeignKey(ReconciliationLog)
    transaction_detail = models.ForeignKey('TransactionDetail')
    status = models.CharField(max_length=32, choices=AMENDSTATUS, default='未补录')
    manager = models.ForeignKey(Manager, null=True, blank=True)
    amend_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '交易' + self.transaction_detail.orderno + self.status

    class Meta:
        db_table = 'MANA_RECONCILIATION_AMENDMENT'


class CarouselFigure(models.Model):
    name = models.CharField(max_length=24, unique=True)
    description = models.CharField(max_length=96, unique=True)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'MANA_CAROUSEL_FIGURE'


# 应用端
class Term(models.Model):
    code = models.CharField(max_length=16, unique=True)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    arg_x = models.CharField(max_length=8, blank=True)
    arg_y = models.CharField(max_length=8, blank=True)
    arg_z = models.CharField(max_length=8, blank=True)

    def __str__(self):
        res = self.description
        if self.start_date:
            res = res.replace('START_DATE', self.start_date.isoformat())
        if self.end_date:
            res = res.replace('END_DATE', self.end_date.isoformat())
        res = res.replace('X', self.arg_x).replace('Y', self.arg_y).replace('Z', self.arg_z)
        return res

    def get_str(self):
        return self.__str__()

    class Meta:
        db_table = 'INNER_APP_TERM'


class Address(models.Model):
    province = models.CharField(max_length=30, default=u'浙江省')
    city = models.CharField(max_length=48)
    county = models.CharField(max_length=48)
    town = models.CharField(max_length=48, blank=True)
    village = models.CharField(max_length=48, blank=True)
    detail = models.CharField(max_length=96, blank=True)

    def __str__(self):
        address_parts = [self.city, self.county, self.town, self.village, self.detail]
        ret_address = ''.join([part for part in address_parts if part])
        return ret_address

    def get_str(self):
        return self.__str__()

    class Meta:
        db_table = 'INNER_APP_ADDRESS'


class Person(models.Model):
    openid = models.CharField(max_length=32)
    name = models.CharField(max_length=48)
    telno = models.CharField(max_length=12, default='000000000000')
    credits = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_PERSON'


class User(Person):
    idcardno = models.CharField(max_length=18, unique=True)
    paypasswd = models.CharField(max_length=128, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    is_new = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.paypasswd = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.paypasswd)

    class Meta:
        db_table = 'INNER_APP_USER'


class Seller(Person):
    account = models.CharField(max_length=24)
    tellerno = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_SELLER'


class BankBranch(models.Model):
    LEVELS = (
        ('1', '总行'),
        ('2', '支行'),
        ('3', '支行网点'),
    )
    deptno = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=96)
    address = models.TextField()
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, default=0)
    country = models.CharField(max_length=20, default=u'其他地区')
    telno = models.CharField(max_length=20, blank=True)
    officehours = models.CharField(max_length=30, blank=True, default='8:00-17:00')
    waitman = models.IntegerField(default=0)
    is_map = models.BooleanField(default=True)
    is_use = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    level = models.CharField(max_length=1, choices=LEVELS, default='3')
    is_withdrawal = models.BooleanField(default=True)
    is_oppen_account = models.BooleanField(default=True)
    is_etc = models.BooleanField(default=True)
    is_loan = models.BooleanField(default=True)
    is_num_taking = models.BooleanField(default=True)
    is_dgkh = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_BANKBRANCH'


class SignData(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField()
    credits = models.IntegerField()

    def __str__(self):
        return self.datetime.strftime('%Y-%m-%d') + ':' + self.user.name + u'签到获得' + str(self.credits) + u'积分'

    class Meta:
        db_table = 'INNER_APP_SIGNDATA'


class SignRecord(models.Model):
    user = models.ForeignKey(User)
    month = models.IntegerField()
    num = models.IntegerField()

    def __str__(self):
        return self.user.name + str(self.month) + u'月累计签到' + str(self.num) + u'次'

    class Meta:
        db_table = 'INNER_APP_SIGNRECORD'


class LotteryRecord(models.Model):
    AWARD_TYPES = (
        ('积分', '积分'),
        ('实物', '实物'),
        ('优惠券', '优惠券'),
        ('谢谢参与', '谢谢参与'),
    )
    STATUS = (
        ('未发放', '未发放'),
        ('已发放', '已发放'),
    )
    user = models.ForeignKey(User)
    description = models.CharField(max_length=32)
    type = models.CharField(max_length=16, default='积分', choices=AWARD_TYPES)
    credits = models.IntegerField()
    created_datetime = models.DateTimeField()
    status = models.CharField(max_length=16, default='未发放', choices=STATUS)
    sent_datetime = models.DateTimeField(null=True, blank=True)
    sent_manager = models.ForeignKey(Manager, null=True, blank=True)
    user_coupon_id = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.user.name + ':' + self.description + ':' + self.created_datetime.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        db_table = 'INNER_APP_LOTTERYLOG'


class ShopType(models.Model):
    name = models.CharField(max_length=12)
    en_name = models.CharField(max_length=12)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_SHOPTYPE'


class Shop(models.Model):
    STATUS = (
        (u'正常', u'正常'),
        (u'停用', u'停用'),
    )
    name = models.CharField(max_length=48, unique=True)
    type = models.ForeignKey(ShopType)
    seller = models.ForeignKey(Seller)
    address = models.ForeignKey(Address)
    bank = models.ForeignKey(BankBranch, null=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    trade_times = models.IntegerField(default=0)
    stick = models.BooleanField(default=False)
    status = models.CharField(max_length=6, default='正常')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_SHOP'


class SellerRegister(models.Model):
    STATUS = (
        (u'待审核', u'待审核'),
        (u'分配给支行', u'分配给支行'),
        (u'分配给客户经理', u'分配给客户经理'),
        (u'通过', u'通过'),
        (u'驳回', u'驳回'),
    )
    openid = models.CharField(max_length=32)
    name = models.CharField(max_length=24)
    telno = models.CharField(max_length=12, blank=True)
    accountno = models.CharField(max_length=24)
    tellerno = models.CharField(max_length=8, blank=True)
    shop_name = models.CharField(max_length=48)
    shop_type = models.ForeignKey(ShopType)
    shop_address = models.ForeignKey(Address)
    apply_datetime = models.DateTimeField()
    status = models.CharField(max_length=24, choices=STATUS)
    bankbranch = models.ForeignKey(BankBranch, null=True, blank=True)
    client_manager = models.ForeignKey(Manager, null=True, blank=True)

    def get_status(self):
        if self.status == u'分配给支行':
            status = u'分配给支行: ' + self.bankbranch.name
        elif self.status == u'分配给客户经理':
            status = u'分配给客户经理: ' + self.client_manager.name
        else:
            status = self.status
        return status

    class Meta:
        db_table = 'INNER_APP_SELLERREGISTER'


class SellerReplace(models.Model):
    STATUS = (
        (u'待审核', u'待审核'),
        (u'分配给支行', u'分配给支行'),
        (u'分配给客户经理', u'分配给客户经理'),
        (u'总行复核', u'总行复核'),
        (u'通过', u'通过'),
        (u'驳回', u'驳回'),
    )
    apply_datetime = models.DateTimeField(auto_now_add=True)
    bankbranch = models.ForeignKey(BankBranch, null=True, blank=True)
    client_manager = models.ForeignKey(Manager, null=True, blank=True)
    openid = models.CharField(max_length=32)
    shop = models.ForeignKey(Shop)
    status = models.CharField(max_length=24, choices=STATUS, default='待审核')
    telno = models.CharField(max_length=12, blank=True)

    def __str__(self):
        return '商户' + self.shop.name + '(经营者' + self.shop.seller.name + ')申请更换微信号'

    def get_status(self):
        if self.status == u'分配给支行':
            status = u'分配给支行: ' + self.bankbranch.name
        elif self.status == u'分配给客户经理':
            status = u'分配给客户经理: ' + self.client_manager.name
        else:
            status = self.status
        return status

    class Meta:
        db_table = 'INNER_APP_SELLERREPLACE'


class Coupon(models.Model):
    RELATIONS = (
        (u'and', u'与'),
        (u'or', u'或'),
    )
    DISCOUNT_TYPES = (
        (u'满减', u'满减'),
        (u'抵用', u'抵用'),
    )
    name = models.CharField(max_length=48)
    description = models.TextField()
    credits = models.IntegerField(default=0)
    discount_type = models.CharField(max_length=12, choices=DISCOUNT_TYPES)
    discount_startline = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    fixed_amount = models.IntegerField(default=0)
    on_date = models.DateField()
    off_date = models.DateField()
    expired_date = models.DateField()
    limit = models.IntegerField(default=0)
    busi_type = models.CharField(max_length=24, blank=True, default='')
    soldnum = models.IntegerField(default=0)
    leftnum = models.IntegerField(default=0)
    shops = models.ManyToManyField(Shop, blank=True)
    term1 = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_set1')
    term2 = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_set2')
    term_relation = models.CharField(max_length=4, choices=RELATIONS, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'INNER_APP_COUPON'


class ReservationNum(models.Model):
    num = models.IntegerField(default=0)
    second = models.IntegerField(default=0)
    day = models.IntegerField(default=0)
    month = models.IntegerField(default=0)
    hour = models.IntegerField(default=0)
    mintue = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    manager = models.ForeignKey(Manager, default=0)
    dec = models.TextField(default='')

    def _str__(self):
        return self.id

    class Meta:
        db_table = 'INNER_APP_RESERVATIONNUM'


class Reservation(models.Model):
    TYPES = (
        ('ETC预约', 'ETC预约'),
        ('贷款预约', '贷款预约'),
        ('快抵贷', '快抵贷'),
        ('取号预约', '取号预约'),
        ('开户预约', '开户预约'),
        ('取现预约', '取现预约'),
        ('对公开户预约', '对公开户预约'),
    )
    STATUSES = (
        ('未受理', '未受理'),
        ('已受理', '已受理'),
    )
    OVERTIME_STATUSES = (
        ('未超时', '未超时'),
        ('超时一阶段', '超时一阶段'),
        ('超时二阶段', '超时二阶段'),
    )
    user_name = models.CharField(max_length=32)
    user_mobile = models.CharField(max_length=20)
    apply_dtime = models.DateTimeField(auto_now_add=True)
    busi_type = models.CharField(max_length=32, choices=TYPES)
    status = models.CharField(max_length=32, default=u'未受理', choices=STATUSES)
    orderno = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(User)
    branch = models.ForeignKey(BankBranch)
    handler = models.ForeignKey(Manager, null=True, blank=True)
    deal_dtime = models.DateTimeField(null=True, blank=True)
    overtime_status = models.CharField(max_length=32, default=u'未超时', choices=OVERTIME_STATUSES)
    stage_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.name + self.busi_type + self.apply_dtime.isoformat() + self.status

    class Meta:
        db_table = 'INNER_APP_RESERVATION'


class NumberTakingReservation(Reservation):
    taking_number = models.CharField(max_length=32, default='0')
    taking_time = models.DateTimeField()

    class Meta:
        db_table = 'INNER_APP_NUMBERTAKINGRESERVATION'


class OpenAccountReservation(Reservation):
    limit = models.CharField(max_length=32, default='0')

    class Meta:
        db_table = 'INNER_APP_OPENACCOUNTRESERVATION'


class ETCReservation(Reservation):
    platenum = models.CharField(max_length=32)

    class Meta:
        db_table = 'INNER_APP_ETCRESERVATION'


class LoanReservation(Reservation):
    loannum = models.CharField(max_length=32)

    class Meta:
        db_table = 'INNER_APP_LOANRESERVATION'


class ReservationKDD(Reservation):
    HOUSE_PROPERTIES = (
        ('住宅', '住宅'),
        ('商铺', '商铺'),
        ('写字楼', '写字楼'),
        ('厂房', '厂房'),
    )
    HOUSE_REGIONS = (
        ('湖州市区', '湖州市区'),
        ('南浔区', '南浔区'),
        ('杭州市主城区', '杭州市主城区'),
        ('临安区', '临安区'),
        ('富阳区', '富阳区'),
        ('其他地区', '其他地区'),
    )
    orgname = models.CharField(max_length=64)
    house_property = models.CharField(max_length=24, choices=HOUSE_PROPERTIES)
    house_region = models.CharField(max_length=24, choices=HOUSE_REGIONS)
    house_location = models.CharField(max_length=128, blank=True, default='')
    house_area = models.IntegerField(null=True, blank=True)
    assess_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_villa = models.BooleanField(default=False)

    class Meta:
        db_table = 'RESERVATION_KDD'


class ReservationDGKH(Reservation):
    GENDERS = (
        ('male', '先生'),
        ('female', '女士'),
    )
    SUBTYPES = (
        ('开户', '开户'),
        ('网银', '网银'),
        ('短信签约', '短信签约'),
    )
    gender = models.CharField(max_length=12, choices=GENDERS, default='male')
    liscence = models.CharField(max_length=18, unique=True)
    orgname = models.CharField(max_length=64)
    subtype = models.CharField(max_length=24, choices=SUBTYPES)
    due_date = models.DateField()
    remark = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = 'RESERVATION_DGKH'


class WithdrawalReservation(Reservation):
    withdrawalnum = models.CharField(max_length=32)
    withdrawaltime = models.DateTimeField()

    class Meta:
        db_table = 'INNER_APP_WITHDRAWALRESERVATION'


class OnlineNumberTaking(models.Model):
    STATUSES = (
        ('无此号码', '无此号码'),
        ('等待中', '等待中'),
        ('正在处理中', '正在处理中'),
        ('处理完毕', '处理完毕'),
        ('已过期', '已过期'),
    )
    user = models.ForeignKey(User)
    status = models.CharField(max_length=32, default='等待中', choices=STATUSES)
    branch = models.ForeignKey(BankBranch)
    listno = models.CharField(max_length=8)
    created_dtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'INNER_APP_ONLINENUMBERTAKING'


class WithdrawAppplication(models.Model):
    WITHDRAW_STATUS = (
        ('待审批', '待审批'),
        ('已审批', '已审批'),
        ('未通过', '未通过'),
    )
    seller = models.ForeignKey(Seller)
    credits = models.IntegerField(default=0)
    poundage = models.DecimalField(max_digits=5, decimal_places=4)
    ratio = models.IntegerField(default=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    receipt_provision = models.BooleanField(default=False)
    status = models.CharField(max_length=24, choices=WITHDRAW_STATUS)
    application_date = models.DateField(default='1970-01-01')
    audit_date = models.DateField(null=True, blank=True)
    auditor = models.ForeignKey(Manager, null=True, blank=True)

    def __str__(self):
        return self.seller.name + '兑换' + str(self.credits) + '积分'

    class Meta:
        db_table = 'INNER_APP_WITHDRAWAPPPLICATION'


class TransactionDetail(models.Model):
    TRADE_TYPES = (
        (u'绑定初始化', u'绑定初始化'),
        (u'扫码获赠', u'扫码获赠'),
        (u'商户扫码直接收取', u'商户扫码直接收取'),
        (u'商户扫码兑换收取', u'商户扫码兑换收取'),
        (u'推荐购券', u'推荐购券'),
        (u'推荐注册', u'推荐注册'),
        (u'中奖', u'中奖'),
        (u'签到', u'签到'),
        (u'扫码赠送', u'扫码赠送'),
        (u'扫码直接支付', u'扫码直接支付'),
        (u'优惠券购买', u'优惠券购买'),
        (u'扫码兑换支付', u'扫码兑换支付'),
        (u'抽奖', u'抽奖'),
        (u'商户提现', u'商户提现'),
    )
    trader = models.ForeignKey(Person, related_name='trade_history')
    opposite = models.ForeignKey(Person, related_name='+', null=True, blank=True)
    credits = models.IntegerField()
    type = models.CharField(max_length=36, choices=TRADE_TYPES)
    info = models.CharField(max_length=96, blank=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True)
    trade_datetime = models.DateTimeField()
    orderno = models.CharField(max_length=32, unique=True)
    need_reconciliation = models.BooleanField(default=False)

    def __str__(self):
        return self.type + self.info + self.orderno

    def get_orderno(self):
        return self.orderno

    class Meta:
        db_table = 'INNER_APP_TRANSACTIONDETAIL'


class UserCoupon(models.Model):
    COUPON_STATUS = (
        (u'未使用', u'未使用'),
        (u'已使用', u'已使用'),
        (u'已过期', u'已过期'),
    )
    user = models.ForeignKey(User)
    coupon = models.ForeignKey(Coupon)
    status = models.CharField(max_length=12, choices=COUPON_STATUS)
    in_log = models.ForeignKey(TransactionDetail, related_name='+', null=True, blank=True)
    out_log = models.ForeignKey(TransactionDetail, related_name='+', null=True, blank=True)

    def __str__(self):
        return self.user.name + ',' + self.coupon.name

    class Meta:
        db_table = 'INNER_APP_USERCOUPON'


class Invitation(models.Model):
    INVITATION_TYPES = (
        (u'注册邀请', u'注册邀请'),
        (u'优惠券分享', u'优惠券分享'),
    )
    inviter = models.ForeignKey(User, related_name='invite_log')
    invitee = models.ForeignKey(User, related_name='invited_log')
    type = models.CharField(max_length=24, choices=INVITATION_TYPES)
    is_completed = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.inviter.name + u'邀请' + self.invitee.name + u':' + self.type

    class Meta:
        db_table = 'INNER_APP_INVITATION'


class CouponInvitation(Invitation):
    coupon = models.ForeignKey(Coupon)

    def __str__(self):
        return self.inviter.name + u'邀请' + self.invitee.name + u':' + self.type + u':' + self.coupon.name

    class Meta:
        db_table = 'INNER_APP_COUPONINVITATION'


class CouponSend(models.Model):
    user_coupon = models.ForeignKey(UserCoupon)
    time = models.DateTimeField()
    operations = models.ForeignKey(Manager)

    class Meta:
        db_table = 'COUPONSEND'


class CouponAward(models.Model):
    user_coupon = models.ForeignKey(UserCoupon)
    time = models.DateTimeField()

    class Meta:
        db_table = 'COUPONAWARD'


class BusiType(models.Model):
    name = models.CharField(max_length=32)
    l_num = models.IntegerField(null=True, blank=True)
    l_time = models.IntegerField(null=True, blank=True)
    h_num = models.IntegerField(null=True, blank=True)
    h_time = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'BUSITYPE'


class CouponRule(models.Model):
    coupon = models.ForeignKey(Coupon)
    busitype = models.ForeignKey(BusiType, null=True, blank=True)
    l_num = models.IntegerField(null=True, blank=True)
    l_time = models.IntegerField(null=True, blank=True)
    h_num = models.IntegerField(null=True, blank=True)
    h_time = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'COUPONRULE'


class LotteryRule(models.Model):
    name = models.CharField(max_length=32)
    value = models.IntegerField()
    text = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'LOTTERYRULE'


class RepetitionExclude(models.Model):
    req_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.req_token

    class Meta:
        db_table = 'INNER_APP_REPETITIONEXCLUDE'


class CusRegion(models.Model):
    cusno = models.CharField(max_length=32, primary_key=True)
    address_code = models.CharField(max_length=32)
    add_dtime = models.DateTimeField(auto_now_add=True)
    mod_dtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cusno + ':' + self.address_code

    class Meta:
        db_table = 'CUS_REGION'


class ManagerRegion(models.Model):
    address_code = models.CharField(max_length=32, primary_key=True)
    manager = models.ForeignKey(Manager)
    add_dtime = models.DateTimeField(auto_now_add=True)
    mod_dtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address_code + self.manager.name

    class Meta:
        db_table = 'MANAGER_REGION'


class PreCreditLine(models.Model):
    cusno = models.CharField(max_length=32, primary_key=True)
    limit = models.BigIntegerField()
    manager = models.ForeignKey(Manager)
    add_dtime = models.DateTimeField(auto_now_add=True)
    mod_dtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cusno + '预授信额度:' + str(self.limit) + '元'

    class Meta:
        db_table = 'PRE_CREDIT_LINE'


class MicroCreditContract(models.Model):
    cusno = models.CharField(max_length=32, primary_key=True)
    limit = models.BigIntegerField()
    manager = models.ForeignKey(Manager)
    add_dtime = models.DateTimeField(auto_now_add=True)
    mod_dtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cusno + '贷款合同额度:' + str(self.limit) + '元'

    class Meta:
        db_table = 'MICRO_CREDIT_CONTRACT'


class CommunityAssess(models.Model):
    community = models.CharField(max_length=128, primary_key=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    add_dtime = models.DateTimeField(auto_now_add=True)
    mod_dtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.community + '单价:' + str(self.price) + '万元'

    class Meta:
        db_table = 'COMMUNITY_ASSESS'


class Activity(models.Model):
    TYPES = (
        ('盖楼', '盖楼'),
        ('信息登记', '信息登记'),
    )
    STATUS = (
        ('使用中', '使用中'),
        ('未使用', '未使用'),
    )
    name = models.CharField(max_length=48, unique=True, help_text='活动名称')
    description = models.TextField(default='', help_text='活动描述')
    typ = models.CharField(max_length=24, choices=TYPES, help_text='活动类型')
    key = models.CharField(max_length=32, unique=True, help_text='客户输入字段')
    status = models.CharField(max_length=24, choices=STATUS, default='未使用', help_text='状态')

    class Meta:
        db_table = 'ACTIVITY'


class ActivityExt(ExtInfo):
    MAP = {
        '盖楼': ['循环一', '循环二', '循环三', '循环一奖品', '循环二奖品', '循环三奖品'],
        '信息登记': ['信息登记字段一', '信息登记字段二', '信息登记字段三']
    }
    activity = models.ForeignKey(Activity, help_text='关联活动')

    class Meta:
        db_table = 'ACTIVITY_EXT'


class ActivityStatistics(models.Model):
    activity = models.ForeignKey(Activity, help_text='关联活动')
    openid = models.CharField(max_length=32, help_text='用户微信唯一标识')
    col1 = models.CharField(max_length=255, help_text='信息字段一')
    col2 = models.CharField(max_length=255, help_text='信息字段二')
    col3 = models.CharField(max_length=255, help_text='信息字段三')
    col4 = models.CharField(max_length=255, help_text='信息字段四')
    col5 = models.CharField(max_length=255, help_text='信息字段五')
    col6 = models.CharField(max_length=255, help_text='信息字段六')
    add_dtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ACTIVITY_STATISTICS'


class SmsRecord(models.Model):
    openid = models.CharField(max_length=32, help_text='用户微信唯一标识')
    telno = models.CharField(max_length=12)
    vcode = models.CharField(max_length=6)
    add_dtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SMS_RECORD'
