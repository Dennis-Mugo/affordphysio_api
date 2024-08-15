from django.urls import path

from physiotherapist import views

urlpatterns = [
    path("v1/login", views.LoginPhysiotherapistView.as_view(), name="login"),
    path("v1/get_single_physio_details", views.get_single_physio_details, name="get_single_physio_details"),
    path("v1/get_available_physios", views.get_available_physios, name="get_available_physios"),
]
