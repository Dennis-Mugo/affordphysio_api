from django.urls import path
from patient import views

urlpatterns = [
    path('v1/signup', views.signup_verify),
    path('signup_set_password', views.signup_set_password),
    path('forgot_password', views.forgot_password_send_email),
    path('reset_password', views.reset_password),
    path('v1/login', views.login),
    path('verify_token', views.test_token),
    path('verify_email_token/<str:tokenId>', views.verify_email_token),
    path('profile/<int:patientId>', views.patient_profile),
    path('logout', views.logout),

    path('v1/add_feedback', views.add_feedback),
    path("v1/get_feedback", views.get_feedback),

    path("v1/make_appointment", views.make_appointment),
    path("v1/upcoming_appointments", views.get_patient_upcoming_appointments),
    path("v1/cancel_appointment", views.cancel_patient_upcoming_appointment),
    path("v1/reschedule_appointment", views.reschedule_patient_upcoming_appointment),

    path("appointments", views.appointments),
    path("cancel_appointment", views.cancel_appointment),

    path("v1/get_schedule", views.get_schedule),
    path("get_educational_resources", views.get_educational_resources),

    path("get_services", views.get_services),
    path("add_payment", views.add_payment),
    path("get_payments", views.get_payments),

    path("v1/update_profile", views.upload_profile),
    path("v1/forgot_password", views.forgot_password_send_phone_number),
]
