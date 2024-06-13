from django.contrib import admin
from django.urls import path, include
from app_admin import views

urlpatterns = [
    path('admins/', views.admin_list),
    path('signup_verify', views.signup_verify),
    path('signup_set_password', views.signup_set_password),
    path('forgot_password', views.forgot_password_send_email),
    path('reset_password', views.reset_password),
    path('login', views.login),
    path('verify_token', views.test_token),
    path('verify_email_token/<str:tokenId>', views.verify_email_token),
    path('profile/<int:adminId>', views.get_admin_profile),
    path('logout', views.logout),

    path('add_manager', views.add_manager),
    path("remove_manager/<int:managerId>", views.remove_manager),
    path("view_managers", views.view_managers),
    path("view_removed_managers", views.view_removed_managers),
    path("view_manager_logs", views.view_manager_logs),


    path("services_provided", views.services_provided),
    path("delete_service_provided/<int:service_id>", views.delete_service_provided),
    path("update_service_provided/<int:service_id>", views.update_service_provided),

    path("education_resources", views.ed_resource),
    path("delete_education_resource/<int:resource_id>", views.delete_ed_resource),
    path("update_education_resource/<int:resource_id>", views.update_ed_resource),

    path("get_incoming_payments", views.get_incoming_payments),
    path("get_accepted_payments", views.get_accepted_payments),
    path("get_declined_payments", views.get_declined_payments),
    path("update_payment_status/<int:payment_id>", views.update_payment_status),

    
]
