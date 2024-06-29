from .serializers import EmailTokenSerializer
client_url = "http://localhost:5173"
from app_manager.models import ManagerUser
from app_manager.serializers import ManagerUserSerializer
from django.shortcuts import get_object_or_404

def get_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/admin/register/{email}/{token_id}"
    
def get_manager_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/manager/managersignup/{email}/{token_id}"
    
# def get_physio_email_verification_link(email):
#     serializer = EmailTokenSerializer(data={})
#     if serializer.is_valid():
#         serializer.save()
#         token_id = serializer.data["id"]
#         return f"{client_url}/physiotherapist/physiosetpassword/{email}/{token_id}"
    
def get_physio_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/physiotherapist/register/{email}/{token_id}"
    
def get_password_reset_link_admin(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/admin/resetpassword/{email}/{token_id}"
    
def get_password_reset_link_physio(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/physiotherapist/reset_password/{email}/{token_id}"
    
def get_password_reset_link_manager(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/manager/managerresetpassword/{email}/{token_id}"
    
def get_manager_detail(logs):
    cache = {}
    res = []
    for log in logs:
        manager_id = log['manager']
        if manager_id in cache:
            log['manager'] = cache[manager_id]
        else:
            manager = get_object_or_404(ManagerUser, id=manager_id)
            serializer = ManagerUserSerializer(instance=manager)
            log['manager'] = serializer.data
            cache[manager_id] = serializer.data
        res.append(log)
    return res