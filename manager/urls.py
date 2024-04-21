from django.urls import path

from manager import views
from manager.views import CreateManagerView

urlpatterns = [
    path('v1/register', CreateManagerView.as_view(), name="register"),

]
