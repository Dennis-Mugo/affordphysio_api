from django.http import JsonResponse
from .models import ManagerUser
from app_admin.models import EmailToken
from app_physio.models import PhysioUser, PhysioLog
from .serializers import ManagerUserSerializer
from app_admin.serializers import EmailTokenSerializer
from app_physio.serializers import PhysioUserSerializer, PhysioLogSerializer
from patient.serializers import PatientLogSerializer, PatientSerializer
from patient.models import PatientLog, Patient
from manager.models import Manager
from app_admin.service import get_password_reset_link_manager, get_physio_email_verification_link
from .service import get_physio_detail, get_patient_detail, add_manager_log

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
import time
import os
from dotenv import load_dotenv
load_dotenv()

sender_email = os.getenv("EMAIL_HOST_USER")

@api_view(['GET', 'POST'])
def manager_list(request):

    #get all the managers
    #serialize them
    #return json
    if request.method == 'GET':
        managers = ManagerUser.objects.all()
        serializer = ManagerUserSerializer(managers, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    if request.method == 'POST':
        serializer = ManagerUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.
            HTTP_201_CREATED)
        


@api_view(["POST"])
def signup_set_password(request):
    email = request.data["email"]
    user = get_object_or_404(ManagerUser, email=email)
    user.set_password(request.data['password'])
    user.save()
    serializer = ManagerUserSerializer(user)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def forgot_password_send_email(request):
    email = request.data["email"]
    user = get_object_or_404(ManagerUser, email=email)
    # Send email with link to take them to forgot password page
    password_change_link = get_password_reset_link_manager(email)
    send_mail(
        'Afford Physio Password Reset',
        f'Follow the link below to change your password\n\n{password_change_link}\n\n The link expires in 10 minutes.',
        sender_email,
        [email],
        fail_silently=False,
    )
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
def reset_password(request):
    email = request.data["email"]
    new_password = request.data["password"]
    user = get_object_or_404(ManagerUser, email=email)
    user.set_password(new_password)
    user.save()
    return Response({"success": True}, status=status.HTTP_200_OK)



@api_view(["POST"])
def login(request):
    user = get_object_or_404(ManagerUser, email=request.data['email'])

    if not user.is_active:
        return Response({"detail": "This account has been deleted!"}, status=status.HTTP_200_OK)
    
    if not user.check_password(request.data['password']):
        return Response({"detail": "Email or password is incorrect"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = ManagerUserSerializer(instance=user)

    log = add_manager_log("Logged in", user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    serializer = ManagerUserSerializer(instance=request.user)
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])

@permission_classes([IsAuthenticated])

def logout(request):
    request.user.auth_token.delete()
    log = add_manager_log("Logged out", request.user)
    if log != True:
        print(log)
        return Response(log, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_200_OK)

@api_view(["GET", "PUT"])
def get_manager_profile(request, managerId):
    user = get_object_or_404(ManagerUser, id=managerId)

    if request.method == "GET":
        serializer = ManagerUserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = ManagerUserSerializer(user, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["PUT"])
# def update_admin_profile(request, adminId):
#     user = get_object_or_404(AdminUser, id=adminId)
#     serializer = AdminUserSerializer(user, request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
def add_physio(request):
    is_resend = request.data.get("isResend", False)
    if is_resend:
        verify_link = get_physio_email_verification_link(request.data['email'])
    
        send_mail(
            'Afford Physio Email verification',
            f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
            sender_email, 
            [request.data['email']],
            fail_silently=False,
        )
        return Response({"success": True}, status=status.HTTP_200_OK)
    

    email_exists = PhysioUser.objects.filter(email=request.data["email"])
    if email_exists.count() > 0:
        return Response({"detail": "This email already exists!"}, status=status.HTTP_200_OK)
    

    data_obj = {
        "email": request.data["email"],
        "first_name": request.data["first_name"],
        "last_name": request.data["last_name"],
        "username": request.data["first_name"]+request.data['last_name'],
        "password": "amref"
    }
    serializer = PhysioUserSerializer(data=data_obj)
    if serializer.is_valid():
        serializer.save()
        verify_link = get_physio_email_verification_link(request.data['email'])
    
        send_mail(
            'Afford Physio Email verification',
            f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
            sender_email, 
            [data_obj['email']],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def remove_physio(request, physioId):
    physio = get_object_or_404(PhysioUser, id=physioId)
    physio.is_active = False
    physio.save()
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_physios(request):
    physios = PhysioUser.objects.filter(is_active=True)
    serializer = PhysioUserSerializer(physios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_removed_physios(request):
    physios = PhysioUser.objects.filter(is_active=False)
    serializer = PhysioUserSerializer(physios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_physio_logs(request):
    physio_logs = PhysioLog.objects.all().order_by("-timestamp")
    serializer = PhysioLogSerializer(physio_logs, many=True)
    log_list = get_physio_detail(serializer.data)
    return Response(log_list, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_patient_logs(request):
    patient_logs = PatientLog.objects.all().order_by("-timestamp")
    serializer = PatientLogSerializer(patient_logs, many=True)
    log_list = get_patient_detail(serializer.data)
    return Response(log_list, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_patients(request):
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



    
    





    
