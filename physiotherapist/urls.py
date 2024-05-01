from django.urls import path

from physiotherapist.views import LoginPhysiotherapistView

urlpatterns = [
    path("v1/login", LoginPhysiotherapistView.as_view(), name="login")
]
