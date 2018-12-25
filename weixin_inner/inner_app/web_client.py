#coding:utf-8
import json

from suds.client import Client

from config import QUEUE_WSDL_URL


class WsdlClient:
    def __init__(self):
        self.client = Client(QUEUE_WSDL_URL)
        self.service = self.client.service


    def get_appointment(self, start_time, end_time, user_id, deptno):
        send_msg = {
            'START_TIME': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'END_TIME': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'CUSTOMER_NO': user_id,
            'NET_NO': deptno,
        }
        error_mapping = {
            '02': '已有预约，预约失败',
            '03': '当前身份证号、银行卡号已是长期VIP客户',
            '04': '预约数据保存失败',
            '05': '参数错误',
        }
        send_msg = json.dumps(send_msg)
        ret_msg = json.loads(self.service.GET_APPOINTMENT(send_msg))
        ret_code = ret_msg.get('RTN_TYPE')
        if ret_code == '01':
            ret_msg['success'] = True
        else:
            ret_msg['success'] = False
            ret_msg['msg'] = error_mapping.get(ret_code, '未知错误')
        return ret_msg

    def get_list_count(self, deptno):
        send_msg = {
            'DEPT_NO': deptno,
            'TASK_TYPE': '0001'
        }
        error_mapping = {
            '01': '参数错误',
            '02': '没有该机构',
            '03': '浪潮接口访问失败',
            '04': '没有该业务',
        }
        send_msg = json.dumps(send_msg)
        ret_msg = json.loads(self.service.GET_LISTCOUNT(send_msg))
        ret_code = ret_msg.get('RTN_TYPE')
        if ret_code == '00':
            ret_msg['success'] = True
        else:
            ret_msg['success'] = False
            ret_msg['msg'] = error_mapping.get(ret_code, '未知错误')
        return ret_msg

    def get_listno(self, deptno):
        send_msg = {
            'DEPT_NO': deptno,
            'TASK_TYPE': '0001',
        }
        error_mapping = {
            '01': '参数错误',
            '02': '没有该机构',
            '03': '浪潮接口访问失败',
            '04': '没有该业务',
            '05': '该业务暂时不办理',
            '06': '该业务已满',
        }
        send_msg = json.dumps(send_msg)
        ret_msg = json.loads(self.service.GET_LISTNO(send_msg))
        ret_code = ret_msg.get('RTN_TYPE')
        if ret_code == '00':
            ret_msg['success'] = True
        else:
            ret_msg['success'] = False
            ret_msg['msg'] = error_mapping.get(ret_code, '未知错误')
        return ret_msg

    def get_isvalid(self, deptno, listno):
        send_msg = {
            'DEPT_NO': deptno,
            'TASK_TYPE': '0003',
            'LIST_NO': listno,
        }
        error_mapping = {
            '01': '参数错误',
            '02': '没有该机构',
            '03': '浪潮接口访问失败',
        }
        status_mapping = {
            '01': '无此号码',
            '02': '等待中',
            '03': '正在处理中',
            '04': '处理完毕',
            '05': '已过期',
        }
        send_msg = json.dumps(send_msg)
        ret_msg = json.loads(self.service.GET_ISVALID(send_msg))
        ret_code = ret_msg.get('RTN_TYPE')
        if ret_code == '00':
            ret_msg['success'] = True
            status_code = ret_msg.get('NO_STATUS')
            ret_msg['status'] = status_mapping.get(status_code, '未知状态')
        else:
            ret_msg['success'] = False
            ret_msg['msg'] = error_mapping.get(ret_code, '未知错误')
        return ret_msg


if __name__ == '__main__':
    cli = WsdlClient()
    print cli.get_list_count('886030')
