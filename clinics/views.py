import asyncio

import django
from django.db.models import Q, Avg, Count
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_physio.serializers import PhysioUserSerializer
from clinics.app_serializers import ClinicsSerializer, PhysioClinicsSerializer, ClinicImageSerializer, \
    ClinicReviewsSerializer
from clinics.models import Clinic, PhysioClinic, ClinicImages, ClinicReviews
from manager.models import Manager
from manager.views import make_request
from patient.models import Patient
from physiotherapist.models import Physiotherapist


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
    def get_clinic_internal(req: HttpRequest):

        filter_ = request.query_params.get("filter", None)
        if filter_ is None or filter_ == "":
            clinics = Clinic.objects.all().filter(status__in=[1])
        else:
            clinics = Clinic.objects.filter(Q(name__contains=filter_) |
                                            Q(location_description__contains=filter_)
                                            ).filter(status__in=[1])

        serializer = ClinicsSerializer(clinics, many=True)
        data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(data=data, status=status.HTTP_200_OK)

    return make_request(request, get_clinic_internal)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_physio_to_clinic(request: HttpRequest) -> HttpResponse:
    def add_physio_to_clinic_internal(request: HttpRequest):
        # get the data
        user: User = request.user
        manager: Manager = Manager.objects.get(id=user.id)
        data: QueryDict = request.data

        serializer = PhysioClinicsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "status": status.HTTP_201_CREATED,
            "status_description": "CREATED",
            "errors": None,
            "data": serializer.data
        }
        return Response(data=response, status=status.HTTP_201_CREATED)

    return make_request(request, add_physio_to_clinic_internal)


@api_view(["GET"])
def get_clinic_details(request: HttpRequest) -> HttpResponse:
    def get_clinic_internal(req: HttpRequest):
        clinic = Clinic.objects.get(id=req.GET["clinic_id"])
        clinic_serializer = ClinicsSerializer(clinic)
        physios = [e.physiotherapist for e in
                   PhysioClinic.objects.select_related("physiotherapist").filter(clinic_id=clinic.id)]

        images = ClinicImages.objects.filter(clinic_id=clinic.id)

        image_serializers = ClinicImageSerializer(images, many=True)

        physiotherapists = PhysioUserSerializer(physios, show_created_by=False, many=True)

        # limit reviews to 10
        clinic_reviews = ClinicReviews.objects.filter(clinic_id=clinic.id)
        rating = clinic_reviews.aggregate(average=Avg("rating"), count=Count("rating"))
        rating_c = (ClinicReviews.objects
                    .values('ratings')
                    .annotate(count=Count('ratings'))).order_by()

        clinic_reviews = clinic_reviews[:10]

        clinics_reviews_serializer = ClinicReviewsSerializer(clinic_reviews, many=True)

        response = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": {
                "clinic": clinic_serializer.data,
                "physiotherapists": physiotherapists.data,
                "images": image_serializers.data,
                "reviews": clinics_reviews_serializer.data,
                "rating": {
                    "avg": rating["average"],
                    "count": rating["count"],
                    "distribution": rating_c,
                }
            }
        }
        return Response(data=response, status=status.HTTP_200_OK)

    return get_clinic_internal(request)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_clinic_images(request: HttpRequest) -> HttpResponse:
    def add_clinic_image_internal(request: HttpRequest):
        user: User = request.user
        manager: Manager = Manager.objects.get(id=user.id)
        data = request.data;
        serializer = ClinicImageSerializer(data=data)
        # TODO: This isn't working, set it up correctly
        serializer.created_by = manager
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serialized_data = {
            "status": status.HTTP_201_CREATED,
            "status_description": "CREATED",
            "errors": None,
            "data": serializer.data
        }
        return Response(data=serialized_data, status=status.HTTP_201_CREATED)

    return make_request(request, add_clinic_image_internal)


@api_view(["GET"])
def get_clinic_reviews(request: HttpRequest) -> HttpResponse:
    def get_clinic_reviews_internal(request: HttpRequest):
        clinic = Clinic.objects.get(id=request.GET["clinic_id"])
        clinic_reviews = ClinicReviews.objects.filter(clinic=clinic)
        clinic_reviews_serializer = ClinicReviewsSerializer(clinic_reviews, many=True)
        serialized_data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": clinic_reviews_serializer.data
        }
        return Response(data=serialized_data, status=status.HTTP_200_OK)

    return make_request(request, get_clinic_reviews_internal)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_clinic_review(request: HttpRequest) -> HttpResponse:
    def add_clinic_review_internal(request: HttpRequest):
        user: User = request.user

        patient: Patient = Patient.objects.get(id=user.id)
        data: QueryDict = request.data
        serializer = ClinicReviewsSerializer(data=data)
        serializer.user = patient
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serialized_data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(status=status.HTTP_201_CREATED, data=serialized_data)

    # return add_clinic_review_internal(request)
    return make_request(request, add_clinic_review_internal)


@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_clinic_review(request: HttpRequest) -> HttpResponse:
    def update_clinic_review_internal(request: HttpRequest):
        user: User = request.user
        patient: Patient = Patient.objects.get(id=user.id)
        data: QueryDict = request.data
        review = ClinicReviews.objects.get(id=data["id"])
        serializer = ClinicReviewsSerializer(data=data, instance=review, partial=True)
        serializer.user = patient
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serialized_data = {
            "status": status.HTTP_200_OK,
            "status_description": "OK",
            "errors": None,
            "data": serializer.data
        }
        return Response(status=status.HTTP_200_OK, data=serialized_data)

    return make_request(request, update_clinic_review_internal)
