from django.urls import path

from manager import views
from manager.views import CreateManagerView, LoginManagerView, add_physiotherapist, get_physiotherapists_for_manager, \
    update_physio_status

urlpatterns = [
    path('v1/register', CreateManagerView.as_view(), name="register"),
    path('v1/login', LoginManagerView.as_view(), name="login"),
    path('v1/add_physio', add_physiotherapist, name="add_physio"),
    path('v1/get_physio', get_physiotherapists_for_manager, name="get_physio"),
    path('v1/update_physio_status', update_physio_status, name="update_physio_status")

]
