# -*- coding:utf-8 -*-
import concurrent
from concurrent.futures import ProcessPoolExecutor
from socket_client import send2serv


def f(i):
    send2serv({'path': 'activity.config', 'kargs': {'key': '月饼'}}, ('127.0.0.1', 7777))


if __name__ == '__main__':
    executor = ProcessPoolExecutor()
    future_to_res = {executor.submit(f, per): per for per in range(1)}
    for future_res in concurrent.futures.as_completed(future_to_res):
        future_res.result()
