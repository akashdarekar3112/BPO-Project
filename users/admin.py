from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProviderProfile, SeekerProfile, SubscriptionPlan, SubscriptionMaster

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'is_email_verified', 'stripe_customer_id')
    list_filter = ('role', 'is_staff', 'is_active', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Stripe Info', {'fields': ('stripe_customer_id',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )

class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'subscription_tier')
    search_fields = ('user__email', 'service_types', 'geoserved')
    list_filter = ('subscription_tier',)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'industry', 'location')
    search_fields = ('user__email', 'industry', 'location')
    list_filter = ('industry', 'location')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_name', 'payment_type', 'prod_id', 'prod_price_id', 'is_active')
    list_filter = ('payment_type', 'is_active')
    search_fields = ('plan_name', 'description')

class SubscriptionMasterAdmin(admin.ModelAdmin):
    list_display = ('subscription_plan', 'stripe_customer_id', 'subscription_id', 'stripe_status', 'is_active')
    list_filter = ('is_active', 'stripe_status')
    search_fields = ('stripe_customer_id', 'subscription_id')

# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProviderProfile, ProviderProfileAdmin)
admin.site.register(SeekerProfile, SeekerProfileAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(SubscriptionMaster, SubscriptionMasterAdmin)
