from app_admin.serializers import EmailTokenSerializer
from .serializers import PatientLogSerializer
import time
import datetime

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

