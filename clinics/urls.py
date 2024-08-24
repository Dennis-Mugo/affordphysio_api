from django.urls import path

from clinics import views

urlpatterns = [
    path("v1/add_clinic", views.add_clinic),
    path("v1/get_clinics", views.get_clinics),
]
