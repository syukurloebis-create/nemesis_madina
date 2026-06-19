import math
from datetime import datetime

def time_decay(event_time):
    days = (datetime.utcnow() - event_time).days
    return math.exp(-days / 365)