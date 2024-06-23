from django.http import JsonResponse
from .models import PhysioUser, PhysioSchedule, PostVisit
from app_admin.models import EmailToken
from patient.models import Appointment, PatientFeedback, Patient
from patient.serializers import AppointmentSerializer, PatientFeedbackSerializer, AppointmentCancellationSerializer
from app_admin.serializers import EmailTokenSerializer
from .serializers import PhysioUserSerializer, PhysioScheduleSerializer, PostVisitSerializer
from app_admin.service import get_password_reset_link_physio
from .service import add_physio_log, get_patient_detail_appointments

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



@api_view(["POST"])
def signup_set_password(request):
    email = request.data["email"]
    user = get_object_or_404(PhysioUser, email=email)
    user.set_password(request.data['password'])
    user.save()
    serializer = PhysioUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def forgot_password_send_email(request):
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
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
def reset_password(request):
    email = request.data["email"]
    new_password = request.data["password"]
    user = get_object_or_404(PhysioUser, email=email)
    user.set_password(new_password)
    user.save()
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
def login(request):
    user = get_object_or_404(PhysioUser, email=request.data['email'])
    user.is_active = True
    user.save()
    if not user.check_password(request.data['password']):
        return Response({"detail": "Email or password is incorrect"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = PhysioUserSerializer(instance=user)

    log = add_physio_log("Logged in", user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    serializer = PhysioUserSerializer(instance=request.user)
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])

@permission_classes([IsAuthenticated])

def logout(request):
    request.user.auth_token.delete()
    log = add_physio_log("Logged out", request.user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["GET", "PUT"])
def physio_profile(request, physioId):
    user = get_object_or_404(PhysioUser, id=physioId)

    if request.method == "GET":
        serializer = PhysioUserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = PhysioUserSerializer(user, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def verify_email_token(request, tokenId):
    token = get_object_or_404(EmailToken, id=tokenId)
    serializer = EmailTokenSerializer(token)
    date_created = serializer.data['date_created']

    dt_created = datetime.datetime.fromisoformat(date_created.replace('Z', '+00:00'))

    epoch_created_seconds = dt_created.timestamp()
    now_epoch_seconds = int(time.time())
    
    token_expiry_duration = 10 * 60 #Token expires in 10 minutes
    token_valid = now_epoch_seconds - epoch_created_seconds < token_expiry_duration

    return Response({"valid": token_valid}, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_feedback(request):
    physio_id = request.data["physioId"]
    physio = get_object_or_404(PhysioUser, id=physio_id)
    feedback_list = PatientFeedback.objects.filter(physiotherapist=physio)
    serializer = PatientFeedbackSerializer(feedback_list, many=True)
    data = get_patient_detail_appointments(serializer.data)
    return Response(data, status=status.HTTP_200_OK)

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
    
    if request.method == "PATCH":
        appointment_id = request.data["appointmentId"]
        appointment = get_object_or_404(Appointment, id=appointment_id)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
def cancel_appointment(request):
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
        return Response(obj, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_schedule(request):
    physio = request.user
    data = request.data
    request.data["physio"] = physio
    request.data["date"] = datetime.date.fromtimestamp(data["dateTimestamp"])
    request.data["start_time"] = datetime.time(hour=data["startTime"]["hour"], minute=data["startTime"]["minute"])
    request.data["end_time"] = datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"])

    serializer = PhysioScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_schedule(request):
    physio = request.user
    schedule_list = PhysioSchedule.objects.filter(physio=physio)
    serializer = PhysioScheduleSerializer(schedule_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_incoming_appointments(request):
    physio = request.user
    appointments = Appointment.objects.filter(physiotherapist=physio, status="pending")
    serializer = AppointmentSerializer(appointments, many=True)
    data = get_patient_detail_appointments(serializer.data)
    return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_accepted_appointments(request):
    physio = request.user
    appointments = Appointment.objects.filter(physiotherapist=physio, status="accepted")
    serializer = AppointmentSerializer(appointments, many=True)
    data = get_patient_detail_appointments(serializer.data)
    return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
def reschedule_appointment(request):
    appointment_id = request.data["appointmentId"]
    appointment = get_object_or_404(Appointment, id=appointment_id)
    data = request.data
    if "startTime" in data and "endTime" in data and "dateTimestamp" in data:
        # request.data["date"] = datetime.date.fromtimestamp(data["dateTimestamp"])
        # request.data["start_time"] = datetime.time(hour=data["startTime"]["hour"], minute=data["startTime"]["minute"])
        # request.data["end_time"] = datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"])
        request.data["timestamp"] = datetime.datetime.fromtimestamp(data["dateTimestamp"] + \
        (data["startTime"]["hour"] * 60 * 60) + \
        (data["startTime"]["minute"] * 60), tz=pytz.timezone("Africa/Nairobi"))

        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "one of the required field values is missing"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
def add_post_visit(request):
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def get_post_visit(request):
    physio_id = request.data["physioId"]
    physio = get_object_or_404(PhysioUser, id=physio_id)
    post_visits = PostVisit.objects.filter(physio=physio)
    serializer = PostVisitSerializer(post_visits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




