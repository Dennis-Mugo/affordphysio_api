from django.urls import path

from sms import views

urlpatterns = [
    path('v1/sms_callback', views.sms_dlr, name='sms_callback'),
]
