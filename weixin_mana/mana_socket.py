# -*- coding: utf-8 -*-
import json
import os
import SocketServer


def get_all_files(p):
    ret_files = []

    def gci(file_path):
        # 遍历file_path下所有文件，包括子目录
        files = os.listdir(file_path)
        print '{}:'.format(file_path)
        for f in files:
            print '{}'.format(f.decode())
            f_path = os.path.join(file_path, f.decode())
            if os.path.isdir(f_path):
                gci(f_path)
            else:
                ret_files.append(f_path)
        print '\n'
    gci(p)
    return ret_files


class FileTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        req_len = self.request.recv(6)
        data = self.request.recv(int(req_len))
        print 'DATA:', data
        if data.startswith('file'):
            file_path = data.split(':')[1]
            if os.path.isfile(file_path):
                f = open(file_path, 'rb')
                while True:
                    resp = f.read(8192)
                    if not resp:
                        print 'file end'
                        break
                    self.request.send(resp)
                f.close()
            else:
                self.request.send('msg:file not existed')
        elif data.startswith('dir'):
            dir_path = data.split(':')[1]
            files = get_all_files(dir_path)
            print 'FILES:{}'.format(files)
            self.request.send('files:' + json.dumps(files))
        else:
            self.request.send('msg:request not valid')


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8082
    SocketServer.ForkingTCPServer.allow_reuse_address = True
    server = SocketServer.ForkingTCPServer((HOST, PORT), FileTCPHandler)
    print "Server loop running in process: ", os.getpid()
    server.serve_forever()
