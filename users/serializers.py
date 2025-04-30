from rest_framework import serializers
from .models import CustomUser, ProviderProfile, SeekerProfile, SubscriptionPlan

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  
        
        email = validated_data.get('email')
        username = email.split('@')[0] 
        
        user = CustomUser.objects.create_user(username=username, **validated_data)
        return user
    
    
class SeekerProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = SeekerProfile
        fields = ['industry', 'location', 'rating_report_url']

    def get_email(self, obj):
        return obj.user.email


class ProviderProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = ProviderProfile
        fields = ['user', 'email', 'service_types', 'geoserved']

    def get_email(self, obj):
        return obj.user.email
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"