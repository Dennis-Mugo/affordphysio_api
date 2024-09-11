from typing import Any

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.serializers import Serializer


def create_token(serializer: Serializer):
    token, created = Token.objects.get_or_create(user=serializer.instance)
    response_data = {"status": status.HTTP_200_OK,
                     "status_description": "CREATED",
                     "errors": None,
                     "data": {'auth_token': token.key,
                              "id": serializer.data["id"],
                              'username': serializer.data["username"],
                              'email': serializer.data["email"],
                              'first_name': serializer.data["first_name"],
                              'last_name': serializer.data["last_name"],
                              'image': serializer.data.get("image", None),
                              "phone_number": serializer.data.get("phone_number", None),
                              "date_of_birth": serializer.data.get("date_of_birth", None),

                              }}

    return Response(response_data,
                    status=status.HTTP_201_CREATED)


def format_successful_operation(data: Any):
    response_data = {"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": None,
                     "data": data}
    return Response(response_data, status=status.HTTP_200_OK)
