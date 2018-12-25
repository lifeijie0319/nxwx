# -*- coding:utf-8 -*-
import base64
import os
import sys
from django.core.wsgi import get_wsgi_application
from socket_client import download_file

sys.path.append('/home/nanxun/weixin_outer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weixin_outer.settings')
application = get_wsgi_application()


def sync_media():
    local_dir = '/home/nanxun/weixin_outer/outer_app/media/'
    remote_dir = '/home/nanxun/weixin_mana/mana_app/media/'
    files = download_file('dir:' + remote_dir)
    for f_path in files:
        print 'FILE({}):{}'.format(type(f_path), f_path)
        path, tail = os.path.splitext(f_path)
        print 'TAIL: {}'.format(tail)
        if tail in ('.jpg', '.png', '.txt'):
            down_file = download_file(fileheader='file:' + f_path)
            local_f_path = f_path.replace('mana', 'outer')
            print type(down_file)
            with open(local_f_path, 'w') as f:
                f.write(down_file)


if __name__ == '__main__':
    sync_media()
