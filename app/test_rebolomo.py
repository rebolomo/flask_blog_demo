#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Requests."""

from __future__ import division
import json
import os
import pickle
import unittest
import collections
import contextlib


import io
#import sys  
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')    	# fix the codec issue in windows cmd

import json
import requests
#import pytest
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth, _basic_auth_str
from requests.compat import (
    Morsel, cookielib, getproxies, str, urljoin, urlparse, is_py3,
    builtin_str, OrderedDict
    )
from requests.cookies import cookiejar_from_dict, morsel_to_cookie
from requests.exceptions import (ConnectionError, ConnectTimeout,
                                 InvalidSchema, InvalidURL, MissingSchema,
                                 ReadTimeout, Timeout, RetryError)
from requests.models import PreparedRequest
from requests.structures import CaseInsensitiveDict
from requests.sessions import SessionRedirectMixin
from requests.models import urlencode
from requests.hooks import default_hooks

try:
    import StringIO
except ImportError:
    import io as StringIO

try:
    from multiprocessing.pool import ThreadPool
except ImportError:
    ThreadPool = None

if is_py3:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('unicode-escape')


# Requests to this URL should always fail with a connection timeout (nothing
# listening on that port)
#BASE_URL = "http://192.168.0.254:8000/"
#BASE_URL = "http://192.168.1.102:9999/api/v1.0/"
#BASE_URL = "http://192.168.0.105:9999/api/v1.0/"
#BASE_URL = "http://172.114.110.108:9999/api/v1.0/"
BASE_URL = "http://127.0.0.1/api/v1.0/"
HTTPBIN = os.environ.get('HTTPBIN_URL', 'http://httpbin.org/')
# Issue #1483: Make sure the URL always has a trailing slash
HTTPBIN = HTTPBIN.rstrip('/') + '/'


def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""
    return urljoin(HTTPBIN, '/'.join(suffix))

	
def register():
    headers = {'content-type': 'application/json'}
    param = {'username' : 'test2', 'password' : '123456' }
    
    r = requests.post(BASE_URL + 'user/register', data=json.dumps(param), headers=headers)    
    print(r.url)
    print(r.status_code)
    print(r.text)
    
def login():
    headers = {'content-type': 'application/json'}
    #param = {'username' : 'test', 'password' : '123456' }
    
    #r = requests.get(BASE_URL + 'user/token', auth=HTTPBasicAuth('test5', 'password'), headers=headers)    
    r = requests.post(BASE_URL + 'user/login', auth=HTTPBasicAuth('test1', '123456'), headers=headers)
    print(r.url)
    print(r.status_code)
    print(r.text)
    jo = json.loads(r.text)
    token = jo['access_token']
    print (token)
    return token

def blogs(token):
    headers = {'content-type': 'application/json'}
    #param = {'username' : 'test5', 'password' : '123456' }
    
    #r = requests.get(BASE_URL + 'user/token', auth=HTTPBasicAuth('test5', 'password'), headers=headers)    
    r = requests.get(BASE_URL + 'posts/', auth=HTTPBasicAuth(token, ''),  headers=headers)    
    #r = requests.get(BASE_URL + 'posts/',  headers=headers)    
    print(r.url)
    print(r.status_code)
    print(r.text)

if __name__ == '__main__':
    #clear_db()

	#register()

    token = login()
    #view_user(token)

    # shop================
    #shops(token)
    #single_shop(token)
	#default_shop(token)
    #create_shop(token)
    #edit_shop(token)
    #set_default_shop(token)
    #shops_by_itemid(token)

    # customer ==================
    #customers_all(token)
    #customers(token)
    #create_customer(token)
    #edit_customer(token)
    #search_customer(token)

    # product ==================
    #products_all(token)
    #products(token)
    #create_product(token)
    #edit_product(token)
    #search_product(token)

    # order =============
    #orders(token)
    #orders_by_itemid(token)
    
    #single_order(token)
    create_order(token)
    #edit_order(token)