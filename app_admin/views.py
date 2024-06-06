from django.http import JsonResponse
from .models import AppAdmin, AdminUser, EmailToken, EducationResource, ServiceProvided
from .serializers import AppAdminSerializer, UserSerializer, AdminUserSerializer, EmailTokenSerializer, EdResourceSerializer, ServiceSerializer
from app_manager.serializers import ManagerUserSerializer, ManagerLogSerializer
from app_manager.models import ManagerUser, ManagerLog
from manager.models import Manager
from .service import get_email_verification_link, get_password_reset_link_admin, get_manager_email_verification_link, get_manager_detail

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

@api_view(['GET', 'POST'])
def admin_list(request):

    #get all the admins
    #serialize them
    #return json
    if request.method == 'GET':
        admins = AppAdmin.objects.all()
        serializer = AppAdminSerializer(admins, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    if request.method == 'POST':
        serializer = AppAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.
            HTTP_201_CREATED)
        

@api_view(['POST'])
def signup_verify(request):
    data = request.data | {"username": request.data["email"], "password": "amref"}
    is_resend = request.data["isResend"]
    serializer = AdminUserSerializer(data=data)
    verify_link = get_email_verification_link(request.data['email'])
    if is_resend:
        #User data is saved but user wants to resend verification email
        send_mail(
            'Afford Physio Email verification',
            f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
            'dennismthairu@gmail.com',
            [request.data['email']],
            fail_silently=False,
        )
        return Response({"success": True}, status=status.HTTP_200_OK)
    
    if serializer.is_valid():
        serializer.save()
        user = AdminUser.objects.get(email=request.data['email'])
        # user.set_password("password")
        # user.save()
        token = Token.objects.create(user=user) 
        send_mail(
            'Afford Physio Email verification',
            f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
            'dennismthairu@gmail.com',
            [request.data['email']],
            fail_silently=False,
        )
        return Response({'token': token.key, 'user': AdminUserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
def signup_set_password(request):
    email = request.data["email"]
    user = get_object_or_404(AdminUser, email=email)
    user.set_password(request.data['password'])
    user.save()
    serializer = AdminUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def forgot_password_send_email(request):
    email = request.data["email"]
    user = get_object_or_404(AdminUser, email=email)
    # Send email with link to take them to forgot password page
    password_change_link = get_password_reset_link_admin(email)
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
    user = get_object_or_404(AdminUser, email=email)
    user.set_password(new_password)
    user.save()
    return Response({"success": True}, status=status.HTTP_200_OK)



@api_view(["POST"])
def login(request):
    user = get_object_or_404(AdminUser, email=request.data['email'])
    
    if not user.check_password(request.data['password']):
        return Response({"detail": "Email or password is incorrect"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = AdminUserSerializer(instance=user)
    # user.set_password("password")
    # user.save()
    
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"Passed for {request.user.email}")


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])

@permission_classes([IsAuthenticated])

def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(["GET", "PUT"])
def get_admin_profile(request, adminId):
    user = get_object_or_404(AdminUser, id=adminId)

    if request.method == "GET":
        serializer = AdminUserSerializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        serializer = AdminUserSerializer(user, request.data, partial=True)
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
def add_manager(request):
    data_obj = {
        "email": request.data["email"],
        "first_name": request.data["first_name"],
        "last_name": request.data["last_name"],
        "username": request.data["first_name"]+request.data['last_name'],
        "password": "amref"
    }
    serializer = ManagerUserSerializer(data=data_obj)
    if serializer.is_valid():
        serializer.save()
        verify_link = get_manager_email_verification_link(request.data['email'])
    
        send_mail(
            'Afford Physio Email verification',
            f'Follow the link below to complete signing up\n\n{verify_link}\n\n The link expires in 10 minutes.',
            'dennismthairu@gmail.com', 
            [data_obj['email']],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def remove_manager(request, managerId):
    manager = get_object_or_404(ManagerUser, id=managerId)
    manager.is_active = False
    manager.save()
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_managers(request):
    managers = ManagerUser.objects.filter(is_active=True)
    serializer = ManagerUserSerializer(managers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def view_removed_managers(request):
    managers = ManagerUser.objects.filter(is_active=False)
    serializer = ManagerUserSerializer(managers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def services_provided(request):
    data = request.data
    if request.method == "GET":
        services = ServiceProvided.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = ServiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   
    
@api_view(["DELETE"])
def delete_service_provided(request, service_id):
    service = get_object_or_404(ServiceProvided, id=service_id)
    service.delete()
    return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

@api_view(["PUT"])
def update_service_provided(request, service_id):
    service = get_object_or_404(ServiceProvided, id=service_id)
    serializer = ServiceSerializer(service, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
def ed_resource(request):
    data = request.data
    if request.method == "GET":
        resources = EducationResource.objects.all()
        serializer = EdResourceSerializer(resources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = EdResourceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   
    
@api_view(["DELETE"])
def delete_ed_resource(request, resource_id):
    resource = get_object_or_404(EducationResource, id=resource_id)
    resource.delete()
    return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

@api_view(["PUT"])
def update_ed_resource(request, resource_id):
    resource = get_object_or_404(EducationResource, id=resource_id)
    serializer = EdResourceSerializer(resource, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def view_manager_logs(request):
    manager_logs = ManagerLog.objects.all().order_by("-timestamp")
    serializer = ManagerLogSerializer(manager_logs, many=True)
    log_list = get_manager_detail(serializer.data)
    return Response(log_list, status=status.HTTP_200_OK)
    
    





    
