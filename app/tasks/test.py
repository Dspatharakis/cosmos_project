import celery
import yaml
from sqlalchemy.sql.expression import func
from app import app , db
from app.models import Kalman, Stats

CONFIG = yaml.load(open("./app/config.yaml"))
placement = CONFIG["settings"]["placement"]
placement_requests = CONFIG["settings"]["placement_requests"]

@celery.task()
def update_kalman_placement():
    kalman = Kalman.query.first()
    ###TODO accumulate stats for this interval
    p = db.session.query(func.max(Stats.id)).scalar() 
    s = Stats.query.filter_by(id=p).first()
    s.placement = kalman.placement
    s.requests = s.requests_admitted + s.requests_rejected
    s.predicted_workload = kalman.X0
    s.average_computation_time_vdu1 = s.average_computation_time_vdu1 / s.vdu1_requests
    s.average_computation_time_vdu2 = s.average_computation_time_vdu1 / s.vdu2_requests
    s.average_computation_time_vdu3 = s.average_computation_time_vdu1 / s.vdu3_requests
    # start of kalman update
    Q = kalman.Q 
    p0 = kalman.P0
    x0 = kalman.X0
    R = kalman.R
    z = kalman.z
    # z is given by the actual requests processed in this interval 
    xkp = x0 
    pkp = p0 + Q 
    Kk = pkp / (pkp + R)
    xke = xkp + Kk * (z - xkp)
    pk = ( 1 - Kk ) * pkp 
    x0 = xke # return please
    p0 = pk   # return please
    print ("new X0 for Kalman: " + str(x0) )
    print ("new P0 for Kalman: " + str(p0) )
    kalman.X0 = x0    # x0 are the requests predicted for the next interval!!
    kalman.P0 = p0
    kalman.z = 0
    # choose proper placement for load balancing
    for item in placement_requests:
        if x0 <= item:
            topology = placement_requests.index(item)
            break
    print ("new topology index for the next interval:" + str(topology))
    kalman.placement = topology
    db.session.commit()
    # new interval new stats
    l = Stats(requests_admitted = 0,requests_rejected = 0,requests_locally = 0,predicted_workload = 0,placement = 0,total_requests = 0,vdu1_requests = 0,vdu2_requests = 0,vdu3_requests = 0,average_computation_time_vdu1 = 0,average_computation_time_vdu2 = 0,average_computation_time_vdu3 =0)
    db.session.add(l)
    db.session.commit()
    
    

