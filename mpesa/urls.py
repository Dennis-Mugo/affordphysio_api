from django.urls import path

from mpesa import views

urlpatterns = [
    path('v1/deposit_mpesa', views.deposit_mpesa, name='mpesa_deposit'),
    path('v1/mpesa_callback', views.mpesa_callback, name='mpesa_callback'),
    path('v1/mpesa_transactions', views.get_mpesa_transactions, name='mpesa_transactions'),
    path("v1/mpesa_wallet", views.get_wallet, name='mpesa_wallet'),
]
