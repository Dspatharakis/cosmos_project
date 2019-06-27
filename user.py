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

MINUTE = 60
TIME_TO_RUN = 120 
def main():
    first_start_time = time.time()
    interval_counter = 0
    rate = 1
    while (time.time() - first_start_time) < TIME_TO_RUN * MINUTE:
        if (time.time()- first_start_time  > interval_counter*30):
            print ("interval time:"+str(time.time()-first_start_time))
            if interval_counter > 0 :  
                filename = "./requests.txt"
                with open(filename, 'r') as f:
                    reader = csv.reader(f)
                    stats = list(reader)
                print (stats) 
                open(filename, 'w').close()
                average_response_time = 0 
                average_computation_time = 0 
                average_transmission_time = 0
                counter = 0  
                for item in stats:
                    average_response_time += float(item[0])
                    average_computation_time += float(item[1])
                    average_transmission_time += float(item[2])
                    counter += 1 
                average_response_time = average_response_time / counter
                average_transmission_time = average_transmission_time / counter 
                average_computation_time = average_computation_time / counter 
                filename = "./interval_stats.txt"
                with open(filename, 'a') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    # If opened for the first time, insert header row
                    if os.path.getsize(filename) == 0:
                        wr.writerow(["number_of_requests","average_response_time", "average_computation_time","average_transmission_time"])
                    wr.writerow([counter,round(average_response_time,5),round(average_computation_time,5),round(average_transmission_time,5)])

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
    
    n = str(random.randint(1, 31))
    img = n + ".png"

    
    #TODO generate two random numbers for position and one for signal strength

    post_url = "http://0.0.0.0:8000/ask"
    payload = {"x": 5,"y": 10,"signal_strength" : 60}
    r = requests.post(post_url, json=payload)
    print (r.text)
    if r.text == "offload":
        files = {"file": open("./" + img, "rb")}
        start_time = time.time()
        post_url = "http://0.0.0.0:8000/offload"
        r = requests.post(post_url, files=files)
        if r.text != "locally":
            response_time = time.time()-start_time
            a = json.loads(r.text)
            for key, value in a.items() :
                if key == "computation_time" :
                    computation_time = float(value)
            filename = "./requests.txt"
            with open(filename, 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([round(response_time,5),round(computation_time,5),round((response_time-computation_time),5)])
        else: 
        print ("local execution")

    else :
        print ("local execution")

if __name__ == "__main__":
    main()
