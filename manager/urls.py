from django.urls import path

from manager import views

urlpatterns = [
    path('hello', views.hello),

]
