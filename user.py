#!/usr/bin/env python3
import time
import random
import datetime
import sys
import os
import requests
import asyncio
import concurrent.futures
import logging
import json
from scipy.stats import poisson

MINUTE = 60
TIME_TO_RUN = 120 
def main():
    first_start_time = time.time()
    interval_counter = 0
    rate = 5
    while (time.time() - first_start_time) < TIME_TO_RUN * MINUTE:
        if (time.time()- first_start_time  > interval_counter*30):
            print ("interval time:"+str(time.time()-first_start_time))         
            logging.basicConfig(
                    level=logging.CRITICAL,
                    format='%(threadName)10s %(name)18s: %(message)s',
                    stream=sys.stderr,
                )
            loop = asyncio.get_event_loop()
            loop.run_until_complete(post(rate))
            interval_counter += 1

async def post(rate):
        log = logging.getLogger('run_blocking_tasks')
        log.info('starting')
        log.info('creating executor tasks')
        requests = poisson.rvs(rate)
        while (requests<1) or (requests<rate-1) or (requests>rate+1):
            requests = poisson.rvs(rate)
        print ("Requests for this interval: " + str(requests))

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            loop = asyncio.get_event_loop()
            response = []
            st = []
            for i in range(requests):
                if i==0:
                    st.append(random.expovariate(0.5))
                else:
                    st.append(st[i-1] + random.expovariate(0.5))
                    if ((st[i]>29)):
                        st[i] = random.expovariate(0.5)
                    elif (st[i]>29):    
                        st.append(st[i]+random.expovariate(0.5))   
                print (st[i])
            futures = [
                loop.run_in_executor(
                    executor,
                    post_request,
                    st[i],
                )
                for i in range(requests)
            ]
            log.info('waiting for executor tasks')
            completed, pending = await asyncio.wait(futures)
            results = [t.result() for t in completed]
            log.info('results: {!r}'.format(results))
            log.info('exiting')


def post_request(n):
    time.sleep(n)
    log = logging.getLogger('blocks({})'.format(n))
    n = str(random.randint(1, 3))
    img = "n.png"   #"n" + n + ".jpg"

    #TODO get position from IMU read position.txt while running Takaklas script for localization with steps. Dont forget callibration.
    #TODO ask for offloading first based to signal strength and position. Dont forget script for change of wifi and measurement of signal strength.
    #TODO if response from controller is offload, then offload, otherwise execute locally.
    #TODO per interval gather stats for all requests 
    files = {"file": open("./" + img, "rb")}
    post_url = "http://0.0.0.0:8000/offload"
    r = requests.post(post_url, files=files)
    #post_url = "http://0.0.0.0:8000/ask"
    #payload = {"x": 5,"y": 10,"signal_strength" : 60}
    #r = requests.post(post_url, json=payload)
    print (r.text)
    print (r)
    #log.info('done')

if __name__ == "__main__":
    main()
