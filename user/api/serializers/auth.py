import logging

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    is_email_verified = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_email_verified')


class RegisterResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    message = serializers.CharField()


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class ResendVerificationResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, allow_blank=True, required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account already exists with this email address.")
        return normalized

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": ["Passwords do not match."]})
        validate_password(attrs["password1"])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password1"],
            is_active=False,
        )
        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def is_valid(self, *, raise_exception=False):
        if 'email' in self.initial_data and 'username' not in self.initial_data:
            if hasattr(self.initial_data, 'copy'):
                self.initial_data = self.initial_data.copy()
            self.initial_data['username'] = self.initial_data['email']
        return super().is_valid(raise_exception=raise_exception)

    def validate(self, attrs):
        logger.info(f"Validating login for attrs: {attrs.keys()}")
        username = attrs.get("username")
        user = User.objects.filter(username=username).first()
        if user and not user.is_active:
            raise serializers.ValidationError({
                "detail": "Please verify your email address before signing in."
            })
        try:
            data = super().validate(attrs)
            data['user'] = UserSerializer(self.user).data
            logger.info(f"Login successful for user: {self.user}")
            return data
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise e
