from app import db

class Kalman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Q = db.Column(db.Float, index=True)
    R = db.Column(db.Float, index=True)
    X0 = db.Column(db.Float, index=True)
    P0 = db.Column(db.Float, index=True)
    z = db.Column(db.Float, index=True)
    placement = db.Column(db.Integer, index=True) # operating vdu's for next interval
    


class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True) #intervals
    requests_admitted = db.Column(db.Float, index=True) # requests accepted for offloading
    requests_rejected = db.Column(db.Float, index=True) # requests that are above predicted workload
    requests_locally = db.Column(db.Float, index=True)  # requests that are out of accepted position or signal strength
    predicted_workload = db.Column(db.Float, index=True) # at each interval
    placement = db.Column(db.String(64), index=True) # operating vdu's for this interval
    total_requests = db.Column(db.Float, index=True) # addmitted + rejected + locally ??
    vdu1_requests = db.Column(db.Float, index=True) 
    vdu2_requests = db.Column(db.Float, index=True)
    vdu3_requests = db.Column(db.Float, index=True)
    average_computation_time_vdu1 = db.Column(db.Float, index=True)
    average_computation_time_vdu2 = db.Column(db.Float, index=True)
    average_computation_time_vdu3 = db.Column(db.Float, index=True)