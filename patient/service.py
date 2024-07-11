from app_admin.serializers import EmailTokenSerializer
from .serializers import PatientLogSerializer
import time
import datetime
from django.shortcuts import get_object_or_404
from app_physio.serializers import PhysioUserSerializer
from app_physio.models import PhysioUser

def get_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"http://localhost:5173/patient/register/{email}/{token_id}"
    
def get_password_reset_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"http://localhost:5173/patient/resetpassword/{email}/{token_id}"
    
def add_patient_log(activity, patient):
    epoch_time = int(time.time())
    timestamp = datetime.datetime.fromtimestamp(epoch_time)  
    log_obj = {
        "activity": activity,
        "timestamp": timestamp,
        "patient": patient
    }
    serializer = PatientLogSerializer(data=log_obj)
    if serializer.is_valid():
        serializer.save()
        return True
    return serializer.errors

def get_physio_detail_feedback(logs):
    cache = {}
    res = []
    for log in logs:
        physio_id = log['physiotherapist']
        if physio_id in cache:
            log['physiotherapist'] = cache[physio_id]
        else:
            physio = get_object_or_404(PhysioUser, id=physio_id)
            serializer = PhysioUserSerializer(instance=physio)
            log['physiotherapist'] = serializer.data
            cache[physio_id] = serializer.data
        res.append(log)
    return res

def get_physios_from_ids(ids):
    result = []
    for id in ids:
        physio = get_object_or_404(PhysioUser, id=id)
        if physio.is_active:
            result.append(physio)
    return result
