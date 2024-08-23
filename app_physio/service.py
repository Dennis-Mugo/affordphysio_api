import time
import datetime
from .serializers import PhysioLogSerializer
from patient.models import Patient
from patient.serializers import PatientSerializer
from django.shortcuts import get_object_or_404


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

def get_patient_detail_appointments(logs):
    cache = {}
    res = []
    for log in logs:
        patient_id = log['patient']
        if patient_id in cache:
            log['patient'] = cache[patient_id]
        else:
            patient = get_object_or_404(Patient, id=patient_id)
            serializer = PatientSerializer(instance=patient)
            log['patient'] = serializer.data
            cache[patient_id] = serializer.data
        res.append(log)
    return res