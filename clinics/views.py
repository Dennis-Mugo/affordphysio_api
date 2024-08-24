import django
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clinics.app_serializers import ClinicsSerializer
from clinics.models import Clinic
from manager.models import Manager
from manager.views import make_request


# Create your views here.


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_clinic(request: HttpRequest) -> HttpResponse:
    def add_clinic_internal(request: HttpRequest):
        # get the data
        user: User = request.user
        manager: Manager = Manager.objects.get(id=user.id)
        data: QueryDict = request.data
        data["created_by_id"] = manager.id
        serializer = ClinicsSerializer(data=data)
        # TODO: This isn't working, set it up correctly
        serializer.created_by = manager
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serialized_data = {
            "status": status.HTTP_201_CREATED,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data=serialized_data, status=status.HTTP_201_CREATED)

    return make_request(request, add_clinic_internal)


@api_view(["GET"])
def get_clinics(request: HttpRequest) -> HttpResponse:
    def get_clinic_internal(request: HttpRequest):
        clinics = Clinic.objects.all().filter(status__in=[1])
        serializer = ClinicsSerializer(clinics, many=True)
        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data=data, status=status.HTTP_200_OK)

    return make_request(request, get_clinic_internal)
