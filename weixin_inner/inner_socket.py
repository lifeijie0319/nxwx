# -*- coding: utf-8 -*-
import django
import json
import os
import SocketServer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weixin_inner.settings")
django.setup()

from inner_app.logger import logger
from inner_app import service


def make_response(data):
    json_data = json.loads(data)
    module_str, func_str = json_data.get('path').split('.')
    module = getattr(service, module_str)
    logger.debug(module)
    func = getattr(module, func_str)
    kargs = json_data.get('kargs')
    data = func(**kargs)
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            req_len = self.request.recv(6)
            data = self.request.recv(int(req_len))
            logger.debug('REQUEST: %s', data)
            resp = make_response(data)
            logger.debug('RESPONSE: %s', resp)
            self.request.sendall(resp)
        except BaseException, e:
            logger.exception(e)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8083
    SocketServer.ForkingTCPServer.allow_reuse_address = True
    server = SocketServer.ForkingTCPServer((HOST, PORT), MyTCPHandler)
    print "Server loop running in process: ", os.getpid()
    server.serve_forever()
