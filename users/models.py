from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        username = email.split('@')[0]  # Create username from email
        extra_fields.setdefault('username', username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SEEKER = 'seeker', 'Seeker'
        PROVIDER = 'provider', 'Provider'
        ADMIN = 'admin', 'Admin'
        NONE = 'none', 'None'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NONE,
    )
    email = models.EmailField(unique=True)

    is_email_verified = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)


    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    

class SeekerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    industry = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    rating_report_url = models.URLField(null=True, blank=True)

class ProviderProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    service_types = models.JSONField()  
    geoserved = models.JSONField()      
    subscription_tier = models.CharField(max_length=50) 
    

class SubscriptionPlan(models.Model):
    """Model to store the subscription plan info"""
    payment_type = models.CharField(max_length=255, null=False,
                            blank=False, default='')
    plan_name = models.CharField(max_length=255, null=False,
                            blank=False, default='')
    description = models.CharField(max_length=255, null=False, blank=False)
    prod_id = models.CharField(max_length=50, blank=True, null=True)
    prod_price_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.plan_name
    
class SubscriptionMaster(models.Model):
    """Model to store the subscription event info"""
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
    subscription_id = models.CharField(max_length=100, null=True)
    stripe_status = models.CharField(max_length=25, null=True, blank=True)
    start_date = models.IntegerField(null=True)
    end_date = models.IntegerField(null=True)
    billing_reason = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"Subscription Master Id: {self.id}"