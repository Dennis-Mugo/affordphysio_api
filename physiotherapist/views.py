import datetime

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app_physio.models import PhysioUser, PhysioSchedule
from app_physio.serializers import PhysioUserSerializer, PhysioScheduleSerializer
from manager.views import make_request
from physiotherapist.app_serializers import PhysioCategoriesSerializer
from physiotherapist.models import Physiotherapist, PhysiotherapistCategories


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


@api_view(['GET'])
def get_single_physio_details(request):
    def get_single_physio_internal(req):
        physio_id = req.GET["id"]

        # first get the physio
        physio = get_object_or_404(PhysioUser, id=physio_id)
        physio_serializer = PhysioUserSerializer(physio, many=False)

        # then get schedules
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        physio = get_object_or_404(PhysioUser, id=physio_id)
        schedule_list = PhysioSchedule.objects.filter(physio=physio, date__gte=today)
        serializer = PhysioScheduleSerializer(schedule_list, many=True)

        response = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": {
                "user": physio_serializer.data,
                "schedules": serializer.data
            }
        }
        return Response(response, status=status.HTTP_200_OK)

    return make_request(request, get_single_physio_internal)


@api_view(["GET"])
def get_available_physios(request):
    def get_available_physio_internal(req):
        data = None
        filter_ = request.query_params.get("filter", None)
        if filter_ is None or filter_ == "":
            data = PhysioUser.objects.all()
        else:
            filter_ = request.query_params.get("filter", None)
            data = PhysioUser.objects.filter(Q(first_name__contains=filter_) |
                                             Q(last_name__contains=filter_) |
                                             Q(username__contains=filter_) |
                                             Q(email__contains=filter_))

        # limit query
        data = limit_query(data, limit=request.query_params.get("limit", None))

        physio_serializer = PhysioUserSerializer(data, many=True)
        response = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": physio_serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    return make_request(request, get_available_physio_internal)


@api_view(["POST"])
def add_physio_category(request):
    def add_physio_category_inner(req):
        serializer = PhysioCategoriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {"status": status.HTTP_201_CREATED,
                         "status_description": "OK",
                         "errors": None,
                         "data": None}
        return Response(response_data, status=status.HTTP_201_CREATED)

    return make_request(request, add_physio_category_inner)


def limit_query(query: QuerySet, limit):
    # Limit query
    data = query
    if limit is not None and isinstance(limit, str) and limit.isdigit() and int(limit) > 0:
        data = query[:int(limit)]

    return data


@api_view(["GET"])
def get_physio_categories(request):
    def get_physio_categories_internal(req):
        data = PhysiotherapistCategories.objects.all()
        # Limit query
        data = limit_query(data, limit=request.query_params.get("limit", None))

        serializer = PhysioCategoriesSerializer(data, many=True)

        response_data = {"status": status.HTTP_200_OK,
                         "status_description": "OK",
                         "errors": None,
                         "data": serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    return make_request(request, get_physio_categories_internal)


@api_view(["GET"])
def get_physios_for_category(request):
    def get_physios_for_category_internal(req):
        category_id = req.GET["id"]
        # get the category id of the
        physio_categories = PhysioUser.objects.filter(category_id=category_id)

        physio_serializer = PhysioUserSerializer(physio_categories, many=True)
        response_data = {"status": status.HTTP_200_OK, "status_description": "OK",
                         "errors": None,
                         "data": physio_serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    return make_request(request, get_physios_for_category_internal)
