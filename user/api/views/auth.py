from rest_framework_simplejwt.views import TokenObtainPairView
from user.api.serializers.auth import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
