#!/usr/bin/env python

import json
import logging
import logging.config
import requests
import time
from requests.exceptions import Timeout

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

def http_get(url, headers=None, data=None, params=None):
    try:
        response = requests.get(url, headers=headers, data=data, params=params, timeout=60) # timeout = 1min
        logger.info("op={:4s}, status={}, url={}".format('GET', response.status_code, url))
    except Timeout:
        logger.error("> ...timeout")
    # try
    return response
# end    


def is_http_ok(url, headers=None, data=None, params=None):
    response = http_get(url, headers, data, params)
    status   = True if response.status_code is 200 else False
    return status
# end
