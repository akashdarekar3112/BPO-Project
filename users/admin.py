from django.contrib import admin
from .models import CustomUser

# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'role', 'is_staff', 'is_active', 'industry', 'location', 'service_types', 'geoserved', 'subscription_tier')
#     list_filter = ('role', 'is_staff', 'is_active')
#     search_fields = ('username', 'role', 'industry', 'location', 'service_types', 'geoserved', 'subscription_tier')

admin.site.register(CustomUser)
