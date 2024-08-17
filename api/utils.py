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
                              }}

    return Response(response_data,
                    status=status.HTTP_201_CREATED)
