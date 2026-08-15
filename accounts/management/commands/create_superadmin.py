from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from uam.models import Role, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Membuat akun Super Admin dan menghubungkannya dengan Role "Super Admin"'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username untuk Super Admin')
        parser.add_argument('--email', type=str, required=True, help='Email untuk Super Admin')
        parser.add_argument('--password', type=str, required=True, help='Password untuk Super Admin')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        # 1. Pastikan Role "Super Admin" sudah ada
        role, created = Role.objects.get_or_create(name='Super Admin')
        if created:
            self.stdout.write(self.style.WARNING('Role "Super Admin" belum ada, secara otomatis dibuat.'))

        # 2. Buat User
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User dengan username "{username}" sudah ada!'))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'User "{username}" berhasil dibuat.'))

        # 3. Hubungkan User dengan Role "Super Admin"
        UserRole.objects.create(user=user, role=role)
        self.stdout.write(self.style.SUCCESS(f'User "{username}" berhasil dijadikan Super Admin!'))
