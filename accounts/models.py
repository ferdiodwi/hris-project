from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from hris_project.common.encrypted_fields import (
    EncryptedCharField,
)

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Default behavior, just mapped for Django's needs
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser):
    # Kolom disesuaikan dengan skema SQL
    username = models.CharField(max_length=150, unique=True)
    email = models.CharField(max_length=150, unique=True)
    
    # Override password agar sesuai dengan kolom password_hash
    password = models.CharField(max_length=255, db_column='password_hash')
    
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'User'

    def __str__(self):
        return self.username

class Employee(models.Model):
    user = models.OneToOneField('User', on_delete=models.RESTRICT, related_name='employee_profile')
    employee_code = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    job_title = models.ForeignKey('organization.JobTitle', on_delete=models.RESTRICT, related_name='employees')
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    phone = models.CharField(max_length=30, null=True, blank=True)
    emergency_contact = models.CharField(max_length=150, null=True, blank=True)
    bpjs_no = models.CharField(max_length=30, null=True, blank=True)
    npwp_no = EncryptedCharField(
    null=True,
    blank=True,
)
    status = models.CharField(max_length=20, default='active')
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'Employee'

    def clean(self):
        super().clean()
        if self.reports_to_id and self.id and self.reports_to_id == self.id:
            raise ValidationError({'reports_to': 'Seorang karyawan tidak boleh menjadi atasan bagi dirinya sendiri.'})

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"

class EmployeeHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='history_records')
    event_type = models.CharField(max_length=30)
    old_job_title = models.ForeignKey('organization.JobTitle', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    new_job_title = models.ForeignKey('organization.JobTitle', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    effective_date = models.DateField()
    note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'EmployeeHistory'

    def __str__(self):
        return f"{self.employee.full_name} - {self.event_type} ({self.effective_date})"
