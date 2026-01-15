from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'total_points', 'created_at']
        read_only_fields = ['id', 'total_points', 'created_at']


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_points = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    transactions_today = serializers.IntegerField()
    points_earned_today = serializers.IntegerField()
    favorite_material = serializers.CharField(allow_null=True)
    
    
class ErrorResponseSerializer(serializers.Serializer):
    """Standardized error response"""
    error = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()