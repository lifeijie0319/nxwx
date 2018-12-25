# -*- coding:utf-8 -*-
from django.conf.urls import url
from django.views.static import serve

from .config import APP_NAME
from .views import activity
from .views import auth
from .views import carousel_figure
from .views import common
from .views import community_assess
from .views import coupon
from .views import coupon_term
from .views import cus_region
from .views import group
from .views import manager
from .views import manager_region
from .views import micro_credit_contract
from .views import param
from .views import pre_credit_line
from .views import reconciliation
from .views import report_coupon
from .views import report_cus_trade_detail
from .views import report_reservation
from .views import report_shop_trade_detail
from .views import report_shop_trade_total
from .views import shop
from .views import signin_rule
from .views import withdraw_application
from .views import reservation
from .views import branch
from .views import lottery_award
from .views import writeoff
from .views import lottery_rule

app_name = APP_NAME

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': '/home/nanxun/weixin_mana/mana_app/media/'}),
    url(r'^staticfile/(?P<name>[a-z_\d]+)/$', common.static, name='staticfile'),

    # 登录登出
    url(r'^login/$', auth.login, name='login'),
    url(r'^login/is_manager_exist/$', auth.is_manager_exist, name='is_manager_exist'),
    url(r'^logout/$', auth.logout, name='logout'),
    url(r'^password_change/$', auth.password_change, name='password_change'),

    # 默认的后台界面
    url(r'^index/$', auth.index, name='index'),

    # 系统管理
    # 用户组管理
    url(r'^group/page/$', group.page, name='group_page'),
    url(r'^group/add/$', group.add, name='group_add'),
    url(r'^group/delete/$', group.delete, name='group_delete'),
    url(r'^group/update/$', group.update, name='group_update'),
    url(r'^group/query/$', group.query, name='group_query'),
    url(r'^group/menu/$', group.menu, name='group_menu'),
    url(r'^group/menu/update/$', group.menu_update, name='group_menu_update'),

    # 用户管理
    url(r'^manager/page/$', manager.page, name='manager_page'),
    url(r'^manager/add/$', manager.add, name='manager_add'),
    # url(r'^manager/delete/$', manager.delete, name='manager_delete'),
    url(r'^manager/update/$', manager.update, name='manager_update'),
    url(r'^manager/query/$', manager.query, name='manager_query'),
    url(r'^manager/reset_password/$', manager.reset_password, name='manager_reset_password'),

    # 系统参数
    url(r'^param/page/$', param.page, name='param_page'),
    url(r'^param/add/$', param.add, name='param_add'),
    url(r'^param/delete/$', param.delete, name='param_delete'),
    url(r'^param/update/$', param.update, name='param_update'),
    url(r'^param/query/$', param.query, name='param_query'),

    # 签到规则设置
    url(r'^signin_rule/page/$', signin_rule.page, name='signin_rule_page'),
    url(r'^signin_rule/add/$', signin_rule.add, name='signin_rule_add'),
    url(r'^signin_rule/delete/$', signin_rule.delete, name='signin_rule_delete'),
    url(r'^signin_rule/update/$', signin_rule.update, name='signin_rule_update'),

    url(r'^coupon_reward/page/', lottery_award.coupon_reward_page, name='coupon_reward_page'),
    url(r'^coupon_reward/query/', lottery_award.coupon_reward_query, name='coupon_reward_query'),
    url(r'^coupon_send_recode/page/', coupon.coupon_send_recode_page, name='coupon_send_recode_page'),
    url(r'^coupon_send_recode/table/', coupon.coupon_send_recode_query, name='coupon_send_recode_query'),
    # 轮播图管理
    url(r'^carousel_figure/page/$', carousel_figure.page, name='carousel_figure_page'),
    url(r'^carousel_figure/update/$', carousel_figure.update, name='carousel_figure_update'),

    # 抽奖消耗表
    url(r'^lottery/award/use/page/$', lottery_award.use_page, name='lottery_award_use_page'),
    url(r'^lottery/award/use/query/$', lottery_award.use_query, name='lottery_award_use_query'),
    # 抽奖奖品设置
    url(r'^lottery/award/set/page/$', lottery_award.set_page, name='lottery_award_set_page'),
    url(r'^lottery/award/add/$', lottery_award.add, name='lottery_award_add'),
    url(r'^lottery/award/update/$', lottery_award.update, name='lottery_award_update'),
    url(r'^lottery/award/delete/$', lottery_award.delete, name='lottery_award_delete'),
    url(r'^lottery/award/distribute/$', lottery_award.distribute, name='lottery_award_distribute'),
    url(r'^lottery/award/distribute/query/$', lottery_award.distribute_query, name='lottery_award_distribute_query'),
    # 抽奖规则设置
    url(r'^lottery/award/rule/set/page/$', lottery_award.rule_set_page, name='lottery_award_rule_set_page'),
    url(r'^lottery/award/rule2/set/page/$', lottery_award.rule2_set_page, name='lottery_award_rule2_set_page'),
    url(r'^lottery/award/rule/add/$', lottery_award.rule_add, name='lottery_award_rule_add'),
    url(r'^lottery/award/rule/update/$', lottery_award.rule_update, name='lottery_award_rule_update'),
    url(r'^lottery/award/rule/delete/$', lottery_award.rule_delete, name='lottery_award_rule_delete'),
    url(r'^lottery/award/rule2/add/$', lottery_award.rule2_add, name='lottery_award_rule2_add'),
    url(r'^lottery/award/rule2/update/$', lottery_award.rule2_update, name='lottery_award_rule2_update'),
    url(r'^lottery/award/rule2/delete/$', lottery_award.rule2_delete, name='lottery_award_rule2_delete'),
    # 商户信息
    url(r'^shop/page/$', shop.page, name='shop_page'),
    # url(r'^shop/stick/$', shop.stick, name='shop_stick'),
    url(r'^shop/query/$', shop.query, name='shop_query'),
    url(r'^shop/update/$', shop.update, name='shop_update'),

    # 提现审核
    url(r'^withdraw_application/page/$', withdraw_application.page, name='withdraw_application_page'),
    url(r'^withdraw_application/query/$', withdraw_application.query, name='withdraw_application_query'),
    url(r'^withdraw_application/audit/$', withdraw_application.audit, name='withdraw_application_audit'),

    # 优惠券
    url(r'^coupon/page/$', coupon.page, name='coupon_page'),
    url(r'^coupon/add/$', coupon.add, name='coupon_add'),
    url(r'^coupon/delete/$', coupon.delete, name='coupon_delete'),
    url(r'^coupon/update/$', coupon.update, name='coupon_update'),
    url(r'^coupon/query/$', coupon.query, name='coupon_query'),
    url(r'^coupon/send/$', coupon.send, name='coupon_send'),
    url(r'^coupon/sendsome/page/$', coupon.coupon_send_some_page, name='coupon_send_some'),
    url(r'^coupon/sendsome/query/$', coupon.coupon_send_some_query, name='coupon_send_some_query'),
    url(r'^coupon/sendsome/$', coupon.coupon_upload_send_some, name='coupon_upload_send_some'),
    url(r'^coupon/sendsome/download/$', coupon.download_temp, name='coupon_sendsome_download'),
    # url(r'^coupon/detail/$', coupon.detail, name='coupon_detail'),
    url(r'^coupon/upload/$', coupon.upload, name='coupon_upload'),

    # 抽奖规则
    url(r'^lottery/rule/page/$', lottery_rule.page, name='lottery_rule_page'),
    url(r'^lottery/rule/query/$', lottery_rule.query, name='lottery_rule_query'),
    url(r'^lottery/rule/add/$', lottery_rule.add, name='lottery_rule_add'),
    url(r'^lottery/rule/delete/$', lottery_rule.delete, name='lottery_rule_delete'),
    url(r'^lottery/rule/update/$', lottery_rule.update, name='lottery_rule_update'),
    # 优惠券条件参数
    url(r'^coupon_term/page/$', coupon_term.page, name='coupon_term_page'),
    url(r'^coupon_term/update/$', coupon_term.update, name='coupon_term_update'),
    url(r'^coupon_term/query/$', coupon_term.query, name='coupon_term_query'),

    # 对账管理
    url(r'^reconciliation/log/page/$', reconciliation.log_page, name='reconciliation_log_page'),
    url(r'^reconciliation/log/query/$', reconciliation.log_query, name='reconciliation_log_query'),
    url(r'^reconciliation/amend/page/$', reconciliation.amend_page, name='reconciliation_amend_page'),
    url(r'^reconciliation/amend/query/$', reconciliation.amend_query, name='reconciliation_amend_query'),
    url(r'^reconciliation/amend_by_hand/$', reconciliation.amend_by_hand, name='reconciliation_amend_by_hand'),
    url(r'^reconciliation/auto_amend/$', reconciliation.auto_amend, name='reconciliation_auto_amend'),

    # 银行网点管理
    url(r'^branch/page/$', branch.page, name='branch_page'),
    url(r'^branch/add/$', branch.add, name='branch_add'),
    url(r'^branch/update/$', branch.update, name='branch_update'),
    url(r'^branch/query/$', branch.query, name='branch_query'),
    url(r'^branch/delete/$', branch.delete, name='branch_delete'),

    # 报表管理
    url(r'^report/coupon/page/$', report_coupon.page, name='report_coupon_page'),
    url(r'^report/coupon/query/$', report_coupon.query, name='report_coupon_query'),
    url(r'^report/cus_trade_detail/page/$', report_cus_trade_detail.page, name='report_cus_trade_detail_page'),
    url(r'^report/cus_trade_detail/query/$', report_cus_trade_detail.query, name='report_cus_trade_detail_query'),
    url(r'^report/reservation/page/$', report_reservation.page, name='report_reservation_page'),
    url(r'^report/reservation/query/$', report_reservation.query, name='report_reservation_query'),
    url(r'^report/shop_trade_detail/page/$', report_shop_trade_detail.page, name='report_shop_trade_detail_page'),
    url(r'^report/shop_trade_detail/query/$', report_shop_trade_detail.query, name='report_shop_trade_detail_query'),
    url(r'^report/shop_trade_total/page/$', report_shop_trade_total.page, name='report_shop_trade_total_page'),
    url(r'^report/shop_trade_total/query/$', report_shop_trade_total.query, name='report_shop_trade_total_query'),

    # 预约日期配置
    url(r'^reservation/date/page/$', reservation.page, name="reservation_date_page"),
    url(r'^reservation/date/add/$', reservation.add, name="reservation_date_submit"),
    url(r'^reservation/date/delete/$', reservation.delete, name='reservation_delete'),
    url(r'^reservation/date/update/$', reservation.update, name='reservation_update'),
    url(r'^reservation/date/query/$', reservation.query, name='reservation_query'),
    url(r'^reservation/second/page/$', reservation.setting_page, name='reservation_setting_page'),
    url(r'reservation/second/add/', reservation.setting_add, name='reservation_setting_add'),
    url(r'reservation/second/delete/$', reservation.setting_delete, name='reservation_delete'),
    url(r'reservation/second/update/$', reservation.setting_update, name='reservation_update'),
    url(r'reservation/second/query/$', reservation.setting_query, name='reservation_query'),

    # 客户地址关系
    url(r'^cus_region/page/$', cus_region.page, name='cus_region_page'),
    url(r'^cus_region/add/$', cus_region.add, name='cus_region_add'),
    url(r'^cus_region/delete/$', cus_region.delete, name='cus_region_delete'),
    url(r'^cus_region/update/$', cus_region.update, name='cus_region_update'),
    url(r'^cus_region/query/$', cus_region.query, name='cus_region_query'),
    url(r'^cus_region/upload/$', cus_region.upload, name='cus_region_upload'),

    # 客户经理地址关系
    url(r'^manager_region/page/$', manager_region.page, name='manager_region_page'),
    url(r'^manager_region/add/$', manager_region.add, name='manager_region_add'),
    url(r'^manager_region/delete/$', manager_region.delete, name='manager_region_delete'),
    url(r'^manager_region/update/$', manager_region.update, name='manager_region_update'),
    url(r'^manager_region/query/$', manager_region.query, name='manager_region_query'),
    url(r'^manager_region/upload/$', manager_region.upload, name='manager_region_upload'),

    # 客户预授信额度
    url(r'^pre_credit_line/page/$', pre_credit_line.page, name='pre_credit_line_page'),
    url(r'^pre_credit_line/add/$', pre_credit_line.add, name='pre_credit_line_add'),
    url(r'^pre_credit_line/delete/$', pre_credit_line.delete, name='pre_credit_line_delete'),
    url(r'^pre_credit_line/update/$', pre_credit_line.update, name='pre_credit_line_update'),
    url(r'^pre_credit_line/query/$', pre_credit_line.query, name='pre_credit_line_query'),
    url(r'^pre_credit_line/upload/$', pre_credit_line.upload, name='pre_credit_line_upload'),

    # 小额贷款合同统计
    url(r'^micro_credit_contract/page/$', micro_credit_contract.page, name='micro_credit_contract_page'),
    url(r'^micro_credit_contract/add/$', micro_credit_contract.add, name='micro_credit_contract_add'),
    url(r'^micro_credit_contract/delete/$', micro_credit_contract.delete, name='micro_credit_contract_delete'),
    url(r'^micro_credit_contract/update/$', micro_credit_contract.update, name='micro_credit_contract_update'),
    url(r'^micro_credit_contract/query/$', micro_credit_contract.query, name='micro_credit_contract_query'),
    url(r'^micro_credit_contract/upload/$', micro_credit_contract.upload, name='micro_credit_contract_upload'),

    # 客户地址关系
    url(r'^community_assess/page/$', community_assess.page, name='community_assess_page'),
    url(r'^community_assess/add/$', community_assess.add, name='community_assess_add'),
    url(r'^community_assess/delete/$', community_assess.delete, name='community_assess_delete'),
    url(r'^community_assess/update/$', community_assess.update, name='community_assess_update'),
    url(r'^community_assess/query/$', community_assess.query, name='community_assess_query'),
    url(r'^community_assess/upload/$', community_assess.upload, name='community_assess_upload'),
    # 核销类
    url(r'^seller/coupon/off/page/$', writeoff.page, name='seller_coupon_off'),
    url(r'^seller/coupon/off/query/$', writeoff.query, name='seller_coupon_off_query'),

    # 字段回复活动
    url(r'^activity/page$', activity.page, name='activity_page'),
    url(r'^activity/query', activity.query, name='activity_query'),
    url(r'^activity/add', activity.add, name='activity_add'),
    url(r'^activity/delete', activity.delete, name='activity_delete'),
    url(r'^activity/update', activity.update, name='activity_update'),
    url(r'^activity/upload', activity.upload, name='activity_upload'),
    url(r'^activity/ext/query', activity.ext_query, name='activity_ext_query'),
    url(r'^activity/ext/add', activity.ext_add, name='activity_ext_add'),
    url(r'^activity/ext/delete', activity.ext_delete, name='activity_ext_delete'),
    url(r'^activity/statistics/page$', activity.statistics_page, name='activity_statistics_page'),
    url(r'^activity/statistics/query', activity.statistics_query, name='activity_statistics_query'),

    # 开发中
    url(r'^todo/page/$', common.todo, name='todo'),
]
