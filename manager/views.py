from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from manager.app_serializers import ManagerSerializer
from manager.models import Manager


# Create your views here.
class CreateManagerView(CreateAPIView):
    model = Manager
    # permission_classes = [
    #     permissions.AllowAny  # Or anon users can't register
    # ]
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        try:
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
        except ValidationError as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST,
                             "status_description": "Bad request",
                             "errors": e.detail,
                             "data": None}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST,
                             "status_description": "Bad request",
                             "errors": {"exception": [f"${e}"]},
                             "data": None}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginManagerView(ObtainAuthToken):
    model = Manager
    # permission_classes = [
    #     permissions.AllowAny  # Or anon users can't register
    # ]
    #serializer_class = ManagerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
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
            return Response(response_data, status=status.HTTP_200_OK, )
        except ValidationError as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST,
                             "status_description": "Bad request",
                             "errors": e.detail,
                             "data": None
                             }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {"status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                             "status_description": "Internal Error",
                             "errors": {"exception": [f"${e}"]},
                             "data": None}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
