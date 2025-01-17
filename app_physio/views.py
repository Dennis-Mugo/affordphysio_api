from django.http import JsonResponse
from .models import PhysioLocation, PhysioUser, PhysioSchedule, PostVisit
from app_admin.models import EmailToken
from patient.models import Appointment, PatientFeedback, Patient, PatientLocation
from patient.serializers import AppointmentSerializer, PatientFeedbackSerializer, AppointmentCancellationSerializer, PatientLocationSerializer, PatientSerializer
from app_admin.serializers import EmailTokenSerializer
from .serializers import PhysioLocationSerializer, PhysioUserSerializer, PhysioScheduleSerializer, PostVisitSerializer
from app_admin.service import get_password_reset_link_physio
from .service import add_physio_log, get_patient_detail_appointments, get_email_verification_link

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
                'dennismthairu@gmail.com',
                [email],
                fail_silently=False,
            )
            res["data"] = {"success": True}
            res["errors"] = []
            return Response(res, status=status.HTTP_200_OK)
        

        data = request.data | {"username": request.data["first_name"] + request.data["last_name"], "password": "amref"}
        serializer = PhysioUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            send_mail(
                'Afford Physio Email verification',
                f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
                'dennismthairu@gmail.com',
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
        user = get_object_or_404(PhysioUser, email=email)
        user.set_password(request.data['password'])
        user.save()
        serializer = PhysioUserSerializer(user)
        res["data"] = serializer.data
        res["status"] = 201
        return Response(res, status=status.HTTP_201_CREATED)
    
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
        user = get_object_or_404(PhysioUser, email=email)
        # Send email with link to take them to forgot password page
        password_change_link = get_password_reset_link_physio(email)
        send_mail(
            'Afford Physio Password Reset',
            f'Follow the link below to change your password\n\n{password_change_link}\n\n The link expires in 10 minutes.',
            'dennismthairu@gmail.com',
            [email],
            fail_silently=False,
        )
        res["data"] = {"success": True}
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
        user = get_object_or_404(PhysioUser, email=email)
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
        user = get_object_or_404(PhysioUser, email=request.data['email'])
        
        if not user.is_active:
            res["errors"].append("This account has been deleted!")
            res["status"] = 404
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        

        if not user.check_password(request.data['password']):
            res["errors"].append("Password is incorrect")
            res["status"] = 404
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        serializer = PhysioUserSerializer(instance=user)

        log = add_physio_log("Logged in", user)
        if log != True:
            print(log)
            res["errors"].append(log)
            res["status"] = 500
            return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        res["data"] = {'token': token.key, 'user': serializer.data}
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
        serializer = PhysioUserSerializer(instance=request.user)
        res["data"] = {'user': serializer.data}
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        log = add_physio_log("Logged out", request.user)
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
def physio_profile(request, physioId):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        user = get_object_or_404(PhysioUser, id=physioId)

        if request.method == "GET":
            serializer = PhysioUserSerializer(instance=user)
            res["data"] = serializer.data
            return Response(res, status=status.HTTP_200_OK)
        
        elif request.method == "PUT":
            serializer = PhysioUserSerializer(user, request.data, partial=True)
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


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_feedback(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        physio = request.user
        feedback_list = PatientFeedback.objects.filter(physiotherapist=physio)
        serializer = PatientFeedbackSerializer(feedback_list, many=True)
        data = get_patient_detail_appointments(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT","POST", "PATCH"])
def appointments(request):
    # if request.method == "PUT":
    #     data = request.data
    #     patient = get_object_or_404(Patient, id=data["patientId"])
    #     obj = {
    #         "patient": patient,
    #         "timestamp": datetime.datetime.fromtimestamp(data["timestamp"]),
    #         "status": data["status"],
    #         "appointment_type": data["appointmentType"]
    #     }
    #     serializer = AppointmentSerializer(data=obj)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # elif request.method == "POST":
    #     patient = get_object_or_404(Patient, id=request.data["patientId"])
    #     appointments = Appointment.objects.filter(patient=patient)
    #     serializer = AppointmentSerializer(appointments, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        if request.method == "PATCH":
            appointment_id = request.data["appointmentId"]
            appointment = get_object_or_404(Appointment, id=appointment_id)
            serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
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
def cancel_appointment(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        data = request.data
        appointment = get_object_or_404(Appointment, id=data["appointmentId"])
        physio = get_object_or_404(PhysioUser, id=data["physioId"])
        patient = get_object_or_404(Patient, id=data["patientId"])

        
        serializer = AppointmentSerializer(appointment)
        date_scheduled = serializer.data['timestamp']
        dt_scheduled = datetime.datetime.fromisoformat(date_scheduled.replace('Z', '+00:00'))

        epoch_scheduled_seconds = dt_scheduled.timestamp()
        now_epoch_seconds = int(time.time())

        appointment_cancel_duration = 6 * 60 * 60 #Appointment can only be cancelled more than 6 hours prior
        is_penalty = epoch_scheduled_seconds - now_epoch_seconds < appointment_cancel_duration

        # if is_penalty:
        #     serializer = PenaltySerializer(data={
        #         "penalty_type": "early_cancellation",
        #         "duration": epoch_scheduled_seconds - now_epoch_seconds,
        #         "fine_percentage": 30
        #     })
        #     if serializer.is_valid():
        #         serializer.save()
                

        cancel_obj = {
            "timestamp": datetime.datetime.fromtimestamp(data["timestamp"]),
            "reason": data["reason"],
            "appointment": data["appointmentId"]
        }
        # if is_penalty:
        #     cancel_obj["penalty"] = serializer.data["id"] 
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
            # if is_penalty: obj["penalty"] = 30
            send_mail(
            'Afford Physio Appointment Cancellation',
            f'Your appointment with {physio.first_name + " " + physio.last_name} has been cancelled due to the following reason:\n\n{data["reason"]}',
            'dennismthairu@gmail.com',
            [patient.email],
            fail_silently=False,
        )
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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_schedule(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        physio = request.user
        data = request.data
        request.data["physio"] = physio
        # request.data["date"] = datetime.date.fromtimestamp(data["dateTimestamp"])
        request.data["date"] = data["dateTimestamp"]
        request.data["start_time"] = datetime.time(hour=data["startTime"]["hour"], minute=data["startTime"]["minute"])
        request.data["end_time"] = datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"])

        serializer = PhysioScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res["data"] = serializer.data
            return Response(res, status=status.HTTP_200_OK)
        else:
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_schedule(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        physio = request.user
        schedule_list = PhysioSchedule.objects.filter(physio=physio)
        serializer = PhysioScheduleSerializer(schedule_list, many=True)
        res["data"] = serializer.data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_incoming_appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        physio = request.user
        appointments = Appointment.objects.filter(physiotherapist=physio, status="pending")
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_patient_detail_appointments(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_accepted_appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        physio = request.user
        appointments = Appointment.objects.filter(physiotherapist=physio, status="accepted")
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_patient_detail_appointments(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_completed_appointments(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }
    try:
        physio = request.user
        appointments = Appointment.objects.filter(physiotherapist=physio, status="completed")
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_patient_detail_appointments(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def reschedule_appointment(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        appointment_id = request.data["appointmentId"]
        appointment = get_object_or_404(Appointment, id=appointment_id)
        data = request.data
        if "startTime" in data and "endTime" in data and "dateTimestamp" in data:
            # request.data["date"] = datetime.date.fromtimestamp(data["dateTimestamp"])
            # request.data["start_time"] = datetime.time(hour=data["startTime"]["hour"], minute=data["startTime"]["minute"])
            # request.data["end_time"] = datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"])
            
            request.data["timestamp"] = datetime.datetime.fromtimestamp(data["dateTimestamp"] + \
            (data["startTime"]["hour"] * 60 * 60) + \
            (data["startTime"]["minute"] * 60))
            request.data["end_time"] = datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"])
            serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res["data"] = serializer.data
                return Response(res, status=status.HTTP_200_OK)
            
            res["errors"] += [err for lst in serializer.errors.values() for err in lst]
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        else:
            res["errors"].append("One of the required field values is missing")
            res["status"] = 400
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def add_post_visit(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        data = request.data
        patient = get_object_or_404(Patient, email=data["patientEmail"])
        physio = get_object_or_404(PhysioUser, id=data["physioId"])
        data["follow_up_date"] = datetime.date.fromtimestamp(data["followUpDate"])
        data["treatment_plan"] = data["treatmentPlan"]
        data["pain_management"] = data["painManagement"]
        data["physio"] = physio
        data["patient"] = patient.id
        serializer = PostVisitSerializer(data=data)
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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_post_visit(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        physio = request.user
        post_visits = PostVisit.objects.filter(physio=physio)
        serializer = PostVisitSerializer(post_visits, many=True)
        data = get_patient_detail_appointments(serializer.data)
        res["data"] = data
        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def get_patient_locations(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        
        locations = PatientLocation.objects.all()
        serializer = PatientLocationSerializer(locations, many=True)
        res["data"] = serializer.data
        
        for location in res["data"]:
            patient = get_object_or_404(Patient, id=location["patient"])
            patient_serializer = PatientSerializer(patient)
            location["patient"] = patient_serializer.data

        

        return Response(res, status=status.HTTP_200_OK)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def add_physio_location(request):
    res = {
        "data": {},
        "errors": [],
        "status": 200
    }

    try:
        data = request.data
        physio = get_object_or_404(PhysioUser, id=data["physioId"])
        data["physio"] = physio
        #Check if physio already has a location
        location = PhysioLocation.objects.filter(physio=physio)

        # if location exists, update it
        if location.exists():
            location = location.first()
            serializer = PhysioLocationSerializer(location, data=data, partial=True)
            # serializer = PhysioLocationSerializer(data=data)
        else:
            serializer = PhysioLocationSerializer(data=data)


        if serializer.is_valid():
            serializer.save()
            res["data"] = serializer.data
            res["data"]["physio"] = PhysioUserSerializer(physio).data
            res["status"] = 201
            return Response(res, status=status.HTTP_201_CREATED)
        
        res["errors"] += [err for lst in serializer.errors.values() for err in lst]
        res["status"] = 400
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        res["errors"].append(str(e))
        res["status"] = 500
        return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)