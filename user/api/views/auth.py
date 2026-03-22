from rest_framework_simplejwt.views import TokenObtainPairView
from user.api.serializers.auth import CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Login request received with data: {request.data}")
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Validation failed for login: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Validation successful, returning token")
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
