# -*- coding: utf-8 -*-
import django
import json
import multiprocessing
import os
import socket
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_inner.settings")
django.setup()
from inner_app.logger import logger
from inner_app import service


HOST, PORT = "0.0.0.0", 7777


def make_response(data):
    print 'start make_response'.format(os.getpid())
    time.sleep(3)
    json_data = json.loads(data)
    module_str, func_str = json_data.get('path').split('.')
    module = getattr(service, module_str)
    # logger.debug(module)
    func = getattr(module, func_str)
    kargs = json_data.get('kargs')
    data = func(**kargs)
    print 'end make_response'.format(os.getpid())
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def handle(channel):
    print 'sub process[{}]'.format(os.getpid())
    print 'channel[{}]'.format(channel)
    pass
    # req_len = channel.recv(6)
    # data = channel.recv(int(req_len))
    # logger.debug('REQUEST: %s', data)
    # resp = make_response(data)
    # logger.debug('RESPONSE: %s', resp)
    # channel.sendall(resp)


def run():
    pool = multiprocessing.Pool()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print 'main process[{}]'.format(os.getpid())
    print 'cpu_count: {}'.format(multiprocessing.cpu_count())
    while True:
        channel, address = server.accept()
        try:
            pool.apply_async(func=handle, args=(1, ))
        except Exception as e:
            logger.exception(e)
        finally:
            channel.close()


if __name__ == "__main__":
    run()
