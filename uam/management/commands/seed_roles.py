from django.core.management.base import BaseCommand
from uam.models import Role

class Command(BaseCommand):
    help = 'Seed the default roles based on BRD (Super Admin, HR Manager, Finance, Karyawan)'

    def handle(self, *args, **kwargs):
        default_roles = ['Super Admin', 'HR Manager', 'Finance', 'Karyawan']
        
        for role_name in default_roles:
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created role "{role_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Role "{role_name}" already exists'))
                
        self.stdout.write(self.style.SUCCESS('Role seeding finished!'))
