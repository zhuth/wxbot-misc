#!/usr/bin/env python3
#encoding: utf-8

from wxpy import *
import time, datetime
import os, importlib
import config
    
if __name__ == '__main__':
    bot = Bot(console_qr=True, cache_path='wxcache')

    handler = importlib.import_module('handler')
    handler_import = time.time()
    handler.context(bot)

    admin = bot.friends().search(config.admin)[0]
    
    def timer():
        time.sleep(3600-(time.time() % 3600))
        while True:
            hr = datetime.datetime.now().hour
            admin.send('现在是 %d 时整。' % hr)
            handler.hourly_task()
            time.sleep(3600)

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
        
        if time.time() - handler_import > 60:
            if os.stat('handler.py').st_mtime > handler_import:
                importlib.reload(handler)
                handler.context(bot)
                print('* handler reloaded')
            handler_import = time.time() - 30
        
        return handler.auto_reply_handler(msg)
    
    file_id = 0
    
    @bot.register(msg_types=ATTACHMENT)
    def save_file(msg):
        global file_id
        file_id += 1
        msg.get_file(str(file_id) + '_' + msg.file_name)
    
    bot.join()
