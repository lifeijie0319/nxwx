#-*- coding:utf-8 -*-
import datetime

from django.db import connections
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_inner.settings")

cursor = connections['old_credits'].cursor()


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    res = cursor.fetchall()
    return [
        dict(zip(columns, row))
        for row in res
    ]


def query_credits(cusno):
    #with connections['old_credits'].cursor() as cursor:
    cursor.execute('SELECT * FROM YDW.I_SC_KHJFYEB WHERE KHH = %s', (cusno,))
    result = dictfetchall(cursor)
    return result


if __name__ == '__main__':
    pid = os.fork()
    if pid == 0:
        print 'I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid())
        print 'child', query_credits('101330721199403195410')
    else:
        print 'I (%s) just created a child process (%s).' % (os.getpid(), pid)
        print 'parent', query_credits('101330721199403195410')
