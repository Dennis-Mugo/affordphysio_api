from django.http import JsonResponse
from .models import Patient
from .serializers import PatientSerializer
from .service import get_email_verification_link, get_password_reset_link

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


@api_view(["POST"])
def signup_verify(request):
    data = request.data | {"username": request.data["email"], "password": "amref"}
    is_resend = request.data["isResend"]
    serializer = PatientSerializer(data=data)
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
        user = Patient.objects.get(email=request.data['email'])
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
        return Response({'token': token.key, 'user': PatientSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

