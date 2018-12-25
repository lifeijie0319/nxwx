#-*- coding:utf-8 -*-
import datetime

from django.db import connections


cursor = connections['old_credits'].cursor()


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    res = cursor.fetchall()
    return [
        dict(zip(columns, row))
        for row in res
    ]


def query_sync_status(table_name):
    sql = """
        SELECT * FROM YDW.WX_SYNC WHERE START_TIME =
        (
            SELECT MAX(START_TIME) FROM YDW.WX_SYNC
            WHERE TBNAME = %s
        )
        AND TBNAME = %s
    """
    cursor.execute(sql, (table_name, table_name))
    sync = dictfetchall(cursor)
    if sync and sync[0].get('STATUS') == 'SUCCESS':
        return True
    else:
        return False


def query_cus_credits(cusno):
    cursor.execute('SELECT * FROM YDW.I_SC_KHJFYEB WHERE KHH = %s', (cusno,))
    return dictfetchall(cursor)


def update_cus_credits(cusno, value):
    return cursor.execute('UPDATE YDW.I_SC_KHJFYEB SET JFYE = JFYE + %s WHERE KHH = %s', (value, cusno))


def insert_cus_credits(cusno, credits):
    today = datetime.date.today().strftime('%Y%m%d')
    cursor.execute('INSERT INTO YDW.I_SC_KHJFYEB(SJRQ, KHH, JFYE, TSRQ, BYZD1, BYZD2) VALUES (%s, %s, %s, %s, %s, %s)', (today, cusno, credits, today, '', ''))


def query_trade_detail(start_datetime, end_datetime):
    cursor.execute('SELECT * FROM BPAPP.TRADE_DETAILS WHERE TRADE_COMM1 LIKE %s AND TRADE_TIME BETWEEN %s AND %s', ('wx%', start_datetime, end_datetime))
    return dictfetchall(cursor)


def query_trade_detail2(start_datetime, end_datetime):
    start = start_datetime.strftime('%Y%m%d%H%M%S%f')
    end = end_datetime.strftime('%Y%m%d%H%M%S%f')
    sql = '''
        SELECT * FROM BPAPP.TRADE_DETAILS
        WHERE LEFT(TRADE_COMM1, 2)='wx'
            AND SUBSTR(TRADE_COMM1, 3, 20) >= %s AND SUBSTR(TRADE_COMM1, 3, 20) < %s
    '''
    cursor.execute(sql, (start, end))
    return dictfetchall(cursor)


def insert_trade_detail(**info):
    keys = ', '.join(info.keys())
    args = ', '.join('%s' for key in info.keys())
    sql = 'INSERT INTO BPAPP.TRADE_DETAILS (%s) VALUES (%s)' %(keys, args)
    #print sql
    #print info
    return cursor.execute(sql, info.values())


def query_cus_term(code):
    cursor.execute('SELECT * FROM YDW.WX_CUS_TERM WHERE CODE = %s', (code,))
    return dictfetchall(cursor)


def add_cus_term(code, description, start_date, end_date, arg_x, arg_y, arg_z):
    return cursor.execute('INSERT INTO YDW.WX_CUS_TERM (CODE, DESCRIPTION, START_DATE, END_DATE, ARG_X, ARG_Y, ARG_Z)\
        VALUES (%s, %s, %s, %s, %s, %s, %s)', (code, description, start_date, end_date, arg_x, arg_y, arg_z))


def update_cus_term(code, start_date, end_date, arg_x, arg_y, arg_z):
    return cursor.execute('UPDATE YDW.WX_CUS_TERM SET START_DATE = %s, END_DATE = %s,\
        ARG_X = %s, ARG_Y = %s, ARG_Z = %s WHERE CODE = %s', (start_date, end_date, arg_x, arg_y, arg_z, code))


def query_ods_branch():
    today = datetime.date.today().strftime('%Y%m%d')
    cursor.execute('SELECT * FROM YDW.ODS_KER_BBFMORGA WHERE ETL_DT = %s', (today, ))
    return dictfetchall(cursor)


def query_ods_staff():
    today = datetime.date.today().strftime('%Y%m%d')
    cursor.execute('SELECT * FROM YDW.ODS_KER_BBFMSTLR WHERE ETL_DT = %s', (today, ))
    return dictfetchall(cursor)
