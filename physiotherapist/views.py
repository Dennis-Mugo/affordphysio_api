from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from manager.views import make_request
from physiotherapist.models import Physiotherapist


# Create your views here.
class LoginPhysiotherapistView(ObtainAuthToken):
    model = Physiotherapist

    # permission_classes = [
    #     permissions.AllowAny  # Or anon users can't register
    # ]
    # serializer_class = ManagerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})


        def make_login_internal(req):
            serializer.is_valid(raise_exception=True)
            user: Physiotherapist = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            # confirm a physiotherapist with the details is present
            Physiotherapist.objects.get(id=user.id)

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

