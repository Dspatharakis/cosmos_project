#!/usr/bin/env python3
import time
import random
import datetime
import sys
import os
import requests
import json
import csv

MINUTE = 60
TIME_TO_RUN = 120 
def main():
    while (True):
    #TODO fix the while condition 
        time.sleep(5)
        first_start_time = time.time()
        interval_counter = 0
        if (time.time()- first_start_time  > interval_counter*30):
            print ("interval time:"+str(time.time()-first_start_time))
            if interval_counter > 0 :  
                gather_stats()

        #TODO if positions.txt doesnt exist then x , y will be 0 , 0 
        with open('positions.txt', 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            print (last_line)
        result = [x.strip() for x in last_line.split(',')]
        x = float(result[0])
        y = float(result[1])

        n = str(random.randint(1, 31))
        img = "test_images/"+ n +".png"

        #TODO Dont forget script for change of wifi and measurement of signal strength.

        post_url = "http://10.1.10.180:8000/ask"
        payload = {"x": x,"y": y,"signal_strength" : 40}
        r = requests.post(post_url, json=payload)
        print (r.text)  
        if r.text == "offload":
            files = {"file": open("./" + img, "rb")}
            start_time = time.time()
            #post_url = "http://10.1.10.180:8000/offload"
            post_url = "http://0.0.0.0:5000/predict"
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
                start_time = time.time()
                files = {"image": open("./"+img,"rb")}
                post_url = "http://0.0.0.0:5000/predict"
                r = requests.post(post_url, files=files)
                response_time = time.time()-start_time
                a = json.loads(r.text)
                a = a["predictions"]
                for key, value in a.items() :
                    if key == 'elapsed_time' :
                        computation_time = float(value.split()[0]) # split to remove tag of seconds 
                filename = "./requests.txt"
                with open(filename, 'a') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerow([round(response_time,5),round(computation_time,5),round((response_time-computation_time),5)])

        else :
            print ("local execution")
            files = {"image": open("./"+img,"rb")}
            start_time = time.time()
            post_url = "http://0.0.0.0:5000/predict"
            r = requests.post(post_url, files=files)
            response_time = time.time()-start_time
            print (r.text)
            a = json.loads(r.text)
            a = a["predictions"]
            for key, value in a.items() :
                if key == 'elapsed_time' :
                    computation_time = float(value.split()[0]) # split to remove tag of seconds 
            filename = "./requests.txt"
            with open(filename, 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([round(response_time,5),round(computation_time,5),round((response_time-computation_time),5)])
        
        #TODO start server at PI script


    def gather_stats ():
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

if __name__ == "__main__":
    main()
