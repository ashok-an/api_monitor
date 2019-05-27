#!/usr/bin/env python

import json
import logging
import logging.config
import requests
import time
from requests.exceptions import Timeout

from requests_jwt import JWTAuth
import prometheus_client as prom

import common


# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

# common values
data    = "{\n\t\"username\": \"admin\",\n\t\"password\": \"alohamora\"\n}"
headers = { 'Content-Type': "application/json", 'cache-control': "no-cache"}

# prometheus
registry = prom.CollectorRegistry()
green = prom.Gauge('active_users_last_green_timestamp', 'Latest 200 status for /active-users endpoint', registry=registry)
red   = prom.Gauge('active_users_last_red_timestamp', 'Latest 40x/50x status for /active-users endpoint', registry=registry)
userCount = prom.Gauge('active_users_output', 'Output from /active-users, -1 in-case of errors', registry=registry)
recovery  = prom.Gauge('active_users_red_to_green_seconds', 'Time in seconds for /active-users to change from 500 to 200', registry=registry)
respTime  = prom.Gauge('active_users_response_time_seconda', 'Response time for /active-users', registry=registry)

errCount  = prom.Counter('active_users_errors', 'Error count for /active-users', registry=registry)
tokCount  = prom.Counter('token_refresh', 'Number of token refresh requests', registry=registry)

TOKEN_CHECK  = prom.Summary('runtime_token_status_seconds', 'Time spent processing /token-status', registry=registry)
TOKEN_GEN    = prom.Summary('runtime_token_seconds', 'Time spent processing /token', registry=registry)
ACTIVE_USERS = prom.Summary('runtime_active_users_seconds', 'Time spent processing /active-users inclusive of token check/refresh', registry=registry)

# Global - bad implementation
TOKEN = ''


def update_last_recovery_time(red, green):
    delta = green - red
    recovery.set(delta)
    logger.info("+ RecoveryTime={}\n".format(delta))
# end

@TOKEN_CHECK.time()
def is_token_ok(token):
    if not token:
        return False
    url     = "https://lackadaisical-tip.glitch.me/token-status"
    params  = {'token': token}
    return common.is_http_ok(url=url, headers=headers, params=params)
# end

@TOKEN_GEN.time()
def gen_token():
    token    = ''
    url      = "https://lackadaisical-tip.glitch.me/token"
    
    response = requests.post(url, headers=headers, data=data)
    logger.info("op={}, status={}, url={}".format('POST', response.status_code, url))

    if response.status_code in [200, 201] and response.json() and 'token' in response.json():
        token = response.json().get('token', '?')

    tokCount.inc()
    return token
# end

def get_token():
    global TOKEN # temp cache, but bad design; better alternate is to implement a class but no time
    if not is_token_ok(TOKEN):
        TOKEN = gen_token()
    # if
    return TOKEN
# end

@ACTIVE_USERS.time()
def get_user_count():
    token    = get_token()
    auth     = JWTAuth(token)
    url      = "https://lackadaisical-tip.glitch.me/active-users"

    start    = time.time()
    response = requests.get(url, auth=auth) 
    logger.info("op={:4s}, status={}, url={}".format('GET', response.status_code, url))
    duration = time.time() - start
    respTime.set(duration)

    # json={u'activeUsers': 8596}
    result = -1
    if response.json() and 'activeUsers' in response.json():
        green.set_to_current_time()
        result = response.json().get('activeUsers', -1)
        userCount.set(result)
    else:
        red.set_to_current_time()
        errCount.inc()
    # if
    prom.push_to_gateway('localhost:9091', job='api_active_users', registry=registry)
    return result
# end


if __name__ == '__main__':
    isFailing = False
    lastRed   = time.time()
    lastGreen = time.time()

    while True:
        result = get_user_count()
        time.sleep(5)
        logger.info("+ Count={}\n".format(result))

        if result == -1:
            lastRed   = time.time()
            isFailing = True
        else:
            lastGreen = time.time()
            if isFailing:
                update_last_recovery_time(lastRed, lastGreen)
                isFailing = False
            # if
        # if                
    # while
# end

