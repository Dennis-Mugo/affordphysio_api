from django.urls import path

from physiotherapist import views

urlpatterns = [
    path("v1/login", views.LoginPhysiotherapistView.as_view(), name="login"),
    path("v1/get_single_physio_details", views.get_single_physio_details, name="get_single_physio_details"),
    path("v1/get_available_physios", views.get_available_physios, name="get_available_physios"),
    path("v1/add_physio_categories", views.add_physio_category, name="add_physio_category"),
    path("v1/get_physio_categories", views.get_physio_categories, name="get_physio_categories"),
    path("v1/get_physio_for_category", views.get_physios_for_category, name="get_physio_in_category"),

    path("v1/add_physio_package",views.add_physio_packages, name="add_physio_packages"),
]
