#coding:utf-8
import sys,os
import httplib

def sendSoapDataByHttp(strWsdl,strInterfacename,strSoapDataFile ):    
    if not os.path.isfile(strSoapDataFile) :
        return -1,"Argument Error, SoapData: %s invalid." % strSoapDataFile

    try:
        f = open(strSoapDataFile,'r')
    except IOError,e:
        return -1,"Fail to open the file: %s." % strSoapDataFile

    lines = f.readlines()
    f.close()

    SoapMessage = '''<?xml version="1.0" encoding="UTF-8"?>\n''' + ''.join(lines)

    ##http://192.168.1.100:7654/services/abcMgntService?wsdl
    pos = strWsdl.find('/',7)
    strHost = strWsdl[7:pos]
    strPostval = strWsdl[pos:len(strWsdl) - 5]

    webservice = httplib.HTTP(strHost)
    webservice.putrequest("POST", strPostval)
    webservice.putheader("Host", strHost)
    webservice.putheader("User-Agent", "Python Post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(SoapMessage))
    webservice.endheaders()
    webservice.send(SoapMessage)
    statuscode, statusmessage, header = webservice.getreply()
    msg = ' Response: %d %s\n headers: %s\n %s' % (statuscode,statusmessage,header,webservice.getfile().read() )

    if statuscode == 200:
        return 0,msg
    else:
        return 1,msg


def send_data():
    retCode, msg = sendSoapDataByHttp("http://192.168.1.100:7654/services/abcMgntService?wsdl
","do_interface_func","./soap_data.xml")
    print "Return code: ", retCode
    print msg
    


 

