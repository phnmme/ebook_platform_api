from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SystemUser

@admin.register(SystemUser)
class SystemUserAdmin(UserAdmin):
    model = SystemUser
    list_display = ("userid", "email", "username", "fullname", "role", "is_active")
    search_fields = ("email", "fullname")