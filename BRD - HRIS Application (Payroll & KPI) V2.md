## Business Requirements Document (BRD) - Sistem Informasi SDM (HRIS)

Nama Proyek: Pengembangan Aplikasi HRIS

## 1. Ringkasan Eksekutif (Executive Summary)

Dokumen ini mendefinisikan persyaratan bisnis untuk pengembangan Sistem Informasi Sumber Daya Manusia (HRIS) yang komprehensif. Tujuan dari sistem ini adalah untuk mendigitalisasi dan mengotomatisasi proses HR melalui serangkaian modul terpadu. Sistem ini dirancang untuk meningkatkan efisiensi operasional HR, meminimalisir kesalahan perhitungan, mempermudah manajemen hierarki organisasi, serta memberikan pengalaman sistem mandiri (Employee Self-Service/ESS) yang terpusat dan intuitif bagi seluruh karyawan.

## 2. Ruang Lingkup Proyek (Project Scope)

## 2.1. Dalam Ruang Lingkup (In-Scope)

Pengembangan fase ini akan mencakup modul-modul inti berikut:

- Attendance Management: Pengelolaan data absensi harian karyawan.

- Approval Management: Sistem alur persetujuan untuk cuti, izin, dan pengajuan lainnya.

- Payroll: Otomatisasi perhitungan gaji, pajak, dan potongan.

- User Management: Pengelolaan data profil dan rekam jejak karyawan (Core HR).

- User Access Management: Manajemen hak akses dan otorisasi keamanan berbasis peran.

- KPI: Pengelolaan target dan evaluasi kinerja karyawan.

- Shifting: Pengaturan jadwal kerja dan rotasi karyawan.

- Organization Management: Pemetaan struktur organisasi, divisi, departemen, dan jabatan.

## 2.2. Luar Ruang Lingkup (Out-of-Scope)

- Modul rekrutmen tingkat lanjut (Applicant Tracking System / ATS).

- Sistem manajemen pembelajaran karyawan (Learning Management System / LMS).


## 3. Persyaratan Fungsional (Functional Requirements)

## 3.1. Organization Management (Divisi, dll)

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| ORG-01 | Struktur Perusahaan | Admin HR dapat membuat, |
|   |   | mengedit, dan menghapus |
|   |   | entitas struktur seperti |
|   |   | Cabang, Direktorat, Divisi, |
|   |   | dan Departemen. |
| ORG-02 | Manajemen Jabatan | Definisi Job Title, Job Level, |
|   |   | dan penetapan Reporting |
|   |   | Line (Atasan Langsung) |
|   |   | untuk mendukung alur |
|   |   | persetujuan. |

## 3.2. User Management

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| USR-01 | Database Karyawan (Core | Pusat data informasi pribadi, |
|   | HR) | kontak darurat, informasi |
|   |   | BPJS, NPWP, dan riwayat |
|   |   | pendidikan/pekerjaan |
|   |   | karyawan. |
| USR-02 | Siklus Karyawan | Proses administratif terpusat |
|   |   | untuk Onboarding |
|   |   | (karyawan baru), |
|   |   | Mutasi/Promosi, dan |
|   |   | Offboarding (karyawan |
|   |   | resign/terminasi). |


## 3.3. User Access Management

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| UAM-01 | Role-Based Access Control Konfigurasi peran pengguna |   |
|   |   | (Super Admin, HR Manager, |
|   |   | Finance, Karyawan) dengan |
|   |   | hak akses baca/tulis/hapus |
|   |   | yang spesifik tiap modul. |
| UAM-02 | Manajemen Autentikasi | Fasilitas pembuatan akun |
|   |   | awal, login aman, dan fitur |
|   |   | pemulihan kata sandi |
|   |   | (Forgot Password). |

## 3.4. Attendance Management

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| ATT-01 | Clock-In & Clock-Out | Pencatatan waktu hadir |
|   |   | secara real-time melalui |
|   |   | web/mobile ESS dengan |
|   |   | dukungan tag lokasi (GPS) |
|   |   | dan validasi foto (Selfie). |
| ATT-02 | Log & Rekapitulasi | Dashboard untuk memonitor |
|   |   | keterlambatan, pulang awal, |
|   |   | ketidakhadiran (mangkir), |
|   |   | dan total jam kerja aktual. |

## 3.5. Shifting


| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| SHF-01 | Pengaturan Master Shift | Pembuatan template jam |
|   |   | kerja shift (misal: Shift Pagi |
|   |   | 08:00-17:00, Shift Malam |
|   |   | 20:00-05:00) beserta aturan |
|   |   | toleransi keterlambatan. |
| SHF-02 | Penjadwalan (Roster) | Fungsionalitas bagi admin |
|   |   | atau manajer untuk |
|   |   | mendistribusikan jadwal shift |
|   |   | secara mingguan/bulanan |
|   |   | kepada anggota tim. |

## 3.6. Approval Management (Cuti, Izin, dll)

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| APP-01 | Pengajuan Mandiri (ESS) | Karyawan dapat |
|   |   | mengajukan Cuti Tahunan, |
|   |   | Izin Khusus, Sakit (upload |
|   |   | surat dokter), Klaim |
|   |   | Reimbursement, dan |
|   |   | Lembur. |
| APP-02 | Multi-level Approval | Notifikasi berjenjang |
|   |   | berdasarkan struktur |
|   |   | organisasi (ORG-02) yang |
|   |   | memungkinkan atasan |
|   |   | langsung (Line Manager) |
|   |   | atau HR untuk menyetujui |
|   |   | (Approve) atau menolak |
|   |   | (Reject) pengajuan. |

## 3.7. Payroll


| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| PAY-01 | Komponen Gaji Dinamis | Konfigurasi variabel Earning |
|   |   | (Gaji Pokok, Tunjangan |
|   |   | Jabatan, Uang Makan |
|   |   | berdasarkan kehadiran) dan |
|   |   | Deduction (Potongan |
|   |   | Keterlambatan, Kasbon). |
| PAY-02 | Kalkulasi PPh 21 & BPJS | Perhitungan pajak |
|   |   | progresif/TER terbaru dan |
|   |   | skema JHT, JP, JKK, JKM, |
|   |   | serta Kesehatan secara |
|   |   | terintegrasi. |
| PAY-03 | Pembuatan Payslip & | Generate slip gaji digital |
|   | Disbursement | ber-password (PDF) dan |
|   |   | penyediaan file berformat |
|   |   | bank untuk eksekusi transfer |
|   |   | masal. |

## 3.8. KPI (Key Performance Indicator)

| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| KPI-01 | Manajemen Target & | Penyusunan target kerja |
|   | Objective | kuartalan/tahunan (Goal |
|   |   | Setting) antara karyawan |
|   |   | dan manajer beserta bobot |
|   |   | pengukurannya. |
| KPI-02 | Siklus Penilaian (Appraisal) | Fasilitas penilaian kinerja |
|   |   | secara periodik oleh atasan, |
|   |   | rekan kerja (peer review), |
|   |   | dan penilaian mandiri |
|   |   | (self-assessment). |


| Kode | Fitur | Deskripsi Kebutuhan |
| --- | --- | --- |
| KPI-03 | Task Management (Tiket | Pembuatan dan pengelolaan |
|   | Penugasan) | tiket tugas (tasks) |
|   |   | sehari-hari yang dapat |
|   |   | ditautkan dengan target KPI |
|   |   | besar. Memiliki status |
|   |   | pelacakan seperti To-Do, In |
|   |   | Progress, dan Done yang |
|   |   | dapat dimonitor atasan |
|   |   | langsung. |

## 4. Persyaratan Non-Fungsional (Non-Functional Requirements)

- Keamanan (Security): Data penting (seperti gaji, nomor rekening, NPWP) harus menggunakan enkripsi tingkat lanjut di sisi database. Manajemen sesi login harus mengikuti standar keamanan OWASP.

- Performa (Performance): Proses perhitungan Payroll untuk seribu karyawan tidak boleh memakan waktu lebih dari 10 menit. Sistem absensi harus memiliki waktu respon < 2 detik per aksi clock-in.

- Skalabilitas (Scalability): Arsitektur harus dirancang sedemikian rupa agar penambahan kapasitas server (horizontal scaling) mudah dilakukan seiring bertambahnya data riwayat (log) absen.

## 5. Asumsi dan Dependensi

- Sistem Organization Management merupakan basis awal yang wajib dikonfigurasi pertama kali agar Approval Management dapat berjalan sempurna.

- Penerapan Role-Based Access Control sangat krusial; kegagalan konfigurasi dapat mengakibatkan karyawan biasa melihat rentang gaji level manajemen.
