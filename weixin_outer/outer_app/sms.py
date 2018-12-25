#-*- coding:utf-8 -*-
import base64
import datetime
import hashlib
import json
import random
import requests


username = 'bc77e9e9354b40ec905f278bc31b97b2'
password = '14a36f45cddd7609'


def send_sms(phone, vcode):
    now = datetime.datetime.utcnow()
    nounce = now.strftime('%Y%m%d%H%M%S%f')
    created = now.strftime('%Y-%m-%d') + 'T' + now.strftime('%H:%M:%S') + 'Z'
    print created
    m = hashlib.sha256()
    m.update(nounce + created + password)
    password_digest = base64.b64encode(m.digest())
    url = 'http://aep.api.cmccopen.cn/entireSms/sendTemplateSms/v1'
    headers = {
        'Authorization': 'WSSE realm="SDP",profile="UsernameToken",type="AppKey"',
        'X-WSSE': 'UsernameToken Username="%s",PasswordDigest="%s",Nonce="%s",Created="%s"' %(username, password_digest, nounce, created),
        'Content-Type': 'application/json;charset=UTF-8',
    }

    payload = {
        'from': '106575261108083',
        'to': '+86' + phone,
        'smsTemplateId': '5f1ea87e-6157-4553-b4bc-da10a2aa7d20',
        'paramValue': {'code': vcode},
        #'notifyURL': 'http://10.135.82.143:7777/tempsms',
        'smsType': 1,
        'toType': 1,
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    print res.headers
    print res.json()


def query_sms_status(sms_id):
    url = 'http://aep.api.cmccopen.cn/sms/getSmsDeliveryStatus/v1?smsMsgId=%s' %sms_id
    headers = {
        'Authorization': 'WSSErealm="SDP",profile="UsernameToken",type="AppKey"',
        'X-WSSE': 'UsernameToken Username="%s",PasswordDigest="%s",Nonce="%s",Created="%s"' %(username, password_digest, nounce, created),
    }
    res = requests.get(url, headers=headers)
    print res.headers
    print res.json()


def get_sms_status(request):
    data = json.loads(request.body)
    print data


if __name__ == '__main__':
    send_sms('17749775784', 134513)
