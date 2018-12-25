# -*- coding:utf-8 -*-
import datetime
import logging
import os
import socket
import SocketServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_fh = logging.FileHandler('/home/nanxun/log/django/forwarder.log')
logger.addHandler(log_fh)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        try:
            req_start = datetime.datetime.now()
            req_len = self.request.recv(6)
            data = self.request.recv(int(req_len))
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if data.startswith('file') or data.startswith('dir'):
                client.connect(('154.88.2.121', 8083))
                client.sendall(req_len + data)
                while True:
                    resp = client.recv(8192)
                    if not resp:
                        break
                    self.request.send(resp)
            else:
                client.connect(('154.88.2.120', 8082))
                client.sendall(req_len + data)
                resdata = ''
                while True:
                    resp = client.recv(2048)
                    if not resp:
                        print 'data end'
                        break
                    resdata += resp
                print 'RESP:', resdata
                self.request.sendall(resdata)
            req_end = datetime.datetime.now()
            if req_end - req_start > datetime.timedelta(seconds=1):
                logger.debug('REQ: %s', data)
                logger.debug('START: %s', req_start)
                logger.debug('END: %s', req_end)
        finally:
            client.close()


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8081
    SocketServer.ForkingTCPServer.allow_reuse_address = True
    server = SocketServer.ForkingTCPServer((HOST, PORT), MyTCPHandler)
    print "Server loop running in process: ", os.getpid()
    server.serve_forever()
