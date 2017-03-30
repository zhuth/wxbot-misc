#!/usr/bin/env python3
#encoding: utf-8

from wxpy import *
import time
import os, importlib
    
if __name__ == '__main__':
    handler = importlib.import_module('handler')
    handler_import = time.time()
    
    bot = Bot(console_qr=True, cache_path='wxcache')

    mew = bot.friends().search('mew')[0]
    zth = bot.friends().search('ZTH')[0]
    xiaoman = bot.friends().search('曼')[0]
    
    def timer():
        time.sleep(3600-(time.time() % 3600))
        while True:
            zth.send('我在')
            time.sleep(3600)
            import datetime
            if datetime.datetime.hour in [6, 10, 14, 18]:
                zth.send(handler.aqi())

    from threading import Thread
    t = Thread(target=timer).start()
    
    @bot.register()
    def print_others(msg):
        print(msg)
        
    @bot.register(msg_types=TEXT)
    def auto_reply(msg):
        global handler_import
        
        if isinstance(msg.chat, Group) and not msg.is_at:
            return
        if not msg.sender in [mew, zth, xiaoman]:
            return
        
        if time.time() - handler_import > 60:
            if os.stat('handler.py').st_mtime > handler_import:
                importlib.reload(handler)
                print('* handler reloaded')
            handler_import = time.time()
        
        return handler.auto_reply_handler(msg)
    
    file_id = 0
    
    @bot.register(msg_types=ATTACHMENT)
    def save_file(msg):
        global file_id
        file_id += 1
        msg.get_file(str(file_id) + '_' + msg.file_name)
    
    bot.join()
