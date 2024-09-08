from django.db.models import Q
from django.http import JsonResponse
from rest_framework.serializers import Serializer

from api.utils import create_token
from manager.views import make_request
from sms.views import create_message
from .models import Patient, PatientFeedback, Appointment, Payment
from app_admin.models import EmailToken, EducationResource, ServiceProvided
from app_physio.models import PhysioUser, PhysioSchedule
from app_physio.serializers import PhysioUserSerializer, PhysioScheduleSerializer
from app_admin.serializers import EmailTokenSerializer, EdResourceSerializer, ServiceSerializer
from .serializers import PatientSerializer, PatientFeedbackSerializer, AppointmentSerializer, \
    AppointmentCancellationSerializer, PenaltySerializer, PaymentSerializer
from .service import get_email_verification_link, get_password_reset_link, add_patient_log, get_physio_detail_feedback, \
    get_physios_from_ids

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
    def signup_verify_internal(req):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return create_token(serializer)

    return make_request(request, signup_verify_internal)


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
    def login_internal(req):
        user = get_object_or_404(Patient, email=request.data['email'])
        if not user.check_password(request.data['password']):
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "status_description": "User account is disabled",
                "errors": {"exception": ["Email or password is incorrect"]},
                "data": None
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "status_description": "User account is disabled",
                "errors": {"exception": ["User account is disabled"]},
                "data": None
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientSerializer(instance=user)

        log = add_patient_log("Logged in", user)
        return create_token(serializer)

    return make_request(request, login_internal)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    serializer = PatientSerializer(instance=request.user)
    return Response({"user": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    def logout_internal(req):
        request.user.auth_token.delete()
        log = add_patient_log("Logged out", request.user)
        return Response({"success": True}, status=status.HTTP_200_OK)

    return make_request(request, logout_internal)


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

    token_expiry_duration = 10 * 60  # Token expires in 10 minutes
    token_valid = now_epoch_seconds - epoch_created_seconds < token_expiry_duration

    return Response({"valid": token_valid}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_feedback(request):
    def add_feedback_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        data = request.data

        data_obj = {
            "patient": patient,
            "physiotherapist": get_object_or_404(PhysioUser, id=data["physio_id"]),
            "comments": data['comments'],
            "rating": data["rating"],
            "timestamp": datetime.datetime.now()
        }
        serializer = PatientFeedbackSerializer(data=data_obj)
        serializer.physiotherapist = get_object_or_404(PhysioUser, id=data["physio_id"])
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }

        return Response(data, status=status.HTTP_201_CREATED)

    return make_request(request, add_feedback_internal)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_feedback(request):
    def get_feedback_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        feedback_list = PatientFeedback.objects.filter(patient=patient)
        serializer = PatientFeedbackSerializer(feedback_list, many=True)

        response = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    return make_request(request, get_feedback_internal)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def make_appointment(request):
    def make_appointment_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)

        data = request.data

        physio_id = data["physio_id"]

        physio = PhysioUser.objects.get(id=physio_id)

        start_time = datetime.datetime.fromisoformat(data["start_time"])
        end_time = datetime.datetime.fromisoformat(data["end_time"])
        if start_time.timestamp() < datetime.datetime.now().timestamp():
            # BUG[cae] = this may allow people to set three hours difference
            raise Exception("Start time must be after current time (can't book an appointment for before)")
        if end_time.timestamp() < start_time.timestamp():
            raise Exception("End time cannot be earlier than start time")

        obj = {
            "patient": patient,
            "physiotherapist": physio,
            "start_time": start_time,
            "physiotherapist_id": physio.id,
            "end_time": end_time,
            "status": 1,
            "appointment_type": data["appointment_type"],
        }

        serializer = AppointmentSerializer(data=obj)
        serializer.physiotherapist = physio
        serializer.physiotherapist_id = physio.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "status": status.HTTP_201_CREATED,
            "status_description": "CREATED",
            "errors": None,
            "data": serializer.data
        }

        return Response(response, status=status.HTTP_201_CREATED)

    # return make_appointment_internal(request)
    return make_request(request, make_appointment_internal)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_patient_upcoming_appointments(request):
    def get_patient_appointments_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)

        status_ = request.query_params.get("status", None)
        upcoming_ = request.query_params.get("upcoming", None)

        if status_ is None or status_ == "":
            appointments_ = Appointment.objects.filter(patient=patient)

        else:
            appointments_ = Appointment.objects.filter(patient=patient,
                                                       status=status_)

        if upcoming_ is not None and upcoming_ == "true":
            # only return upcoming requests
            appointments_ = appointments_.filter(start_time__gt=datetime.datetime.now())

        serializer = AppointmentSerializer(appointments_, many=True)

        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    return make_request(request, get_patient_appointments_internal)


@api_view(["GET", "DELETE"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def cancel_patient_upcoming_appointment(request):
    def get_patient_appointments_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        appointments = Appointment.objects.get(patient=patient, id=request.GET["id"],
                                               start_time__gte=datetime.datetime.now())
        appointments.status = "-1"
        appointments.save()
        serializer = AppointmentSerializer(appointments, many=False)
        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    return make_request(request, get_patient_appointments_internal)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def reschedule_patient_upcoming_appointment(request):
    def reschedule_patient_appointments_internal(req):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        data = request.data

        appointments = Appointment.objects.get(patient=patient, id=data["appointment_id"],
                                               start_time__gte=datetime.datetime.now())

        start_time = datetime.datetime.fromisoformat(data["start_time"])
        end_time = datetime.datetime.fromisoformat(data["end_time"])
        if end_time.timestamp() < start_time.timestamp():
            raise Exception("End time cannot be earlier than start time")

        appointments.start_time = start_time
        appointments.end_time = end_time

        appointments.save()
        serializer = AppointmentSerializer(appointments, many=False)
        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    return make_request(request, reschedule_patient_appointments_internal)


@api_view(["PUT", "POST", "PATCH"])
def appointments(request):
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
            "end_time": datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"]),
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
            "timestamp": datetime.datetime.fromtimestamp(data["dateTimestamp"] + \
                                                         (data["startTime"]["hour"] * 60 * 60) + \
                                                         (data["startTime"]["minute"] * 60)),
            "end_time": datetime.time(hour=data["endTime"]["hour"], minute=data["endTime"]["minute"]),
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

    appointment_cancel_duration = 6 * 60 * 60  # Appointment can only be cancelled more than 6 hours prior
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


@api_view(["GET"])
def get_schedule(request):
    def get_schedule_internal(req):
        physio_id = req.GET["id"]
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        physio = get_object_or_404(PhysioUser, id=physio_id)
        schedule_list = PhysioSchedule.objects.filter(physio=physio, date__gte=today)
        serializer = PhysioScheduleSerializer(schedule_list, many=True)
        response = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    return make_request(request, get_schedule_internal)


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


@api_view(["POST"])
def get_payments(request):
    patient_id = request.data.get("patientId", False)
    if not patient_id:
        return Response({"detail": "PatientId is missing"}, status=status.HTTP_400_BAD_REQUEST)
    payments = Payment.objects.filter(patient=patient_id)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_profile(request):
    def upload_profile_internal(request):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    return make_request(request, upload_profile_internal)
