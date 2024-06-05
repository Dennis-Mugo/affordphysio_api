from .serializers import EmailTokenSerializer
client_url = "http://localhost:5173"


    
def get_password_reset_link_physio(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"{client_url}/manager/managerresetpassword/{email}/{token_id}"