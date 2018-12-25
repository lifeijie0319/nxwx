#-*- coding:utf-8 -*-
import datetime

from django.db import connections


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    res = cursor.fetchall()
    return [
        dict(zip(columns, row))
        for row in res
    ]


def execute_sql(sql, params=()):
    with connections['old_credits'].cursor() as cursor:
        ret = cursor.execute(sql, params)
        cursor.close() 
    return ret


def fetch_all(sql, params=[]):
    with connections['old_credits'].cursor() as cursor:
        cursor.execute(sql, params)
        ret = dictfetchall(cursor)
    return ret


def query_sync_status(table_name):
    sql = """
        SELECT * FROM YDW.WX_SYNC WHERE START_TIME =
        (
            SELECT MAX(START_TIME) FROM YDW.WX_SYNC
            WHERE TBNAME = %s
        )
        AND TBNAME = %s
    """
    sync = fetch_all(sql, (table_name, table_name))
    if sync and sync[0].get('STATUS') == 'SUCCESS':
        return True
    else:
        return False


def query_cus_credits(cusno):
    if query_sync_status('I_SC_KHJFYEB'):
        sql = 'SELECT * FROM YDW.I_SC_KHJFYEB WHERE KHH = %s'
        params = (cusno,)
        result = fetch_all(sql, params)
    else:
        sql = 'SELECT MAX(DATE_ID) FROM YDW.WX_SYNC'
        in_date = fetch_all(sql)
        in_date = in_date[0].get('DATE_ID') if in_date else '20150802'
        sql = """
            SELECT NVL(SUM(JFYE), 0) AS JFYE FROM
            (
                SELECT KHH, BRJFYE AS JFYE FROM YDW.R_JF_KHJFHZ
                WHERE KHH = %s AND SJRQ = %s
                UNION ALL
                SELECT CUST_NO AS KHH, TRADE_SCORE AS JFYE FROM BPAPP.TRADE_DETAILS
                WHERE TRADE_TYPE IN ('充值','冲正', '绑定初始化', '扫码获赠', '推荐购券', '推荐注册', '中奖', '签到')
                    AND CUST_NO = %s AND TRADE_TIME >= TO_DATE(%s, 'YYYYMMDD') + 1 DAYS
                UNION ALL
                SELECT CUST_NO AS KHH, (-1) * TRADE_SCORE AS JFYE FROM BPAPP.TRADE_DETAILS
                WHERE TRADE_TYPE IN ('兑换','预兑换', '扫码赠送', '扫码直接支付', '扫码兑换支付', '优惠券购买', '抽奖')
                    AND CUST_NO = %s AND TRADE_TIME >= TO_DATE(%s, 'YYYYMMDD') + 1 DAYS
            )
        """
        params = (cusno, in_date, cusno, in_date, cusno, in_date)
        result = fetch_all(sql, params)
    return result


def update_cus_credits(cusno, value):
    sql = 'UPDATE YDW.I_SC_KHJFYEB SET JFYE = JFYE + %s WHERE KHH = %s'
    params = (value, cusno)
    result = execute_sql(sql, params)
    return result


def insert_cus_credits(cusno, credits):
    today = datetime.date.today().strftime('%Y%m%d')
    sql = 'INSERT INTO YDW.I_SC_KHJFYEB(SJRQ, KHH, JFYE, TSRQ, BYZD1, BYZD2) VALUES (%s, %s, %s, %s, %s, %s)'
    params = (today, cusno, credits, today, '', '')
    result = execute_sql(sql, params)
    return result


#def query_trade_detail(in_date):
#    start_datetime = in_date + ' 00:00:00'
#    end_datetime = in_date + ' 23:59:59'
#    sql = 'SELECT * FROM BPAPP.TRADE_DETAILS WHERE TRADE_COMM1 LIKE %s AND TRADE_TIME BETWEEN %s AND %s'
#    params = ('wx%', start_datetime, end_datetime)
#    result = fetch_all(sql, params)
#    return result


def insert_trade_detail(**info):
    keys = ', '.join(info.keys())
    args = ', '.join('%s' for key in info.keys())
    sql = 'INSERT INTO BPAPP.TRADE_DETAILS (%s) VALUES (%s)' %(keys, args)
    params = info.values()
    result = execute_sql(sql, params)
    return result


def query_cus_info(cusno):
    if query_sync_status('WX_CUS_INFO_OPT'):
        sql = 'SELECT * FROM YDW.WX_CUS_INFO_OPT WHERE CST_ID = %s'
    else:
        sql = 'SELECT * FROM YDW.WX_CUS_INFO WHERE CST_ID = %s'
    params = (cusno,)
    result = fetch_all(sql, params)
    return result


def query_account(account):
    if query_sync_status('WX_ACCT_DEBIT_CARD_UNION_OPT'):
        sql = 'SELECT * FROM YDW.WX_ACCT_DEBIT_CARD_UNION_OPT WHERE ACCT_ID = %s OR CARD_ID = %s'
    else:
        sql = 'SELECT * FROM YDW.WX_ACCT_DEBIT_CARD_UNION WHERE ACCT_ID = %s OR CARD_ID = %s'
    params = (account, account)
    result = fetch_all(sql, params)
    return result


def query_coupon_term(cusno):
    if query_sync_status('WX_CUS_TERM_TOTAL_OPT'):
        sql = 'SELECT * FROM YDW.WX_CUS_TERM_TOTAL_OPT WHERE KHH = %s'
    else:
        sql = 'SELECT * FROM YDW.WX_CUS_TERM_TOTAL WHERE KHH = %s'
    params = (cusno,)
    result = fetch_all(sql, params)
    return result
