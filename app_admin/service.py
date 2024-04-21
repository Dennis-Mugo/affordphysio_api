from .serializers import EmailTokenSerializer

def get_email_verification_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"http://localhost:5173/admin/register/{email}/{token_id}"
    
def get_password_reset_link(email):
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"https://www.affordphysio.com/resetpassword/{email}/{token_id}"