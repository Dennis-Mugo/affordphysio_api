from django.contrib import admin
from django.urls import path, include
from patient import views

urlpatterns = [
    path('signup_verify', views.signup_verify),
    path('signup_set_password', views.signup_set_password),
    path('forgot_password', views.forgot_password_send_email),
    path('reset_password', views.reset_password),
    path('login', views.login),
    path('verify_token', views.test_token),
    path('verify_email_token/<str:tokenId>', views.verify_email_token),
    path('profile/<int:patientId>', views.patient_profile),
    path('logout', views.logout),

    path('add_feedback', views.add_feedback),
    path("get_feedback", views.get_feedback),

    path("appointments", views.appointments),
    path("cancel_appointment", views.cancel_appointment)
]

