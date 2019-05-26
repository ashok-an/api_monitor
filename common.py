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

def is_http_ok(url, headers=None, data=None, params=None):
    status = False
    try:
        response = requests.get(url, headers=headers, data=data, params=params, timeout=60) # timeout = 1min
        logger.info("op={:4s}, status={}, url={}, json={}".format('GET', response.status_code, url, response.json()))
        status = True if response.status_code is 200 else False
    except Timeout:
        logger.error("> ...timeout")
    # try    
    return status
# end

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print '%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000)
        return result
    # end
    return timed
# end
