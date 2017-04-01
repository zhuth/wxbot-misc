#!/usr/bin/env python3
#encoding=utf-8

import config, re, pycurl, base64
from io import BytesIO

_context = None

def context(val=None):
    global _context
    if val: _context = val
    return _context

def hourly_task():
    if not context(): return
    admin = context().friends().search(config.admin)[0]
    import datetime
    hr = datetime.datetime.now().hour
    if hr in [6, 12, 18]:
        admin.send(aqi())

def aqi(city='shanghai'):
    url = 'http://api.waqi.info/feed/%s/?token=%s' % (city, config.aqitoken)
    import json
    t = json.loads(download(url, False)[0].decode('utf-8'))
    try:
        return 'AQI: ' + str(t['data']['aqi']) + ', @' + t['data']['time']['s']
    except:
        return 'Err.'
    return 'Unable to get AQI.'

def download(url, proxy=True, referer=''):
    if '#' in url: url = url[:url.find('#')]
    if url.endswith('&'): url = url[:-1]
    url = url.strip()
    from w3lib.html import replace_entities
    url = replace_entities(url)
    
    print('* Download', url)
    
    c = pycurl.Curl() #创建一个同libcurl中的CURL处理器相对应的Curl对象
    b = BytesIO()
    c.setopt(pycurl.URL, url)
    #写的回调
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1) #参数有1、2
    #最大重定向次数,可以预防重定向陷阱
    c.setopt(pycurl.MAXREDIRS, 5)
    #连接超时设置
    c.setopt(pycurl.CONNECTTIMEOUT, 60) #链接超时
    #模拟浏览器
    c.setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)")
    if not referer:
        referer = url
    c.setopt(c.REFERER, referer)
    # cookie设置
    c.setopt(pycurl.COOKIEFILE, "cookies")
    c.setopt(pycurl.COOKIEJAR, "cookies")
    
    if proxy:
        #设置代理
        c.setopt(pycurl.PROXY, config.proxy)
        c.setopt(pycurl.PROXYUSERPWD, config.userpwd)
    c.perform()
    h = b.getvalue()
    b.close()
    u = c.getinfo(c.CONTENT_TYPE)
    u = u.split('/')[-1][:3]
    return h, u
    
def auto_reply_handler(msg):
    
    def save_file(content, url, ext='pdf'):
        fn = '/tmp/' + base64.urlsafe_b64encode(url.encode('utf-8'))[-16:].decode('ascii').replace('=', '') + '.' + ext.lower()
        with open(fn, 'wb') as f:
            f.write(content)
        return fn
        
    t = msg.text
    if '.cnki.' in t:
        msg.reply('开始下载')
        try:
            h, u = download(t, True)
            if u == 'htm':
                h = h.decode('utf-8')
                for m in re.finditer(r'href="(.*?)"', h):
                    url = m.group(1)
                    if 'pdfdown' in url:
                        #url = url.replace('nhdown', 'pdfdown')
                        pdf, u = download(url, True, t)
                        fn = save_file(pdf, url)
                        msg.reply_file(fn)
                        break
                for m in re.finditer(r'href="(.*?)"', h):
                    url = m.group(1)
                    if 'nhdown' in url:
                        url = url.replace('nhdown', 'pdfdown')
                        pdf, u = download(url, True, t)
                        fn = save_file(pdf, url)
                        msg.reply_file(fn)
                        break
                return '未找到正确的链接'
            elif u == 'pdf':
                fn = save_file(h, t)
                msg.reply_file(fn)
            else:
                return 'Unknown type: ' + u
        except Exception as ex:
            return str(ex)
        finally:
            pass
    elif 'libgen.' in t:
        try:
            h, u = download(t, False)
            m = re.search(r"'(/get.php.*?)'", h.decode('utf-8'))
            if not m: return '未找到链接'
            url = m.group(1)
            msg.reply('开始下载')
            h, u = download('http://libgen.io' + url, False, t)
            fn = save_file(h, url, u)
            msg.reply_file(fn)
        except Exception as ex:
            return str(ex)
    elif t in ['?', '？']: return '!'
    elif t == 'aqi':
        return aqi()
    elif t.startswith('~'):
        import os
        if t == '~ls':
            return '\n'.join(os.listdir('/tmp/'))
        elif t.startswith('~send'): 
            fn = '/tmp/' + t.split(' ')[1]
            msg.reply_file(fn)
        elif t.startswith('~friend'):
            cond = t.split(' ')[1]
            msg.reply(str(context().friends().search(cond)))
        
if __name__ == '__main__':
    class FakeMessage:
        text = ''
        
        def reply_file(self, fn): print('reply file', fn)
        
        def reply(self, any): print(any)
        
    msg = FakeMessage()
    msg.text = 'http://kns.cnki.net/kcms/detail/detail.aspx?filename=1016031862.nh&dbcode=CDFD&dbname=CDFDTEMP&v='
    r = auto_reply_handler(msg)
    print(r)
