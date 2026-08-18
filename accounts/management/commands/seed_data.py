from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Seed demo data: Organization, Accounts (User & Employee), dan UAM (Permission & UserRole)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Hapus semua data seed sebelum mengisi ulang (hati-hati di production!)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        self.stdout.write(self.style.MIGRATE_HEADING('\n===== HRIS Data Seeder =====\n'))

        self._seed_organization()
        self._seed_users_and_employees()
        self._seed_permissions()
        self._seed_user_roles()

        self.stdout.write(self.style.SUCCESS('\n✅ Seeding selesai! Semua data demo berhasil dibuat.\n'))

    # ──────────────────────────────────────────
    # FLUSH
    # ──────────────────────────────────────────
    def _flush(self):
        from accounts.models import Employee, EmployeeHistory, User
        from organization.models import Branch, Directorate, Division, Department, JobTitle
        from uam.models import UserRole, RolePermission, Permission

        self.stdout.write(self.style.WARNING('🗑  Menghapus data lama...'))
        EmployeeHistory.objects.all().delete()
        Employee.objects.all().delete()
        UserRole.objects.all().delete()
        RolePermission.objects.all().delete()
        Permission.objects.all().delete()
        # Hanya hapus Employee & History — User yang sudah ada TIDAK dihapus
        self.stdout.write('   (User asli tidak dihapus, hanya data Employee & UAM-nya)')
        JobTitle.objects.all().delete()
        Department.objects.all().delete()
        Division.objects.all().delete()
        Directorate.objects.all().delete()
        Branch.objects.all().delete()
        self.stdout.write(self.style.WARNING('   Data lama berhasil dihapus.\n'))

    # ──────────────────────────────────────────
    # 1. ORGANIZATION
    # ──────────────────────────────────────────
    def _seed_organization(self):
        from organization.models import Branch, Directorate, Division, Department, JobTitle

        self.stdout.write(self.style.MIGRATE_HEADING('📌 [1/4] Seeding Organization...'))

        # Branch
        branch, _ = Branch.objects.get_or_create(
            name='Kantor Pusat Jakarta',
            defaults={'address': 'Jl. Sudirman No. 88, Jakarta Selatan'},
        )
        self.stdout.write(f'   Branch      : {branch.name}')

        # Directorate
        dir_sdm, _ = Directorate.objects.get_or_create(
            name='Direktorat SDM & Umum', branch=branch,
        )
        dir_it, _ = Directorate.objects.get_or_create(
            name='Direktorat Teknologi & Inovasi', branch=branch,
        )
        dir_fin, _ = Directorate.objects.get_or_create(
            name='Direktorat Keuangan', branch=branch,
        )
        self.stdout.write(f'   Directorate : {dir_sdm.name}, {dir_it.name}, {dir_fin.name}')

        # Division
        div_hr, _ = Division.objects.get_or_create(name='Divisi Human Resources', directorate=dir_sdm)
        div_it, _ = Division.objects.get_or_create(name='Divisi IT & Engineering', directorate=dir_it)
        div_fin, _ = Division.objects.get_or_create(name='Divisi Finance & Accounting', directorate=dir_fin)
        self.stdout.write(f'   Division    : {div_hr.name}, {div_it.name}, {div_fin.name}')

        # Department
        dept_hc, _ = Department.objects.get_or_create(name='Department Human Capital', division=div_hr)
        dept_be, _ = Department.objects.get_or_create(name='Department Backend Engineering', division=div_it)
        dept_acc, _ = Department.objects.get_or_create(name='Department Accounting', division=div_fin)
        self.stdout.write(f'   Department  : {dept_hc.name}, {dept_be.name}, {dept_acc.name}')

        # JobTitle
        jt_data = [
            ('Direktur SDM',                'Direktur',  dept_hc),
            ('HR Manager',                  'Manager',   dept_hc),
            ('HR Staff',                    'Staff',     dept_hc),
            ('Backend Developer Junior',    'Junior',    dept_be),
            ('Backend Developer Senior',    'Senior',    dept_be),
            ('Finance Manager',             'Manager',   dept_acc),
            ('Finance Staff',               'Staff',     dept_acc),
        ]
        self._job_titles = {}
        for name, level, dept in jt_data:
            jt, _ = JobTitle.objects.get_or_create(name=name, department=dept, defaults={'job_level': level})
            self._job_titles[name] = jt

        self.stdout.write(f'   JobTitle    : {len(self._job_titles)} jabatan dibuat')
        self.stdout.write(self.style.SUCCESS('   ✓ Organization selesai'))

    # ──────────────────────────────────────────
    # 2. USER & EMPLOYEE
    # ──────────────────────────────────────────
    def _seed_users_and_employees(self):
        from accounts.models import User, Employee

        self.stdout.write(self.style.MIGRATE_HEADING('\n📌 [2/4] Seeding Users & Employees...'))
        self.stdout.write('   (Auto-create user jika belum ada, skip jika sudah ada)')
        self.stdout.write('   (Urutan: dari jabatan tertinggi ke bawah agar reports_to bisa diisi)')

        self._employees = {}

        # ── Super Admin: user 'admin' ──
        self._get_or_create_user('admin', 'admin@gmail.com', 'admin123')

        # ── Direktur SDM: user 'ferdio' ──
        ferdio = self._get_or_create_user('ferdio', 'ferdio@gmail.com', 'ferdio123')
        emp_ferdio = self._make_employee(
            user=ferdio,
            code='EMP-001',
            name='Ferdio Dwi Syahputra',
            job_title_name='Direktur SDM',
            reports_to=None,
        )
        self._employees['ferdio'] = emp_ferdio

        # ── HR Manager: user 'zidane' ──
        zidane = self._get_or_create_user('zidane', 'zidane@gmail.com', 'zidane123')
        emp_zidane = self._make_employee(
            user=zidane,
            code='EMP-002',
            name='Zidane',
            job_title_name='HR Manager',
            reports_to=emp_ferdio,
        )
        self._employees['zidane'] = emp_zidane

        # ── Backend Developer: user 'alvyn' ──
        alvyn = self._get_or_create_user('alvyn', 'alvyn@gmail.com', 'alvyn123')
        emp_alvyn = self._make_employee(
            user=alvyn,
            code='EMP-003',
            name='Alvyn Akbar',
            job_title_name='Backend Developer Junior',
            reports_to=emp_ferdio,
        )
        self._employees['alvyn'] = emp_alvyn

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(self._employees)} karyawan selesai di-seed'))

    def _get_or_create_user(self, username, email, password):
        """Ambil user jika sudah ada, atau buat baru dengan password default."""
        from accounts.models import User
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'   + User dibuat : {username} | password: {password}')
        else:
            self.stdout.write(f'   ~ User ada    : {username} (ID: {user.id})')
        return user

    def _make_employee(self, user, code, name, job_title_name, reports_to):
        from accounts.models import Employee
        emp, created = Employee.objects.get_or_create(
            employee_code=code,
            defaults={
                'user': user,
                'full_name': name,
                'job_title': self._job_titles[job_title_name],
                'reports_to': reports_to,
                'status': 'active',
            },
        )
        arrow = f'→ atasan: {reports_to.full_name}' if reports_to else '→ (tidak ada atasan)'
        status = 'baru' if created else 'ada'
        self.stdout.write(f'   {"+" if created else "~"} Employee [{status}]: {name} ({job_title_name}) {arrow}')
        return emp

    # ──────────────────────────────────────────
    # 3. PERMISSION
    # ──────────────────────────────────────────
    def _seed_permissions(self):
        from uam.models import Permission, Role, RolePermission

        self.stdout.write(self.style.MIGRATE_HEADING('\n📌 [3/4] Seeding Permissions...'))

        modules = [
            'Organization',
            'User Management',
            'User Access Management',
            'Payroll',
            'Attendance',
            'Shifting',
            'Approvals',
            'KPI',
        ]

        self._permissions = {}
        for module in modules:
            perm, created = Permission.objects.get_or_create(
                module=module,
                defaults={'can_read': True, 'can_write': False, 'can_delete': False},
            )
            self._permissions[module] = perm
            self.stdout.write(f'   {"+" if created else "~"} Permission: {module}')

        # Beri akses penuh ke Super Admin
        super_admin_role = Role.objects.filter(name='Super Admin').first()
        hr_manager_role = Role.objects.filter(name='HR Manager').first()
        finance_role = Role.objects.filter(name='Finance').first()

        if super_admin_role:
            for module, perm in self._permissions.items():
                # Update permission menjadi full access dulu
                perm.can_read = True
                perm.can_write = True
                perm.can_delete = True
                perm.save()
                RolePermission.objects.get_or_create(role=super_admin_role, permission=perm)
            self.stdout.write(f'   ✓ Super Admin: full access semua modul')

        if hr_manager_role:
            for module in ['Organization', 'User Management', 'User Access Management', 'Attendance', 'Shifting', 'Approvals']:
                if module in self._permissions:
                    RolePermission.objects.get_or_create(role=hr_manager_role, permission=self._permissions[module])
            self.stdout.write(f'   ✓ HR Manager: akses Organization, User Mgmt, Attendance, Shifting, Approvals')

        if finance_role:
            for module in ['Payroll']:
                if module in self._permissions:
                    RolePermission.objects.get_or_create(role=finance_role, permission=self._permissions[module])
            self.stdout.write(f'   ✓ Finance: akses Payroll')

        self.stdout.write(self.style.SUCCESS('   ✓ Permissions selesai'))

    # ──────────────────────────────────────────
    # 4. USER ROLE
    # ──────────────────────────────────────────
    def _seed_user_roles(self):
        from uam.models import Role, UserRole

        self.stdout.write(self.style.MIGRATE_HEADING('\n📌 [4/4] Seeding UserRole...'))

        # Tambahkan juga akun 'admin' sebagai Super Admin
        from accounts.models import User
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            super_admin_role = Role.objects.filter(name='Super Admin').first()
            if super_admin_role:
                ur, created = UserRole.objects.get_or_create(user=admin_user, role=super_admin_role)
                self.stdout.write(f'   {"+" if created else "~"} admin → Role: Super Admin')

        role_map = {
            'ferdio': 'Super Admin',  # Direktur = Super Admin
            'zidane': 'HR Manager',
            'alvyn':  'Karyawan',
        }

        for emp_key, role_name in role_map.items():
            emp = self._employees.get(emp_key)
            role = Role.objects.filter(name=role_name).first()
            if emp and role:
                ur, created = UserRole.objects.get_or_create(user=emp.user, role=role)
                self.stdout.write(
                    f'   {"+" if created else "~"} {emp.full_name} → Role: {role_name}'
                )

        self.stdout.write(self.style.SUCCESS('   ✓ UserRole selesai'))
