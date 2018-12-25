#coding:utf-8
from ..models import *
from django.forms.models import model_to_dict
from ..tools import to_json


def simple_insert(data,model,key=-1,key_data={}):
    '''
    插入数据
    入参：
    data：请求数据字典
    model：模型名称
    key_data:{"colum":model}
    '''
    string = model+'('
    for k in data:
        flag = 0
        if key != -1:
            for i in key_data:
                if (k == i):
                    flag =i
            if flag != 0:
                """
                查询外键对应的类
                """
                forstring = str(key_data[flag])+'.objects.get(id='+str(data[k])+')'
                forkey = eval(forstring)
                string = string + k + '='+'forkey'+','
            else :
                string = string + k + '='+str(data[k])+','
        else:
            string = string + k + '='+str(data[k])+','
    string = string[:-1]
    string = string+')'
    formdata = eval(string)
    formdata.save()
    resp = {"errcode": 0, "msg": "success"}
    return resp


def simple_query(data,model,key =-1,key_data={}):
   '''
   查询数据
   入参：
   data:请求数据字典
   model: 查询模型名称
   model.object.filter()
   '''
   string = model+'.objects.filter('
   for k in data:
       string = string +k +"="+str(data[k])+','
   string = string[:-1]
   string = string+')'
   formdata = eval(string)
   result = formdata 
   result = to_json(result)
   if key == -1:
       print "result:",result
       resp = {"errcode": 0, "msg": "success" ,"result":result}
   else :
       for i in result:
           for j in i.get("field"):
               for k in key_data:
                   if k == j:
                       '''展开外键'''
                       key_string = key_data[k]+'.objects.get(id='+str(i['field'][j])+')'
                       key_data = eval(key_string)
                       result["i"]['field'][j]= to_string(key_data)
   return resp


def simple_update(data,model,updata):
   '''
   更新数据
   入参:
   data:请求数据字典
   model:更新模型名称
   updata:更新数据字典
   '''
   string = model +'.objects.filter('
   for k in data:
       string = string + k +'='+str(data[k])  +','
   string = string[:-1]
   string = string +').update('
   for k in updata:
       string = string +k +'='+ str(data[k])+','
   string = string[:-1]
   string = string +')'
   formdata = eval(string)
   formdata.save()   
   resp = {'errcode': 0, 'msg': 'success'}
   return resp

def simple_delete(data,model):
   '''
   更新参数
   入参：
   data:请求数据字典
   model:请求模型名称
   models.UserInfo.objects.filter(user='yangmv').delete()
   '''
   string = model+'.objects.filter('
   for k in data:
       string = string +k +'='+str(data[k]) +','
   string = string [:-1]
   string = string +').delete()'
   formdata = eval(string)
   resp = {'errcode': 0, 'msg': 'success'}
   return resp
