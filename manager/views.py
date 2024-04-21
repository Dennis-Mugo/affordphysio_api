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
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
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
                             "errors": {},
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
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": e.detail,
                             "data": {}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": {"exception": [f"${e}"]},
                             "data": {}}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
