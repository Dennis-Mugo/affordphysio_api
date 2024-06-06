client_url = "http://localhost:5173"
import time
import datetime
from .serializers import PhysioLogSerializer

def add_physio_log(activity, physio):
    epoch_time = int(time.time())
    timestamp = datetime.datetime.fromtimestamp(epoch_time)  
    log_obj = {
        "activity": activity,
        "timestamp": timestamp,
        "physio": physio
    }
    serializer = PhysioLogSerializer(data=log_obj)
    if serializer.is_valid():
        serializer.save()
        return True
    return serializer.errors