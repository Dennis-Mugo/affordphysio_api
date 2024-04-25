import json
from typing import Dict

import django.http
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from manager.app_serializers import ManagerSerializer, PhysioSerializer
from manager.models import Manager
from physiotherapist.models import Physiotherapist


# Create your views here.
class CreateManagerView(CreateAPIView):
    model = Manager
    # permission_classes = [
    #     permissions.AllowAny  # Or anon users can't register
    # ]
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        def make_signup_internal(request: django.http.HttpRequest):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            token, created = Token.objects.get_or_create(user=serializer.instance)
            response_data = {"status": status.HTTP_201_CREATED,
                             "status_description": "CREATED",
                             "errors": None,
                             "data": {'auth_token': token.key,
                                      "id": serializer.data["id"],
                                      'username': serializer.data["username"],
                                      'email': serializer.data["email"],
                                      'first_name': serializer.data["first_name"],
                                      'last_name': serializer.data["last_name"],
                                      }}

            return Response(response_data,
                            status=status.HTTP_201_CREATED, headers=headers)

        return make_request(request, make_signup_internal)


class LoginManagerView(ObtainAuthToken):
    model = Manager

    # permission_classes = [
    #     permissions.AllowAny  # Or anon users can't register
    # ]
    # serializer_class = ManagerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        def make_login_internal(req):
            serializer.is_valid(raise_exception=True)
            user: Manager = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            response_data = {"status": status.HTTP_200_OK,
                             "status_description": "OK",
                             "errors": None,
                             "data": {
                                 'auth_token': token.key,
                                 'id': user.id,
                                 'username': user.username,
                                 "email": user.email,
                                 "first_name": user.first_name,
                                 "last_name": user.last_name,
                             }}
            return Response(response_data, status=status.HTTP_200_OK)

        return make_request(request, make_login_internal)


def add_physiotherapist_inner(request: django.http.HttpRequest):
    # the currently logged in user
    user: User = request.user
    # check if the user is a manager, if the get fails
    # this means the user is not a manager
    manager: Manager = Manager.objects.get(id=user.id)
    serializer = PhysioSerializer(data=request.data)
    serializer.created_by = manager
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": None,
                     "data": serializer.data},
                    status=status.HTTP_200_OK)


def get_physiotherapist_for_manager_inner(request: django.http.HttpRequest):
    """
    Get all the physiotherapist a manager added
    """
    # the currently logged-in user
    user: User = request.user
    # check if the user is a manager, if the get fails
    # this means the user is not a manager
    manager: Manager = Manager.objects.get(id=user.id)
    # get the physiotherapists that the manager created
    physiotherapist = Physiotherapist.objects.filter(created_by=manager)
    serializer = PhysioSerializer(many=True, data=physiotherapist, show_created_by=False)
    serializer.show_created_by = False
    serializer.is_valid()
    return Response({"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": None,
                     "data": serializer.data},
                    status=status.HTTP_200_OK)


def make_request(request: django.http.HttpRequest, function):
    """
    Make requests makes an internal request handling errors for me

    :param request: Django request
    :param function: A function we call, passing the `request` argument to it
    """
    try:
        return function(request)
    except ValidationError as e:
        response_data = {"status": status.HTTP_400_BAD_REQUEST,
                         "status_description": "Bad request",
                         "errors": e.detail,
                         "data": None}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        response_data = {"status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                         "status_description": "Internal server error",
                         "errors": {"exception": [f"${e}"]},
                         "data": None}
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_physiotherapist(request: django.http.HttpRequest):
    return make_request(request, add_physiotherapist_inner)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_physiotherapists_for_manager(request: django.http.HttpRequest):
    return make_request(request, get_physiotherapist_for_manager_inner)


def update_physio_status_inner(request: django.http.HttpRequest):
    # data
    json_data: Dict = json.loads(request.body)
    # ensure the data exists in response, and act appropriately
    assert ("id" in json_data)
    assert ("status" in json_data)
    # the currently logged-in user
    user: User = request.user
    # check if the user is a manager, if the get fails
    # this means the user is not a manager
    manager: Manager = Manager.objects.get(id=user.id)

    physiotherapist: Physiotherapist = Physiotherapist.objects.get(id=json_data["id"], created_by=manager)
    physiotherapist.is_active = json_data["status"]
    physiotherapist.save()
    physio_serializer = PhysioSerializer(data=[physiotherapist], many=True)
    physio_serializer.is_valid()
    return Response({"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": None,
                     "data": physio_serializer.data[0]  # Return the first element.
                     },
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_physio_status(request: django.http.HttpRequest):
    return make_request(request, update_physio_status_inner)
