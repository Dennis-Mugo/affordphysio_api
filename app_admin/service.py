from .serializers import EmailTokenSerializer

def get_email_verification_link():
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"https://www.affordphysio.com/setpassword/{token_id}"
    
def get_password_reset_link():
    serializer = EmailTokenSerializer(data={})
    if serializer.is_valid():
        serializer.save()
        token_id = serializer.data["id"]
        return f"https://www.affordphysio.com/resetpassword/{token_id}"