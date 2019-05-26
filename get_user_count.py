#!/usr/bin/env python

import json
import logging
import logging.config
import requests
import time
from requests.exceptions import Timeout

from requests_jwt import JWTAuth

import common

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

# Global - bad implementation
TOKEN = ''

def is_token_ok(token):
    if not token:
        return False
    # if
    url     = "https://lackadaisical-tip.glitch.me/token-status"
    data    = "{\n\t\"username\": \"admin\",\n\t\"password\": \"alohamora\"\n}"
    headers = { 'Content-Type': "application/json", 'cache-control': "no-cache"}
    params  = {'token': token}
    return common.is_http_ok(url=url, headers=headers, params=params)
# end

def gen_token():
    token    = ''
    url      = "https://lackadaisical-tip.glitch.me/token"
    data     = "{\n\t\"username\": \"admin\",\n\t\"password\": \"alohamora\"\n}"
    headers  = { 'Content-Type': "application/json", 'cache-control': "no-cache"}
    
    response = requests.post(url, headers=headers, data=data)
    logger.info("op={}, status={}, url={}, json={:40s}".format('POST', response.status_code, url, response.json()))

    if response.status_code in [200, 201] and response.json() and 'token' in response.json():
        token = response.json().get('token', '?')
    # if
    return token
# end

def get_token():
    global TOKEN # temp cache, but bad design; better alternate is to implement a class but no time
    if not is_token_ok(TOKEN):
        TOKEN = gen_token()
    # if
    return TOKEN
# end

@common.timeit
def get_user_count():
    token    = get_token()
    auth     = JWTAuth(token)
    url      = "https://lackadaisical-tip.glitch.me/active-users"
    response = requests.get(url, auth=auth) 
    logger.info("op={:4s}, status={}, url={}, json={}".format('GET', response.status_code, url, response.json()))
    # json={u'activeUsers': 8596}
    if response.json() and 'activeUsers' in response.json():
        return response.json().get('activeUsers', 0)
    else:
        return 0
    # if
# end

if __name__ == '__main__':
    for i in range(1, 20):
        count = get_user_count()
        time.sleep(5)
        logger.info("+ Count={}\n".format(count))
    # for
# end

