from django.contrib import admin
from .models import ManagerUser, EmailToken, ManagerLog
# Register your models here.

admin.site.register(ManagerUser)
admin.site.register(EmailToken)
admin.site.register(ManagerLog)
