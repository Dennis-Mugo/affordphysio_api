from .serializers import EmailTokenSerializer
client_url = "http://localhost:5173"

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
    
def get_physio_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/physiotherapist/physiosetpassword/{email}/{token_id}"
    
def get_physio_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/physiotherapist/set_password/{email}/{token_id}"
    
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
        return f"{client_url}/manager/managerresetpassword/{email}/{token_id}"
    
def get_password_reset_link_manager(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/manager/managerresetpassword/{email}/{token_id}"