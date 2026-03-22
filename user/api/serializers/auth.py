from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def is_valid(self, *, raise_exception=False):
        # Alias 'email' to 'username' before validation for flexible auth
        if 'email' in self.initial_data and 'username' not in self.initial_data:
            # Handle potential immutability of initial_data (e.g. QueryDict)
            if hasattr(self.initial_data, 'copy'):
                self.initial_data = self.initial_data.copy()
            self.initial_data['username'] = self.initial_data['email']
        return super().is_valid(raise_exception=raise_exception)

    def validate(self, attrs):
        # Now 'username' is already in 'attrs' because of is_valid mapping
            
        logger.info(f"Validating login for attrs: {attrs.keys()}")
        try:
            data = super().validate(attrs)
            data['user'] = UserSerializer(self.user).data
            logger.info(f"Login successful for user: {self.user}")
            return data
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise e
