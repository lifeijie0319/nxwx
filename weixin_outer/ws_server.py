#-*- coding:utf-8 -*-
import json
import os
import tornado.ioloop
import tornado.web
import tornado.websocket
 
  
class TradeReplyHandler(tornado.web.RequestHandler): 
    def post(self):
        print WSHandler.clients
        post_data = json.loads(self.request.body)
        print 'POST:', post_data
        openid = post_data.get('openid')
        print 'OPENID:', openid
        client = WSHandler.find_client(openid)
        if client:
            text = post_data.get('text')
            client.write_message(text)
            self.write({'success': True})
        else:
            self.write({'success': False})


class WSHandler(tornado.websocket.WebSocketHandler):  
    clients = {}
 
    @classmethod
    def find_client(cls, openid):
        return cls.clients.get(openid)
                
    def check_origin(self, origin):
        return True

    def open(self, openid):
        WSHandler.clients[openid] = self
        print 'OPEN:', WSHandler.clients
  
    def on_close(self):
        for k, v in WSHandler.clients.items():
            if v == self:
                WSHandler.clients.pop(k)
        print 'CLOSE:', WSHandler.clients
          
##MAIN  
if __name__ == '__main__':  
    app = tornado.web.Application(  
        handlers=[
            (r'/ws/trade_reply', TradeReplyHandler),
            (r"/ws/(?P<openid>[\w-]+)", WSHandler)
        ],  
        debug = True,
        template_path = os.path.join(os.path.dirname(__file__), "templates"),  
        static_path = os.path.join(os.path.dirname(__file__), "static")  
    )
    port = 9091
    app.listen(port)
    print 'listen ', port
    tornado.ioloop.IOLoop.instance().start()  
