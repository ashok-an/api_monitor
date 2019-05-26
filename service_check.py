#!/usr/bin/env python
import json
import logging
import logging.config
import requests
import time
from requests.exceptions import Timeout

import prometheus_client as prom

import common

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('api_monitor')

# prometheus initialization
registry = prom.CollectorRegistry()
green = prom.Gauge('service_last_green_timestamp', 'Latest 200 status for /status endpoint', registry=registry)
red   = prom.Gauge('service_last_red_timestamp', 'Latest 40x/50x status for /status endpoint', registry=registry)
REQUEST_TIME = prom.Summary('runtime_status_seconds', 'Time spent processing /status', registry=registry)

@REQUEST_TIME.time()
def is_service_ok():
    url    = 'https://lackadaisical-tip.glitch.me/status'
    status = common.is_http_ok(url)
    g      = None
    if status:
        green.set_to_current_time()
    else:
        red.set_to_current_time()
    # if
    prom.push_to_gateway('localhost:9091', job='api_status', registry=registry)
# end

if __name__ == '__main__':
    while True:
        is_service_ok()
        time.sleep(5)
    # while
# end

