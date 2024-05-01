from django.contrib import admin

from manager.models import Manager


# Register your models here.
@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    pass