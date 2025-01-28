from django.http import JsonResponse

from app_physio.service import calculate_review_stats
from patient.mpesa_service import send_stk_push
from .models import MPesaPayment, Patient, PatientFeedback, Appointment, PatientLocation, Payment
from app_admin.models import EmailToken, EducationResource, ServiceProvided
from app_physio.models import PhysioLocation, PhysioUser, PhysioSchedule
from app_physio.serializers import PhysioLocationSerializer, PhysioUserSerializer, PhysioScheduleSerializer
from app_admin.serializers import EmailTokenSerializer, EdResourceSerializer, ServiceSerializer
from .serializers import MPesaPaymentSerializer, PatientLocationSerializer, PatientSerializer, PatientFeedbackSerializer, AppointmentSerializer, AppointmentCancellationSerializer, PenaltySerializer, PaymentSerializer
from .service import get_email_verification_link, get_password_reset_link, add_patient_log, get_physio_detail_feedback, get_physios_from_ids

from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
import datetime
import pytz
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("EMAIL_HOST_USER")

response_format = {
    "data": {},
    "errors": [],
    "status": 200
}


@api_view(["POST"])
def signup_verify(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        is_resend = request.data.get("isResend", False)
        email = request.data["email"]
        verify_link = get_email_verification_link(email)
        if is_resend:
            #User data is saved but user wants to resend verification email
            send_mail(
                'Afford Physio Email verification',
                f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
                sender_email,
                [email],
                fail_silently=False,
            )
            res["data"] = {"success": True}
            res["errors"] = []
            return Response(res, status=status.HTTP_200_OK)
        

        data = request.data | {"username": request.data["first_name"] + request.data["last_name"], "password": "amref"}
        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # user = Patient.objects.get(email=request.data['email'])
            # user.set_password("password")
            # user.save()
            # token = Token.objects.create(user=user) 
            send_mail(
                'Afford Physio Email verification',
                f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
                sender_email,
                [request.data['email']],
                fail_silently=False,
            )
            res["data"] = {"success": True}
            res["status"] = 201
            res["errors"] = []
            return Response(res, status=status.HTTP_201_CREATED)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def signup_set_password(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        email = request.data["email"]
        first_name = request.data["firstName"]
        surname = request.data["surname"]
        password = request.data["password"]
        home_address = request.data["homeAddress"]
        phone_number = request.data["phoneNumber"]

        
        #Check if user with this email exists
        user = Patient.objects.filter(email=email)
        if user.exists():
            res["errors"].append("A user with that email already exists.")
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


        username = first_name + surname

        serializer = PatientSerializer(data={
            "first_name": first_name,
            "last_name": surname,
            "email": email,
            "username": username,
            "home_address": home_address,
            "phone_number": phone_number
        })

    

        if serializer.is_valid():
            serializer.save()
            #Set the password
            user = Patient.objects.get(email=email)
            user.set_password(password)
            user.save()

            res["data"] = serializer.data
            res["errors"] = []
            res["status"] = 201
            return Response(res, status=status.HTTP_201_CREATED)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def forgot_password_send_email(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try: 
        email = request.data["email"]
        print(sender_email)
        user = get_object_or_404(Patient, email=email)
        # Send email with link to take them to forgot password page
        password_change_link = get_password_reset_link(email)
        send_mail(
            'Afford Physio Password Reset',
            f'Follow the link below to change your password\n\n{password_change_link}\n\n The link expires in 10 minutes.',
            sender_email,
            [email],
            fail_silently=False,
        )
        res["data"] = {"success": True}
        res["errors"] = []
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def reset_password(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        email = request.data["email"]
        new_password = request.data["password"]
        user = get_object_or_404(Patient, email=email)
        user.set_password(new_password)
        user.save()
        res["data"] = {"success": True}
        return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def login(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        user = get_object_or_404(Patient, email=request.data['email'])
        
        if not user.check_password(request.data['password']):
            res["errors"].append("Password is incorrect")
            res["status"] = 404
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        serializer = PatientSerializer(instance=user)

        log = add_patient_log("Logged in", user)
        if log != True:
            print(log)
            res["errors"].append(log)
            res["status"] = 500
            return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        res["data"] = {"token": token.key, "user": serializer.data}
        res["status"] = 201
        return Response(res, status=status.HTTP_201_CREATED)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        serializer = PatientSerializer(instance=request.user)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 403
        return Response(res, status=status.HTTP_403_FORBIDDEN)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])

@permission_classes([IsAuthenticated])

def logout(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        request.user.auth_token.delete()
        log = add_patient_log("Logged out", request.user)
        if log != True:
            print(log)
            res["errors"].append(log)
            res["status"] = 500
            return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        res["data"] = {"success": True}
        return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET", "PUT"])
def patient_profile(request, patientId):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        user = get_object_or_404(Patient, id=patientId)

        if request.method == "GET":
            serializer = PatientSerializer(instance=user)
            res["data"] = serializer.data
            return Response(res, status=status.HTTP_200_OK)
        
        elif request.method == "PUT":
            serializer = PatientSerializer(user, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res["data"] = serializer.data
                res["status"] = 201
                return Response(res, status=status.HTTP_201_CREATED)
            
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def verify_email_token(request, tokenId):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        token = get_object_or_404(EmailToken, id=tokenId)
        serializer = EmailTokenSerializer(token)
        date_created = serializer.data['date_created']

        dt_created = datetime.datetime.fromisoformat(date_created.replace('Z', '+00:00'))

        epoch_created_seconds = dt_created.timestamp()
        now_epoch_seconds = int(time.time())
        
        token_expiry_duration = 10 * 60 #Token expires in 10 minutes
        token_valid = now_epoch_seconds - epoch_created_seconds < token_expiry_duration

        res["data"] = {"valid": token_valid}
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
def add_feedback(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        data = request.data
        data_obj = {
            "patient": get_object_or_404(Patient, id=data["patientId"]),
            "physiotherapist": get_object_or_404(PhysioUser, id=data["physioId"]),
            "comments": data.get('comments', "False"),
            "rating": data["rating"],
            "timestamp": datetime.datetime.fromtimestamp(data["timestamp"])  
        }
        
        serializer = PatientFeedbackSerializer(data=data_obj)
        if serializer.is_valid():
            serializer.save()
            res["data"] = {"success": True}
            res["status"] = 201
            return Response(res, status=status.HTTP_201_CREATED)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def get_feedback(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        patient_id = request.data["patientId"]
        patient = get_object_or_404(Patient, id=patient_id)
        feedback_list = PatientFeedback.objects.filter(patient=patient)
        serializer = PatientFeedbackSerializer(feedback_list, many=True)
        data = get_physio_detail_feedback(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT","POST", "PATCH"])
def appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        if request.method == "PUT":
            data = request.data
            patient = get_object_or_404(Patient, id=data["patientId"])
            physio = get_object_or_404(PhysioUser, id=data["physioId"])
            obj = {
                "patient": patient,
                "physiotherapist": physio,
                "timestamp": datetime.datetime.fromtimestamp(data["dateTimestamp"] + \
                (data["startTime"]["hour"] * 60 * 60) + \
                (data["startTime"]["minute"] * 60)),
                "end_time": datetime.time(hour = data["endTime"]["hour"], minute = data["endTime"]["minute"]),
                "status": data["status"],
                "appointment_type": data["appointmentType"]
            }
            serializer = AppointmentSerializer(data=obj)
            if serializer.is_valid():
                serializer.save()
                send_mail(
                    'Afford Physio Appointment Confirmation',
                    f'You have successfully created an appointment with Dr. {physio.first_name} {physio.last_name}.\n\n Your appointment is in review and you will be notified once it is accepted.\n\n Thank you for choosing Afford Physio.',
                    sender_email,
                    [patient.email],
                    fail_silently=False,
                )
                res["data"] = serializer.data
                res["status"] = 201
                return Response(res, status=status.HTTP_201_CREATED)
            
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == "POST":
            patient = get_object_or_404(Patient, id=request.data["patientId"])
            appointments = Appointment.objects.filter(patient=patient)
            serializer = AppointmentSerializer(appointments, many=True)
            data = get_physio_detail_feedback(serializer.data)
            res["data"] = data
            return Response(res, status=status.HTTP_200_OK)
        
        elif request.method == "PATCH":
            # patient_id = request.data["patientId"]
            data = request.data
            appointment_id = data["appointmentId"]
            appointment = get_object_or_404(Appointment, id=appointment_id)
            
            obj = {
                "timestamp": datetime.datetime.fromtimestamp(data["dateTimestamp"] + \
                (data["startTime"]["hour"] * 60 * 60) + \
                (data["startTime"]["minute"] * 60)),
                "end_time": datetime.time(hour = data["endTime"]["hour"], minute = data["endTime"]["minute"]),
                "status": data["status"],
                "appointment_type": data["appointmentType"]
            }
            serializer = AppointmentSerializer(appointment, data=obj, partial=True)
            if serializer.is_valid():
                serializer.save()
                res["data"] = serializer.data
                return Response(res, status=status.HTTP_200_OK)
            
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
def get_upcoming_appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        patient = get_object_or_404(Patient, id=request.data["patientId"])
        #Check if appointment status=accepted and is in the future
        appointments = Appointment.objects.filter(patient=patient, timestamp__gte=datetime.datetime.now(), status="accepted")
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_physio_detail_feedback(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def get_completed_appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        patient = get_object_or_404(Patient, id=request.data["patientId"])
        #Check if appointment status=completed
        appointments = Appointment.objects.filter(patient=patient, status="completed")
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_physio_detail_feedback(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def cancel_appointment(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        data = request.data
        appointment = get_object_or_404(Appointment, id=data["appointmentId"])

        if appointment.patient.id != int(data["patientId"]):
            res["errors"].append("This appointment does not belong to this patient")
            res["status"] = 403
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AppointmentSerializer(appointment)
        date_scheduled = serializer.data['timestamp']
        dt_scheduled = datetime.datetime.fromisoformat(date_scheduled.replace('Z', '+00:00'))

        epoch_scheduled_seconds = dt_scheduled.timestamp()
        now_epoch_seconds = int(time.time())

        appointment_cancel_duration = 6 * 60 * 60 #Appointment can only be cancelled more than 6 hours prior
        is_penalty = epoch_scheduled_seconds - now_epoch_seconds < appointment_cancel_duration

        

        if is_penalty:
            serializer = PenaltySerializer(data={
                "penalty_type": "early_cancellation",
                "duration": epoch_scheduled_seconds - now_epoch_seconds,
                "fine_percentage": 30
            })
            if serializer.is_valid():
                serializer.save()
            else:
                res["errors"] += [err for lst in serializer.errors.values() for err in lst]
                

        cancel_obj = {
            "timestamp": datetime.datetime.fromtimestamp(data["timestamp"]),
            "reason": data["reason"],
            "appointment": data["appointmentId"]
        }
        if is_penalty:
            cancel_obj["penalty"] = serializer.data["id"] 
        serializer = AppointmentCancellationSerializer(data=cancel_obj)

        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        
        serializer = AppointmentSerializer(appointment, data={"status": "cancelled"}, partial=True)

        if serializer.is_valid():
            serializer.save()
            obj = serializer.data
            if is_penalty: obj["penalty"] = 30
            res["data"] = obj
            return Response(res, status=status.HTTP_200_OK)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def get_schedule(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        physio_id = request.data["physioId"]
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        physio = get_object_or_404(PhysioUser, id=physio_id)
        schedule_list = PhysioSchedule.objects.filter(physio=physio, date__gte=today)
        serializer = PhysioScheduleSerializer(schedule_list, many=True)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_educational_resources(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        resources = EducationResource.objects.all()
        serializer = EdResourceSerializer(resources, many=True)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_services(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        services = ServiceProvided.objects.all()
        serializer = ServiceSerializer(services, many=True)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def add_payment(request):
    data = request.data
    data["timestamp"] = datetime.datetime.fromtimestamp(data["timestamp"])
    data["patient"] = data["patientId"]
    serializer = PaymentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def get_payments(request):
    patient_id = request.data.get("patientId", False)
    if not patient_id:
        return Response({"detail": "PatientId is missing"}, status=status.HTTP_400_BAD_REQUEST)
    payments = Payment.objects.filter(patient=patient_id)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data, status.HTTP_200_OK)

@api_view(["GET"])
def get_available_physios(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        schedules = PhysioSchedule.objects.filter(date__gte=today)
        serializer = PhysioScheduleSerializer(schedules, many=True)
        physio_ids = [physio["physio"] for physio in serializer.data]
        physio_ids = list(set(physio_ids))
        data = get_physios_from_ids(physio_ids)
        physio_serializer = PhysioUserSerializer(data, many=True)
        res["data"] = physio_serializer.data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def get_physio_locations(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        
        locations = PhysioLocation.objects.all()
        serializer = PhysioLocationSerializer(locations, many=True)
        res["data"] = serializer.data
        
        for location in res["data"]:
            physio = get_object_or_404(PhysioUser, id=location["physio"])
            physio_serializer = PhysioUserSerializer(physio)
            location["physio"] = physio_serializer.data

        

        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def add_patient_location(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        data = request.data
        patient = get_object_or_404(Patient, id=data["patientId"])
        data["patient"] = patient
        #Check if patient already has a location
        location = PatientLocation.objects.filter(patient=patient)

        # if location exists, update it
        if location.exists():
            location = location.first()
            serializer = PatientLocationSerializer(location, data=data, partial=True)
            # serializer = PatientLocationSerializer(data=data)
        else:
            serializer = PatientLocationSerializer(data=data)


        if serializer.is_valid():
            serializer.save()
            res["data"] = serializer.data
            res["data"]["patient"] = PatientSerializer(patient).data
            res["status"] = 201
            return Response(res, status=status.HTTP_201_CREATED)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def physios_near_me(request):
    #Get the patient's location
    # Get the physio locations
    # Calculate the distance between the patient and the physio
    # Return the physios within a certain radius
    # Return the physios in order of distance
    # Return the physios with their schedules
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        patient_id = request.data["patientId"]
        patient = get_object_or_404(Patient, id=patient_id)
        patient_location = get_object_or_404(PatientLocation, patient=patient)
        patient_lat = patient_location.latitude
        patient_lon = patient_location.longitude

        physio_locations = PhysioLocation.objects.all()
        serializer = PhysioLocationSerializer(physio_locations, many=True)
        data = serializer.data
        for location in data:
            physio = get_object_or_404(PhysioUser, id=location["physio"])
            physio_serializer = PhysioUserSerializer(physio)
            #Get the distance between the patient and the physio using euclidean distance
            physio_lat = location["latitude"]
            physio_lon = location["longitude"]
            distance = ((physio_lat - patient_lat) ** 2 + (physio_lon - patient_lon) ** 2) ** 0.5
            location["distance"] = distance

            

            location["physio"] = physio_serializer.data

        data = sorted(data, key=lambda x: x["distance"])
        #Get the first 5 physios
        data = data[:5]
        for location in data:
            physio = get_object_or_404(PhysioUser, id=location["physio"]["id"])
            feedbacks = PatientFeedback.objects.filter(physiotherapist=physio)
            feedback_serializer = PatientFeedbackSerializer(feedbacks, many=True)
            feedback_stats = calculate_review_stats(feedback_serializer)
            location["physio"]["feedback_stats"] = feedback_stats

        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)  

    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

@api_view(["POST"])
def validate_payment(request):

    accepted_result = {    
        "ResultCode": "0",
        "ResultDesc": "Accepted",
    }
    rejected_result = {
        "ResultCode": "C2B00011",
        "ResultDesc": "Rejected"
    }
    return Response(accepted_result, status=status.HTTP_200_OK)
    try:
        data = request.data
        print(data)
        print(json.dumps(data, indent=4))
        return Response(accepted_result, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        return Response(rejected_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def send_prompt(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        phone_number = request.data["phoneNumber"]
        patient_id = request.data["patientId"]
        amount = 1
        promptResult = send_stk_push(phone_number, amount)
        if promptResult.get("errorMessage", False):
            res["status"] = 400
            res["errors"].append(promptResult["errorMessage"])
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
        if promptResult.get("ResponseDescription", False):
            obj = {
                "request_id": promptResult["MerchantRequestID"],
                "checkout_id": promptResult["CheckoutRequestID"],
                "amount": amount,
                "phone_number": phone_number,
                "patient": patient_id,
                "status": "pending"
            }
            serializer = MPesaPaymentSerializer(data=obj)
            if serializer.is_valid():
                serializer.save()
            else:
                res["status"] = 400
                res["errors"] += [err for lst in serializer.errors.values() for err in lst]
                return Response(res, status=status.HTTP_400_BAD_REQUEST)
            
            res["status"] = 200
            res["data"] = {**promptResult, "paymentId": serializer.data["id"]}
            return Response(res, status=status.HTTP_200_OK)
        
        res["status"] = 500
        res["errors"].append(promptResult)
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    

@api_view(["POST"])
def confirm_payment(request):
    accepted_result = {    
        "ResultCode": "0",
        "ResultDesc": "Accepted",
    }
    rejected_result = {
        "ResultCode": "C2B00011",
        "ResultDesc": "Rejected"
    }
    
    
    try:
        data = request.data
        print(data)
        print(json.dumps(data, indent=4))

        obj = data["Body"]["stkCallback"]
        request_id = obj["MerchantRequestID"]
        checkout_id = obj["CheckoutRequestID"]
        result_code = obj["ResultCode"]

        if result_code == 0:
            payment = get_object_or_404(MPesaPayment, request_id=request_id, checkout_id=checkout_id)
            payment.status = "completed"
            payment.status_message = obj["ResultDesc"]
            payment.save()
            return Response(accepted_result, status=status.HTTP_200_OK)
        
        else:
            payment = get_object_or_404(MPesaPayment, request_id=request_id, checkout_id=checkout_id)
            payment.status = "failed"
            payment.status_message = obj["ResultDesc"]
            payment.save()
            
        return Response(accepted_result, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        return Response(rejected_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(["POST"])
def check_payment_status(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        payment_id = request.data["paymentId"]
        payment = get_object_or_404(MPesaPayment, id=payment_id)
        serializer = MPesaPaymentSerializer(payment)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)