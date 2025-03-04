from django.contrib import admin
from django.urls import path, include
from app_physio import views

urlpatterns = [
    path("signup_verify_email", views.signup_verify),
    # path('signup_set_password', views.signup_set_password),
    path('signup', views.signup_set_password),
    path('forgot_password', views.forgot_password_send_email),
    path('reset_password', views.reset_password),
    path('login', views.login),
    path('verify_token', views.test_token),
    path('verify_email_token/<str:tokenId>', views.verify_email_token),
    path('profile/<int:physioId>', views.physio_profile),
    path('logout', views.logout),

    path("set_schedule", views.set_schedule),
    path ("get_schedule", views.get_schedule),

    path("get_incoming_appointments", views.get_incoming_appointments),
    path("get_accepted_appointments", views.get_accepted_appointments),
    path("get_completed_appointments", views.get_completed_appointments),


    path("change_appointment_status", views.appointments),
    path("cancel_appointment", views.cancel_appointment),
    path("reschedule_appointment", views.reschedule_appointment),

    
    path("get_feedback", views.get_feedback),
    path("get_average_rating", views.get_average_rating),
    path("add_post_visit", views.add_post_visit),
    path("get_post_visit", views.get_post_visit),

    path("save_physio_location", views.add_physio_location),
    path("get_patient_locations", views.get_patient_locations),
    # path("appointments", views.appointments),

    path("add_video_recommendation", views.add_video_recommendation),
]

