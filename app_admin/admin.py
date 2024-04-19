from django.contrib import admin
from .models import AppAdmin, AdminUser
# Register your models here.

admin.site.register(AppAdmin)
admin.site.register(AdminUser)