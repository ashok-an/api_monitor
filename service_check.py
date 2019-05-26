#!/usr/bin/env python
import json
import logging
import logging.config
import requests
import time
from requests.exceptions import Timeout

import common

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

def is_service_ok():
    url = 'https://lackadaisical-tip.glitch.me/status'
    return common.is_http_ok(url)
# end

if __name__ == '__main__':
    while True:
        is_service_ok()
        time.sleep(5)
        print
    # while
# end

