from django.http import JsonResponse
from .models import Patient, PatientFeedback, Appointment, Payment
from app_admin.models import EmailToken, EducationResource, ServiceProvided
from app_physio.models import PhysioUser, PhysioSchedule
from app_physio.serializers import PhysioUserSerializer, PhysioScheduleSerializer
from app_admin.serializers import EmailTokenSerializer, EdResourceSerializer, ServiceSerializer
from .serializers import PatientSerializer, PatientFeedbackSerializer, AppointmentSerializer, AppointmentCancellationSerializer, PenaltySerializer, PaymentSerializer
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


@api_view(["POST"])
def signup_verify(request):
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
        return Response({"success": True}, status=status.HTTP_200_OK)
    

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
            'dennismthairu@gmail.com',
            [request.data['email']],
            fail_silently=False,
        )
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def signup_set_password(request):
    email = request.data["email"]
    user = get_object_or_404(Patient, email=email)
    user.set_password(request.data['password'])
    user.save()
    serializer = PatientSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def forgot_password_send_email(request):
    email = request.data["email"]
    user = get_object_or_404(Patient, email=email)
    # Send email with link to take them to forgot password page
    password_change_link = get_password_reset_link(email)
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
    user = get_object_or_404(Patient, email=email)
    user.set_password(new_password)
    user.save()
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
def login(request):
    user = get_object_or_404(Patient, email=request.data['email'])
    
    if not user.check_password(request.data['password']):
        return Response({"detail": "Email or password is incorrect"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = PatientSerializer(instance=user)

    log = add_patient_log("Logged in", user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    serializer = PatientSerializer(instance=request.user)
    return Response({"user": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])

@permission_classes([IsAuthenticated])

def logout(request):
    request.user.auth_token.delete()
    log = add_patient_log("Logged out", request.user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["GET", "PUT"])
def patient_profile(request, patientId):
    user = get_object_or_404(Patient, id=patientId)

    if request.method == "GET":
        serializer = PatientSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = PatientSerializer(user, request.data, partial=True)
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
def add_feedback(request):
    data = request.data
    data_obj = {
        "patient": get_object_or_404(Patient, id=data["patientId"]),
        "physiotherapist": get_object_or_404(PhysioUser, id=data["physioId"]),
        "comments": data['comments'],
        "rating": data["rating"],
        "timestamp": datetime.datetime.fromtimestamp(data["timestamp"])  
    }
    serializer = PatientFeedbackSerializer(data=data_obj)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": True}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def get_feedback(request):
    patient_id = request.data["patientId"]
    patient = get_object_or_404(Patient, id=patient_id)
    feedback_list = PatientFeedback.objects.filter(patient=patient)
    serializer = PatientFeedbackSerializer(feedback_list, many=True)
    data = get_physio_detail_feedback(serializer.data)
    return Response(data, status=status.HTTP_200_OK)

@api_view(["PUT","POST", "PATCH"])
def appointments(request):
    if request.method == "PUT":
        data = request.data
        patient = get_object_or_404(Patient, id=data["patientId"])
        physio = get_object_or_404(PhysioUser, id=data["physioId"])
        obj = {
            "patient": patient,
            "physiotherapist": physio,
            "timestamp": datetime.datetime.fromtimestamp(data   ["dateTimestamp"] + \
            (data["startTime"]["hour"] * 60 * 60) + \
            (data["startTime"]["minute"] * 60)),
            "end_time": datetime.time(hour = data["endTime"]["hour"], minute = data["endTime"]["minute"]),
            "status": data["status"],
            "appointment_type": data["appointmentType"]
        }
        serializer = AppointmentSerializer(data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "POST":
        patient = get_object_or_404(Patient, id=request.data["patientId"])
        appointments = Appointment.objects.filter(patient=patient)
        serializer = AppointmentSerializer(appointments, many=True)
        data = get_physio_detail_feedback(serializer.data)
        return Response(data, status=status.HTTP_200_OK)
    
    elif request.method == "PATCH":
        # patient_id = request.data["patientId"]
        data = request.data
        appointment_id = data["appointmentId"]
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        obj = {
            "timestamp": datetime.datetime.fromtimestamp(data   ["dateTimestamp"] + \
            (data["startTime"]["hour"] * 60 * 60) + \
            (data["startTime"]["minute"] * 60)),
            "end_time": datetime.time(hour = data["endTime"]["hour"], minute = data["endTime"]["minute"]),
            "status": data["status"],
            "appointment_type": data["appointmentType"]
        }
        serializer = AppointmentSerializer(appointment, data=obj, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
def cancel_appointment(request):
    data = request.data
    appointment = get_object_or_404(Appointment, id=data["appointmentId"])

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
    
    serializer = AppointmentSerializer(appointment, data={"status": "cancelled"}, partial=True)

    if serializer.is_valid():
        serializer.save()
        obj = serializer.data
        if is_penalty: obj["penalty"] = 30
        return Response(obj, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def get_schedule(request):
    physio_id = request.data["physioId"]
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    physio = get_object_or_404(PhysioUser, id=physio_id)
    schedule_list = PhysioSchedule.objects.filter(physio=physio, date__gte=today)
    serializer = PhysioScheduleSerializer(schedule_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_educational_resources(request):
    resources = EducationResource.objects.all()
    serializer = EdResourceSerializer(resources, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_services(request):
    services = ServiceProvided.objects.all()
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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

@api_view(["GET"])
def get_available_physios(request):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    schedules = PhysioSchedule.objects.filter(date=today)
    serializer = PhysioScheduleSerializer(schedules, many=True)
    physio_ids = [physio["physio"] for physio in serializer.data]
    physio_ids = list(set(physio_ids))
    data = get_physios_from_ids(physio_ids)
    physio_serializer = PhysioUserSerializer(data, many=True)

    return Response(physio_serializer.data, status=status.HTTP_200_OK)



    

    