from django.urls import path

from clinics import views

urlpatterns = [
    path("v1/add_clinic", views.add_clinic),
    path("v1/get_clinics", views.get_clinics),
    path("v1/add_physio_to_clinic", views.add_physio_to_clinic),

    path("v1/get_clinic_details", views.get_clinic_details),

    path("v1/add_clinic_images", views.add_clinic_images),
    path("v1/add_clinic_review", views.add_clinic_review),
    path("v1/get_clinic_reviews", views.get_clinic_reviews),

    path("v1/update_clinic_review",views.update_clinic_review)

]
