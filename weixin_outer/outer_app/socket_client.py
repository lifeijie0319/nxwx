# coding:utf-8
import base64
import socket
import json

from config import INNER_SK, MANA_SK
from global_var import logger


def download_file(fileheader, ip_port=MANA_SK):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sk.connect(ip_port)
        req_len = str(len(fileheader.encode('utf-8'))).zfill(6)
        sk.send(req_len + fileheader)
        resp = sk.recv(1024)
        while True:
            data = sk.recv(8192)
            if data == '':
                break
            resp += data
        if resp.startswith('msg'):
            return None
        elif resp.startswith('files'):
            logger.debug(resp)
            files_json = resp.split(':')[1]
            files = json.loads(files_json)
            logger.debug(files)
            return files
        else:
            return resp
    except Exception, e:
        logger.exception(e)
    finally:
        logger.debug("close....")
        sk.close()


def send2serv(data, ip_port=INNER_SK):
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    logger.debug('DATA_TYPE: %s' %type(data))
    sk = socket.socket()
    try:
        sk.connect(ip_port)
        req_len = str(len(data)).zfill(6)
        req = req_len + data
        logger.debug('REQUEST: %s', type(req))
        sk.sendall(req)
        resdata = ''
        while True:
            resp = sk.recv(2048)
            if not resp:
                break
            resdata += resp
        logger.debug('RES: %s', resdata)
        return json.loads(resdata)
    finally:
        logger.debug('close....')
        sk.close()
