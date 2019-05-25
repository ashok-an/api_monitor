#!/usr/bin/env python

import json
import logging
import logging.config
import requests

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

# Global - bad implementation
TOKEN = ''

def _is_http_ok(url, auth=None):
    r = requests.get(url, auth=auth)
    logger.info("GET URL={}".format(url))
    logger.info("+ Status={}, Text={}".format(r.status_code, r.text))
    status = True if r.status_code is 200 else False
    return status
# end

def is_service_ok():
    url = 'https://lackadaisical-tip.glitch.me/status'
    return _is_http_ok(url)
# end

def _is_token_ok(token=None):
    url = 'https://lackadaisical-tip.glitch.me/token'
    return _is_http_ok(url, auth=('admin', 'alohamora'))
# end

def _gen_token():
    global TOKEN
    output = None
# end

def _renew_token(token=None):
    global TOKEN
    pass
# end

def get_token():
    global TOKEN
    pass
# end

def get_user_count():
    output = 0
    return output
# end

if __name__ == '__main__':
    count = get_user_count()
    logger.info("Count={}".format(count))

    _is_token_ok()
    is_service_ok()
# end
