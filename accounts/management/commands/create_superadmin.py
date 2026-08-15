from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from uam.models import Role, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superadmin user and automatically assign the "Super Admin" role to it.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, type=str)
        parser.add_argument('--email', required=True, type=str)
        parser.add_argument('--password', required=True, type=str)

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # 1. Pastikan Role "Super Admin" ada
        role, _ = Role.objects.get_or_create(name='Super Admin')

        # 2. Buat User
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if user_created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Berhasil membuat user "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'User "{username}" sudah ada. Memperbarui password...'))
            user.set_password(password)
            user.save()

        # 3. Assign Role "Super Admin" ke User tersebut
        user_role, role_created = UserRole.objects.get_or_create(user=user, role=role)
        if role_created:
            self.stdout.write(self.style.SUCCESS(f'Berhasil memberikan akses "Super Admin" ke user "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'User "{username}" sudah memiliki akses "Super Admin"'))

        self.stdout.write(self.style.SUCCESS('Proses pembuatan Super Admin selesai!'))
