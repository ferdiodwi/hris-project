from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from uam.models import Role, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Membuat akun Super Admin dan menghubungkannya dengan Role "Super Admin"'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username untuk Super Admin')
        parser.add_argument('--email', type=str, help='Email untuk Super Admin')
        parser.add_argument('--password', type=str, help='Password untuk Super Admin')

    def handle(self, *args, **kwargs):
        import getpass

        username = kwargs.get('username')
        while not username:
            username = input('Username: ')

        email = kwargs.get('email')
        while not email:
            email = input('Email: ')

        password = kwargs.get('password')
        while not password:
            password = getpass.getpass('Password: ')

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
