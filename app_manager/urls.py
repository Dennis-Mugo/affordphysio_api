from django.contrib import admin
from django.urls import path, include
from app_manager import views

urlpatterns = [
    # path('admins/', views.admin_list),
    # path('signup_verify', views.signup_verify),
    path('signup_set_password', views.signup_set_password),
    path('forgot_password', views.forgot_password_send_email),
    path('reset_password', views.reset_password),
    path('login', views.login),
    path('verify_token', views.test_token),
    path('verify_email_token/<str:tokenId>', views.verify_email_token),
    path('profile/<int:managerId>', views.get_manager_profile),
    path('logout', views.logout),

    path('add_physio', views.add_physio),
    path("remove_physio/<int:physioId>", views.remove_physio),
    path("view_physios", views.view_physios),
    path("view_removed_physios", views.view_removed_physios),

    path("view_physio_logs", views.view_physio_logs),
    path("view_patient_logs", views.view_patient_logs),
    path("view_patients", views.view_patients),



    
]
