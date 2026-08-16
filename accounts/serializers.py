from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Employee, EmployeeHistory

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Gunakan create_user agar password di-hash secara otomatis
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('id',)

    def validate(self, data):
        reports_to = data.get('reports_to')
        # self.instance is not None when updating
        if reports_to and self.instance and reports_to.id == self.instance.id:
            raise serializers.ValidationError({"reports_to": "Seorang karyawan tidak boleh menjadi atasan bagi dirinya sendiri."})
        return data

class EmployeeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHistory
        fields = '__all__'
        read_only_fields = ('id',)
