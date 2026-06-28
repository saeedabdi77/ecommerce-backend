from django.contrib import admin
from .models import User, Province, City, Address
from user.logs import admin as logs_admin

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    list_filter = ['province']
    search_fields = ['name']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'postal_code']
    search_fields = ['user__phone_number', 'city__name', 'postal_code']
