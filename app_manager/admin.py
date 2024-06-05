from django.contrib import admin
from .models import ManagerUser, EmailToken
# Register your models here.

admin.site.register(ManagerUser)
admin.site.register(EmailToken)
