import uuid
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from datetime import date
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from uam.permissions import HasRBACPermission
from .serializers import (
    RegisterSerializer, 
    ForgotPasswordSerializer,
    EmployeeSerializer,
    EmployeeHistorySerializer
)
from .models import Employee, EmployeeHistory
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

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Berhasil logout."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token tidak valid atau gagal diblacklist."}, status=status.HTTP_400_BAD_REQUEST)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    rbac_module = 'User Management'

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        employee = self.get_object()
        history = EmployeeHistory.objects.filter(employee=employee).order_by('-effective_date')
        serializer = EmployeeHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def onboard(self, request, pk=None):
        employee = self.get_object()
        EmployeeHistory.objects.create(
            employee=employee,
            event_type='onboarding',
            new_job_title=employee.job_title,
            effective_date=date.today(),
            note=request.data.get('note', 'Karyawan baru di-onboard.')
        )
        return Response({'message': 'Berhasil onboard karyawan.'})

    @action(detail=True, methods=['post'])
    def mutate(self, request, pk=None):
        employee = self.get_object()
        new_job_title_id = request.data.get('new_job_title_id')
        if not new_job_title_id:
            return Response({'error': 'new_job_title_id wajib diisi.'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_job_title = employee.job_title
        employee.job_title_id = new_job_title_id
        employee.save()

        EmployeeHistory.objects.create(
            employee=employee,
            event_type='mutasi',
            old_job_title=old_job_title,
            new_job_title=employee.job_title,
            effective_date=date.today(),
            note=request.data.get('note', 'Karyawan dimutasi.')
        )
        return Response({'message': 'Berhasil mutasi karyawan.'})

    @action(detail=True, methods=['post'])
    def offboard(self, request, pk=None):
        employee = self.get_object()
        employee.status = 'inactive'
        employee.termination_date = date.today()
        employee.save()

        EmployeeHistory.objects.create(
            employee=employee,
            event_type='offboarding',
            old_job_title=employee.job_title,
            effective_date=date.today(),
            note=request.data.get('note', 'Karyawan di-offboard.')
        )
        return Response({'message': 'Berhasil offboard karyawan.'})

class EmployeeHistoryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeHistory.objects.all()
    serializer_class = EmployeeHistorySerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    rbac_module = 'User Management'
