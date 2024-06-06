from .serializers import EmailTokenSerializer
client_url = "http://localhost:5173"
from app_physio.models import PhysioUser
from .serializers import ManagerLogSerializer
from app_physio.serializers import PhysioUserSerializer 
from patient.models import Patient
from patient.serializers import PatientSerializer
from django.shortcuts import get_object_or_404
import datetime
import time

def add_manager_log(activity, manager):
    epoch_time = int(time.time())
    timestamp = datetime.datetime.fromtimestamp(epoch_time)  
    log_obj = {
        "activity": activity,
        "timestamp": timestamp,
        "manager": manager
    }
    serializer = ManagerLogSerializer(data=log_obj)
    if serializer.is_valid():
        serializer.save()
        return True
    return serializer.errors

def get_physio_detail(logs):
    cache = {}
    res = []
    for log in logs:
        physio_id = log['physio']
        if physio_id in cache:
            log['physio'] = cache[physio_id]
        else:
            physio = get_object_or_404(PhysioUser, id=physio_id)
            serializer = PhysioUserSerializer(instance=physio)
            log['physio'] = serializer.data
            cache[physio_id] = serializer.data
        res.append(log)
    return res

def get_patient_detail(logs):
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

