from django.urls import path

from manager import views
from manager.views import CreateManagerView, LoginManagerView

urlpatterns = [
    path('v1/register', CreateManagerView.as_view(), name="register"),
    path('v1/login', LoginManagerView.as_view(), name="login")

]
