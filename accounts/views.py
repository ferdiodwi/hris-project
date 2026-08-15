import uuid
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from uam.permissions import HasRBACPermission
from .serializers import RegisterSerializer, ForgotPasswordSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # Hanya bisa diakses oleh admin (atau user yang punya modul 'User Management' can_write)
    permission_classes = [IsAuthenticated, HasRBACPermission]
    rbac_module = 'User Management'

    def create(self, request, *args, **kwargs):
        # Override untuk custom response (optional)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        return Response({
            "message": "User berhasil dibuat",
            "user_id": user.id,
            "username": user.username
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny] # Siapapun bisa request forgot password
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            # Simulasi pengiriman token ke email
            reset_token = str(uuid.uuid4())
            print(f"--- SIMULASI EMAIL ---")
            print(f"To: {email}")
            print(f"Subject: Password Reset")
            print(f"Token Anda: {reset_token}")
            print(f"----------------------")
            
            return Response({"message": "Instruksi reset password telah dikirim ke email Anda."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Agar tidak membocorkan informasi apakah email terdaftar atau tidak
            return Response({"message": "Instruksi reset password telah dikirim ke email Anda."}, status=status.HTTP_200_OK)
