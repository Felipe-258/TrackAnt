from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Colony


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Colony)
class ColonyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_guest', 'created_at']
    list_filter = ['is_guest']
    search_fields = ['name', 'owner__username']
