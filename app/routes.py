import os 
import json
import yaml
import requests
import time
import random
from flask import Flask 
from app import app , db
from flask import request, Response, jsonify
from sqlalchemy import event
from app.models import Kalman, Stats
from sqlalchemy.sql.expression import func
from functools import reduce
from werkzeug.utils import secure_filename

CONFIG = yaml.load(open("./app/config.yaml"))
Q = CONFIG["settings"]["Q"]
R = CONFIG["settings"]["R"]
P0 = CONFIG["settings"]["P0"]
X0 = CONFIG["settings"]["X0"]
total_requests = CONFIG["settings"]["total_requests"]
ips = CONFIG["settings"]["ips"]
accepted_signal_strength = CONFIG["settings"]["accepted_signal_strength"]
placement_requests = CONFIG["settings"]["placement_requests"]
placement = CONFIG["settings"]["placement"]
workload_per_vdu = CONFIG["settings"]["workload_per_vdu"]
accepted_regions_of_transmission = CONFIG["settings"]["accepted_regions_of_transmission"]


@app.route("/db")
def initialize_db():
    # initialize Kalman Filter 
    u = Kalman(Q=Q,R=R,X0=X0,P0=P0,z=0,placement=0)
    db.session.add(u)
    db.session.commit()
    l = Stats(requests_admitted = 0,requests_rejected = 0,requests_locally = 0,predicted_workload = 0,placement = 0,total_requests = 0,vdu1_requests = 0,vdu2_requests = 0,vdu3_requests = 0,average_computation_time_vdu1 = 0,average_computation_time_vdu2 = 0,average_computation_time_vdu3 =0)
    db.session.add(l)
    db.session.commit()
    return ("OK")
    
@app.route("/ask", methods = ['POST'])
def post():
    #admission control with position x,y < x_ad , y _ad the terittory we accept | and appropriate signal_strength
    a = (request.get_json())
    for key, value in a.items() :
        if key == "x" :
            x = int(value)
        elif key == "y" :
            y = int(value)
        elif key == "signal_strength" :
            signal_strength = int(value) 
    print (x,y,signal_strength)
    for item in accepted_regions_of_transmission:
        if (x > item[0][0] and x < item[1][0]) and (y > item[0][1] and y < item[1][1]):
            if signal_strength > accepted_signal_strength:
                return "offload"

    kalman = Kalman.query.first()
    z = kalman.z
    x0 = kalman.X0
    kalman.z = z + 1
    db.session.commit()
    p = db.session.query(func.max(Stats.id)).scalar()  
    s = Stats.query.filter_by(id=p).first()
    s.requests_locally = s.requests_locally + 1
    db.session.commit()
    return "locally"
@app.route("/offload",  methods = ['POST'])
def offload():
    kalman = Kalman.query.first()
    z = kalman.z
    x0 = kalman.X0
    kalman.z = z + 1
    print ("to z einai:"+str(z))
    db.session.commit()
    #x0 = 1000000000000
    if z <= x0:
        #TODO delete int after db upgrade 
        topology = int(kalman.placement)
        print (placement[topology])
        # TODO put it in db there is no need to calculate it every time
        sum=0   # maybe sum = x0 ?? please check
        d = [0] * 3
        for i in range(3): 
            sum += placement[topology][i] * workload_per_vdu[i] 
            d[i] = placement[topology][i] * workload_per_vdu[i] 
        p = map(lambda pc:pc/sum,d)
        c = reduce(lambda c, x: c+[c[-1]+x], p,[0])[1:]
        rand = random.uniform(0,1)
        host_id = next(i for i, v in enumerate(c) if v > rand)
        print ("To host id einai : "+str(host_id))
        start_time = time.time()
        resp = offload_to_vdu(host_id, request)
        comput_time = time.time() - start_time
        if resp == "Host unavailable.":
            return "locally"
        a = json.loads(resp.text)
        a = a["predictions"]
        for key, value in a.items() :
            if key == 'elapsed_time' :
                computation_time = float(value.split()[0]) # split to remove tag of seconds 
        #TODO queueing time -> computation time
        computation_time = comput_time

        #requests admitted 
        p = db.session.query(func.max(Stats.id)).scalar() 
        s = Stats.query.filter_by(id=p).first()
        s.requests_admitted = s.requests_admitted + 1
        #requests and computation for each vdu
        if host_id == 0 : 
            s.vdu1_requests = s.vdu1_requests + 1 
            s.average_computation_time_vdu1 = s.average_computation_time_vdu1 + computation_time
        elif host_id == 1 :
            s.vdu2_requests = s.vdu2_requests + 1 
            s.average_computation_time_vdu2 = s.average_computation_time_vdu2 + computation_time
        else: 
            s.vdu3_requests = s.vdu3_requests + 1 
            s.average_computation_time_vdu3 = s.average_computation_time_vdu3 + computation_time
        db.session.commit()
        
        return jsonify({'computation_time' : computation_time})
    else:
        p = db.session.query(func.max(Stats.id)).scalar() 
        s = Stats.query.filter_by(id=p).first()
        s.requests_rejected = s.requests_rejected + 1
        db.session.commit() 
        return "locally"

def offload_to_vdu(host_id, request):
    img = request.files['file']
    files = {"image": img}
    post_url = "http://" + ips[host_id]+ ":" + "5000" + "/predict"
    try:
        return requests.post(post_url, files=files, timeout=25)
    except (requests.Timeout, requests.ConnectionError):
        print('Host at ' + ips[host_id]  + ' unavailable.')
        return 'Host unavailable.'
        
if __name__ == "__main__":
    app.run(threaded=True)
