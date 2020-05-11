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
import csv
from scipy.stats import poisson
import threading 

MINUTE = 60
WAIT_SECONDS = 30

first_start_time = time.time()

def stop():
    print ("STOP")


def main():
    #first_start_time = time.time()
    rate = int(sys.argv[1])
    print (rate)
    upper_bound = int(sys.argv[2])
    time_to_run = int(sys.argv[3])

    interval_counter = 0
    counter  = 1
    if (rate==upper_bound):
        variance = 1
    else:
        variance = 0

    while (time.time() - first_start_time) < time_to_run * MINUTE:
        if (interval_counter % 10 == 0) and (interval_counter>0) and (counter == 0):
            counter = 1
	# check for up or down
            if (variance==0):
                rate += 2
            else:
                rate -= 2
            if (rate <= 2):
                variance = 0
            if (rate >= upper_bound):
                variance = 1
        elif ((interval_counter + 1) % 10 == 0) and (interval_counter>0) and (counter == 1):
            counter = 0

        if (time.time()- first_start_time  > interval_counter*30):
            print (rate) 
            logging.basicConfig(
                    level=logging.CRITICAL,
                    format='%(threadName)10s %(name)18s: %(message)s',
                    stream=sys.stderr,
                )
            loop = asyncio.get_event_loop()
            loop.call_later(30, stop)
            task = loop.create_task(post(rate))

            #loop.run_until_complete(post(rate))
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass

            interval_counter += 1

async def post(rate):
        log = logging.getLogger('run_blocking_tasks')
        log.info('starting')
        log.info('creating executor tasks')
        requests = poisson.rvs(rate)
        while (requests<1) or (requests < rate ) or (requests>rate+1):
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
                #print (st[i])
            futures = [
                loop.run_in_executor(
                    executor,
                    post_request,
                    st[i],
                )
                for i in range(requests)
            ]
            log.info('waiting for executor tasks')
            completed, pending = await asyncio.wait(futures, timeout = 30)
            results = [t.result() for t in completed]
            log.info('results: {!r}'.format(results))
            log.info('exiting')


def post_request(n):
    time.sleep(n)
    log = logging.getLogger('blocks({})'.format(n))
    
    #TODO send random image from pool

    n = str(random.randint(1, 31))
    img = "test_images/" + n + ".png"

    #TODO generate two random numbers for position and one for signal strength

    post_url = "http://192.168.247.91:8000/ask"
    payload = {"x": 5,"y": 10,"signal_strength" : 60}
    r = requests.post(post_url, json=payload)
    #print (r.text)
    if r.text == "offload":
        files = {"file": open("./" + img, "rb")}
        start_time = time.time()
        post_url = "http://192.168.247.91:8000/offload"
        r = requests.post(post_url, files=files)
        if r.text != "locally":
            response_time = time.time()-start_time
            a = json.loads(r.text)
            for key, value in a.items() :
                if key == "computation_time" :
                    computation_time = float(value)
            filename = "./requests1.txt"
            with open(filename, 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([round(response_time,5),round(computation_time,5),round((response_time-computation_time),5)])
        else: 
            print ("local execution")

    else :
        print ("local execution")

if __name__ == "__main__":
    main()
