# Panduan Pengujian (Testing Guide) Aplikasi HRIS

Dokumen ini berisi urutan pengujian (testing flow) untuk memastikan semua fitur backend yang telah dibuat berfungsi dengan baik sesuai dengan **Business Requirements Document (BRD) V2**.

Anda dapat melakukan pengujian ini menggunakan **Postman** atau **Apidog** dengan mengimpor berkas `HRIS_Postman_Collection.json`.

---

## Prasyarat (Pre-requisites)
1. **Jalankan Server Django:** Pastikan server backend sedang berjalan (`python manage.py runserver`).
2. **Siapkan User Admin:** Pastikan Anda sudah memiliki user "Super Admin". Jika belum ada superuser, buat melalui terminal:
   ```bash
   python manage.py createsuperuser
   ```
3. **Impor Postman Collection:** Impor file `HRIS_Postman_Collection.json` terbaru ke Postman.
4. **Set Environment Variable:** Pastikan variabel `base_url` di Postman mengarah ke `http://localhost:8000`.

---

## Alur Pengujian Utama (End-to-End Flow)

Urutan di bawah ini dirancang mengikuti dependensi antar modul (harus urut dari atas ke bawah).

### 1. Proses Autentikasi (Auth)
Kita membutuhkan token JWT untuk mengakses endpoint lainnya.
- Buka folder **Auth -> Login**.
- Masukkan `username` dan `password` superuser Anda di bagian `form-data`.
- Klik **Send**. 
- **Hasil yang Diharapkan:** Anda akan mendapatkan `access` dan `refresh` token. 
- *Aksi:* Kopi `access` token tersebut, Anda akan menempelkannya di tab **Headers** (dengan format `Bearer <token>`) pada setiap *request* di tahap selanjutnya.

### 2. Modul Organization Management (ORG-01, ORG-02)
Karena Employee membutuhkan struktur organisasi (Job Title), kita harus membuatnya terlebih dahulu secara berjenjang.

1. **Branches:**
   - Gunakan endpoint `POST Create Branch`.
   - Isi form: `name` (misal: "Kantor Pusat"), `address` (misal: "Jakarta").
   - Catat ID Branch yang dikembalikan (misal: `1`).
2. **Directorates:**
   - Gunakan endpoint `POST Create Directorate`.
   - Isi form: `name` ("Direktorat HR & Operasional"), `branch_id` (`1`).
   - Catat ID Directorate.
3. **Divisions:**
   - Gunakan endpoint `POST Create Division`.
   - Isi form: `name` ("Divisi HR"), `directorate_id` (`1`).
4. **Departments:**
   - Gunakan endpoint `POST Create Department`.
   - Isi form: `name` ("Talent Acquisition"), `division_id` (`1`).
5. **Job Titles:**
   - Gunakan endpoint `POST Create Job Title`.
   - Isi form: `name` ("Senior Recruiter"), `job_level` ("Senior"), `department_id` (`1`).
   - Catat ID Job Title yang dihasilkan (Misal: `1`).

*Pastikan semua operasi POST menghasilkan HTTP 201 Created.* Anda juga bisa mengetes GET, PUT, dan DELETE.

### 3. Pembuatan Akun User (UAM-02)
Untuk mendaftarkan karyawan, HR harus membuat akun login-nya (User) terlebih dahulu.
- Buka folder **Auth -> Register**.
- Masukkan `username` (misal: "budi"), `email`, dan `password`.
- **Hasil yang Diharapkan:** HTTP 201 Created. Catat `user_id` yang dihasilkan (Misal: `2`).

### 4. Menentukan Role (UAM-01)
- Buka folder **UAM -> Assign Role**.
- Masukkan `user` (ID user budi, misal `2`) dan `role` (ID Role "Karyawan", biasanya ID `4` jika urutan seed Super Admin, HR Manager, Finance, Karyawan).
- **Hasil yang Diharapkan:** User "budi" kini resmi berstatus Karyawan di sistem RBAC.

### 5. Modul Core HR - Pengelolaan Karyawan (USR-01)
Sekarang buat profil asli karyawannya.
- Buka folder **Core HR (Employees) -> Employees CRUD -> Create Employee**.
- Di bagian form-data, isi:
  - `user`: `2` (ID akun Budi)
  - `employee_code`: "EMP-001"
  - `full_name`: "Budi Santoso"
  - `job_title`: `1` (ID Job Title Senior Recruiter)
  - `bpjs_no` & `npwp_no`: (Isi angka sembarang)
- **Hasil yang Diharapkan:** Profil karyawan berhasil dibuat. Catat ID Employee Budi (Misal: `1`).

### 6. Pengujian Siklus Karyawan & Histori (USR-02)
Mari tes otomatisasi pencatatan riwayat (mutasi, promosi, offboarding). Gunakan endpoint di bawah folder **Employee Actions**.

1. **Onboard Employee:**
   - Buka `POST Onboard Employee` untuk ID `1` (ubah URL jika ID-nya bukan 1).
   - Isi form `note` (misal: "Budi resmi bergabung").
   - **Cek:** HTTP 200.
2. **Mutate Employee:**
   - (Opsional: Buat satu Job Title baru lagi di Organization, misal ID `2` "HR Manager").
   - Buka `POST Mutate Employee`.
   - Isi form `new_job_title_id` (`2`), dan `note` ("Promosi jadi manajer").
   - **Cek:** Profil Budi sekarang berubah job title-nya menjadi `2`.
3. **Cek Employee History:**
   - Buka `GET Get Employee History` untuk ID `1`.
   - **Hasil yang Diharapkan:** Mengembalikan Array/List riwayat Budi. Anda akan melihat 2 objek: event "onboarding" dan event "mutasi".
4. **Offboard Employee:**
   - Buka `POST Offboard Employee`.
   - Isi `note` ("Budi resign").
   - **Cek:** Buka `GET List Employees`, lihat status Budi sekarang berubah menjadi `inactive` dan `termination_date` terisi. Riwayat `offboarding` juga akan tercatat di History.

### 7. Validasi Self-Reference Atasan (Negative Testing)
Untuk memastikan seorang karyawan tidak bisa menjadi atasan dirinya sendiri:
- Buka `PUT Update Employee` (di dalam folder Employees CRUD).
- Ganti/masukkan kolom `reports_to` dengan ID karyawan itu sendiri (Misal Budi ID `1`, isi `reports_to` dengan `1`).
- **Hasil yang Diharapkan:** API menolak *request* (HTTP 400 Bad Request) dan memunculkan *error message*: "Seorang karyawan tidak boleh menjadi atasan bagi dirinya sendiri."

---

## Skenario Error yang Bisa Anda Coba (Negative Case)
- Melakukan *request* ke endpoint tanpa Header `Authorization: Bearer <token>`. Sistem harus mengembalikan status **401 Unauthorized**.
- Mengisi `branch_id` yang tidak eksis di *database* saat membuat `Directorate`. Sistem harus merespons **400 Bad Request**.

Selamat menguji!
