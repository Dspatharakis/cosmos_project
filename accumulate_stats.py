#!/usr/bin/env python3
import time
import random
import datetime
import sys
import os
import requests
import logging
import json
import csv
import threading 

MINUTE = 60
TIME_TO_RUN = 120 
WAIT_TIME_SECONDS = 30

first_start_time = time.time()


def foo():
    filename = "./requests1.txt"
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        stats = list(reader)
    #print (stats) 
    open(filename, 'w').close()
    average_response_time = 0 
    average_computation_time = 0 
    average_transmission_time = 0
    counter = 0  
    delay = []
    for item in stats:
        average_response_time += float(item[0])
        average_computation_time += float(item[1])
        average_transmission_time += float(item[2])
        delay.append(float(item[3]))
        counter += 1 
    average_response_time = average_response_time / counter
    average_transmission_time = average_transmission_time / counter 
    average_computation_time = average_computation_time / counter 
    filename = "./interval_stats1.txt"
    with open(filename, 'a') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        # If opened for the first time, insert header row
        if os.path.getsize(filename) == 0:
            wr.writerow(["time","number_of_requests","average_response_time", "average_computation_time","average_transmission_time"])
        print (counter)
        wr.writerow([round(time.time()-first_start_time,3),counter,round(average_response_time,5),round(average_computation_time,5),round(average_transmission_time,5)])


    filename = "./requests_rejected.txt"
    rejected = 0 
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            stats2 = list(reader)
        rejected = 0
        for item in stats2:
            delay.append(float(item))
            rejected += 1
    except FileNotFoundError:
        print ("Nothing was rejected")

    filename = "./simulation.txt"
    with open(filename, 'a') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        # If opened for the first time, insert header row
        if os.path.getsize(filename) == 0:
            wr.writerow(["time","poisson_rate","expo"])
        delay = sorted(delay)
        wr.writerow([round(time.time()-first_start_time,3),counter+rejected, delay]) # should short the list of delay



def main():
    ticker = threading.Event()
    while not ticker.wait(WAIT_TIME_SECONDS):
        foo()


if __name__ == "__main__":
    main()

