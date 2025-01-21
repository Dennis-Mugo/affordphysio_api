client_url = "http://localhost:5173"
import time
import datetime
from .serializers import PhysioLogSerializer
from patient.models import Patient
from patient.serializers import PatientSerializer
from django.shortcuts import get_object_or_404
from app_admin.serializers import EmailTokenSerializer



def get_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"http://localhost:5173/physiotherapist/register/{email}/{token_id}"


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

def calculate_review_stats(serializer):
    #Calculate the average rating
    total_rating = 0
    for feedback in serializer.data:
        total_rating += feedback["rating"]
    
    average_rating = 0
    if len(serializer.data):
        average_rating = total_rating / len(serializer.data)
    #Set average_rating to one decimal place
    average_rating = round(average_rating, 1)
    # get the number of ratings
    num_ratings = len(serializer.data)
    # get the number of comments
    num_comments = 0
    for feedback in serializer.data:
        if feedback["comments"] != "False":
            num_comments += 1
    num_reviews = len(serializer.data)

    stars_count = [0, 0, 0, 0, 0]
    for feedback in serializer.data:
        stars_count[feedback["rating"] - 1] += 1

    

    res = {
        "average_rating": average_rating, 
        "num_ratings": num_ratings, 
        "num_comments": num_comments,
        "num_reviews": num_reviews,
        "num_5stars": stars_count[4],
        "num_4stars": stars_count[3],
        "num_3stars": stars_count[2],
        "num_2stars": stars_count[1],
        "num_1stars": stars_count[0]
    }
    return res