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
    match_score = serializers.IntegerField(required=False)

    class Meta:
        model = SeekerProfile
        fields = ['industry', 'location', 'rating_report_url', 'email', 'match_score']

    def get_email(self, obj):
        if isinstance(obj, dict):
            return obj.get('email')
        return obj.user.email if obj.user else None


class ProviderProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    match_score = serializers.IntegerField(required=False)

    class Meta:
        model = ProviderProfile
        fields = ['email', 'service_types', 'geoserved', 'match_score']

    def get_email(self, obj):
        if isinstance(obj, dict):
            return obj.get('email')
        return obj.user.email if obj.user else None
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"