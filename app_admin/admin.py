from django.contrib import admin
from .models import AppAdmin, AdminUser, EmailToken
# Register your models here.

admin.site.register(AppAdmin)
admin.site.register(AdminUser)
admin.site.register(EmailToken)