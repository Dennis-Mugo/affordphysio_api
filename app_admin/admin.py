from django.contrib import admin
from .models import AppAdmin, AdminUser, EmailToken, ServiceProvided, EducationResource
# Register your models here.

admin.site.register(AppAdmin)
admin.site.register(AdminUser)
admin.site.register(EmailToken)
admin.site.register(ServiceProvided)
admin.site.register(EducationResource)