'''
    Mooc 的请求模块：包含 get, post, head 常用的三大请求
'''

from time import sleep
from functools import wraps
from socket import timeout, setdefaulttimeout
from urllib import request, parse
from urllib.error import ContentTooShortError, URLError, HTTPError
from Mooc.Mooc_Config import *

__all__ = [
    'RequestFailed', 'request_get', 'request_post', 'request_head', 'request_check'
]

headers = ("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")  #这里模拟浏览器  
opener = request.build_opener()  
opener.addheaders = [headers]
request.install_opener(opener)
setdefaulttimeout(TIMEOUT)

class RequestFailed(Exception):
    pass

def request_decorate(count=3):
    def decorate(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            cnt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (ContentTooShortError, URLError, HTTPError, ConnectionResetError):
                    cnt += 1
                    if cnt >= count:
                        break
                    # print("continue......")
                    sleep(0.32)
                except (timeout):
                    break
            raise RequestFailed("request failed")
        return wrap_func
    return decorate

@request_decorate()
def request_get(url, decoding='utf8'):
    '''get请求'''
    req = request.Request(url=url)
    response = request.urlopen(req, timeout=TIMEOUT)
    text = response.read().decode(decoding)
    response.close()
    return text

@request_decorate()
def request_post(url, data, decoding='utf8'):
    '''post请求'''
    data = parse.urlencode(data).encode('utf8')
    req = request.Request(url=url, data=data, method='POST')
    response = request.urlopen(req, timeout=TIMEOUT)
    text = response.read().decode(decoding)
    response.close()
    return text

@request_decorate()
def request_head(url):
    '''head请求'''
    req = request.Request(url=url);
    response = request.urlopen(req, timeout=TIMEOUT)
    header =  dict(response.getheaders())
    response.close()
    return header

@request_decorate(1)
def request_check(url):
    '''检查url是否可以访问'''
    req = request.Request(url=url);
    response = request.urlopen(req, timeout=TIMEOUT)
    response.close()
