# flask下的一些工具脚本
import random
import requests
import json

from urllib.parse import urlparse
from flask import request, current_app

#from app import logger

#logger = logging.getLogger("tools")
#mylogger.addconsole()
def generate_verification_code(count):

    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))

    myslice = random.sample(code_list, count)  
    verification_code = ''.join(myslice)  # list to string
    # print code_list
    # print type(myslice)
    return verification_code

def get_main_url():
    o = urlparse(request.url_root)
    base_url = o.scheme + '://' + o.hostname + ':' + current_app.config['API_MAIN_PORT']
    logger.info(base_url)
    return base_url

def get_timer_url():
    o = urlparse(request.url_root)
    base_url = o.scheme + '://' + o.hostname + ':' + current_app.config['API_TIMER_PORT']
    logger.info(base_url)
    return base_url
