-- =====================================================================
-- HRIS DATABASE SCHEMA
-- Project   : Pengembangan Aplikasi HRIS
-- Engine    : MySQL 8.x
-- Framework : Django (models mapped 1:1 to tables below)
-- Generated : 2026-08-15
--
-- Urutan CREATE TABLE mengikuti urutan dependency (FK).
-- Jalankan file ini dari atas ke bawah tanpa diubah urutannya.
-- =====================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET NAMES utf8mb4;

-- =====================================================================
-- MODULE: ACCOUNTS (Login & Autentikasi)
-- =====================================================================

CREATE TABLE `User` (
  `id`            BIGINT AUTO_INCREMENT,
  `username`      VARCHAR(150) NOT NULL,
  `email`         VARCHAR(150) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `is_active`     BOOLEAN NOT NULL DEFAULT TRUE,
  `last_login`    DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_username` (`username`),
  UNIQUE KEY `uq_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: ORGANIZATION MANAGEMENT
-- =====================================================================

CREATE TABLE `Branch` (
  `id`         BIGINT AUTO_INCREMENT,
  `name`       VARCHAR(100) NOT NULL,
  `address`    VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Directorate` (
  `id`         BIGINT AUTO_INCREMENT,
  `branch_id`  BIGINT NOT NULL,
  `name`       VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_directorate_branch` (`branch_id`),
  CONSTRAINT `fk_directorate_branch`
    FOREIGN KEY (`branch_id`) REFERENCES `Branch`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Division` (
  `id`              BIGINT AUTO_INCREMENT,
  `directorate_id`  BIGINT NOT NULL,
  `name`            VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_division_directorate` (`directorate_id`),
  CONSTRAINT `fk_division_directorate`
    FOREIGN KEY (`directorate_id`) REFERENCES `Directorate`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Department` (
  `id`          BIGINT AUTO_INCREMENT,
  `division_id` BIGINT NOT NULL,
  `name`        VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_department_division` (`division_id`),
  CONSTRAINT `fk_department_division`
    FOREIGN KEY (`division_id`) REFERENCES `Division`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `JobTitle` (
  `id`             BIGINT AUTO_INCREMENT,
  `department_id`  BIGINT NOT NULL,
  `name`           VARCHAR(100) NOT NULL,
  `job_level`      VARCHAR(50) NULL,
  PRIMARY KEY (`id`),
  KEY `idx_jobtitle_department` (`department_id`),
  CONSTRAINT `fk_jobtitle_department`
    FOREIGN KEY (`department_id`) REFERENCES `Department`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: USER MANAGEMENT (Core HR)
-- =====================================================================

CREATE TABLE `Employee` (
  `id`                  BIGINT AUTO_INCREMENT,
  `user_id`             BIGINT NOT NULL,
  `employee_code`       VARCHAR(30) NOT NULL,
  `full_name`           VARCHAR(150) NOT NULL,
  `job_title_id`        BIGINT NOT NULL,
  `reports_to_id`       BIGINT NULL,
  `phone`               VARCHAR(30) NULL,
  `emergency_contact`   VARCHAR(150) NULL,
  `bpjs_no`             VARCHAR(30) NULL,
  `npwp_no`             VARCHAR(30) NULL,
  `status`              VARCHAR(20) NOT NULL DEFAULT 'active',
  `hire_date`           DATE NULL,
  `termination_date`    DATE NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_employee_code` (`employee_code`),
  UNIQUE KEY `uq_employee_user` (`user_id`),
  KEY `idx_employee_jobtitle` (`job_title_id`),
  KEY `idx_employee_reportsto` (`reports_to_id`),
  CONSTRAINT `fk_employee_user`
    FOREIGN KEY (`user_id`) REFERENCES `User`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_employee_jobtitle`
    FOREIGN KEY (`job_title_id`) REFERENCES `JobTitle`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_employee_reportsto`
    FOREIGN KEY (`reports_to_id`) REFERENCES `Employee`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `EmployeeHistory` (
  `id`               BIGINT AUTO_INCREMENT,
  `employee_id`      BIGINT NOT NULL,
  `event_type`       VARCHAR(30) NOT NULL, -- onboarding, mutasi, promosi, offboarding
  `old_job_title_id` BIGINT NULL,
  `new_job_title_id` BIGINT NULL,
  `effective_date`   DATE NOT NULL,
  `note`             TEXT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_history_employee` (`employee_id`),
  CONSTRAINT `fk_history_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_history_old_jobtitle`
    FOREIGN KEY (`old_job_title_id`) REFERENCES `JobTitle`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_history_new_jobtitle`
    FOREIGN KEY (`new_job_title_id`) REFERENCES `JobTitle`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: USER ACCESS MANAGEMENT (RBAC)
-- =====================================================================

CREATE TABLE `Role` (
  `id`          BIGINT AUTO_INCREMENT,
  `name`        VARCHAR(50) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Permission` (
  `id`         BIGINT AUTO_INCREMENT,
  `module`     VARCHAR(50) NOT NULL,
  `can_read`   BOOLEAN NOT NULL DEFAULT FALSE,
  `can_write`  BOOLEAN NOT NULL DEFAULT FALSE,
  `can_delete` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `UserRole` (
  `id`      BIGINT AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `role_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_userrole` (`user_id`, `role_id`),
  KEY `idx_userrole_role` (`role_id`),
  CONSTRAINT `fk_userrole_user`
    FOREIGN KEY (`user_id`) REFERENCES `User`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_userrole_role`
    FOREIGN KEY (`role_id`) REFERENCES `Role`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `RolePermission` (
  `id`            BIGINT AUTO_INCREMENT,
  `role_id`       BIGINT NOT NULL,
  `permission_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_rolepermission` (`role_id`, `permission_id`),
  KEY `idx_rolepermission_permission` (`permission_id`),
  CONSTRAINT `fk_rolepermission_role`
    FOREIGN KEY (`role_id`) REFERENCES `Role`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_rolepermission_permission`
    FOREIGN KEY (`permission_id`) REFERENCES `Permission`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: SHIFTING
-- =====================================================================

CREATE TABLE `ShiftMaster` (
  `id`                BIGINT AUTO_INCREMENT,
  `name`              VARCHAR(50) NOT NULL,
  `start_time`        TIME NOT NULL,
  `end_time`          TIME NOT NULL,
  `tolerance_minutes` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ShiftRoster` (
  `id`               BIGINT AUTO_INCREMENT,
  `employee_id`      BIGINT NOT NULL,
  `shift_master_id`  BIGINT NOT NULL,
  `date`             DATE NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_roster_employee_date` (`employee_id`, `date`),
  KEY `idx_roster_shift` (`shift_master_id`),
  CONSTRAINT `fk_roster_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_roster_shift`
    FOREIGN KEY (`shift_master_id`) REFERENCES `ShiftMaster`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: ATTENDANCE MANAGEMENT
-- =====================================================================

CREATE TABLE `AttendanceLog` (
  `id`                  BIGINT AUTO_INCREMENT,
  `employee_id`         BIGINT NOT NULL,
  `roster_id`           BIGINT NULL,
  `clock_in_time`       DATETIME NULL,
  `clock_out_time`      DATETIME NULL,
  `clock_in_lat`        DECIMAL(10,6) NULL,
  `clock_in_lng`        DECIMAL(10,6) NULL,
  `clock_in_photo_url`  VARCHAR(255) NULL,
  `status`              VARCHAR(20) NOT NULL DEFAULT 'present', -- present, late, absent, early_leave
  PRIMARY KEY (`id`),
  KEY `idx_attendance_employee` (`employee_id`),
  KEY `idx_attendance_roster` (`roster_id`),
  CONSTRAINT `fk_attendance_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_roster`
    FOREIGN KEY (`roster_id`) REFERENCES `ShiftRoster`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: APPROVAL MANAGEMENT (Cuti, Izin, dll)
-- =====================================================================

CREATE TABLE `ApprovalRequest` (
  `id`              BIGINT AUTO_INCREMENT,
  `employee_id`     BIGINT NOT NULL,
  `request_type`    VARCHAR(30) NOT NULL, -- cuti_tahunan, izin, sakit, reimbursement, lembur
  `start_date`      DATE NULL,
  `end_date`        DATE NULL,
  `attachment_url`  VARCHAR(255) NULL,
  `amount`          DECIMAL(15,2) NULL,
  `reason`          TEXT NULL,
  `status`          VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_apprequest_employee` (`employee_id`),
  CONSTRAINT `fk_apprequest_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ApprovalStep` (
  `id`           BIGINT AUTO_INCREMENT,
  `request_id`   BIGINT NOT NULL,
  `approver_id`  BIGINT NOT NULL,
  `level`        INT NOT NULL DEFAULT 1,
  `decision`     VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
  `decided_at`   DATETIME NULL,
  `note`         TEXT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_appstep_request` (`request_id`),
  KEY `idx_appstep_approver` (`approver_id`),
  CONSTRAINT `fk_appstep_request`
    FOREIGN KEY (`request_id`) REFERENCES `ApprovalRequest`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_appstep_approver`
    FOREIGN KEY (`approver_id`) REFERENCES `Employee`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: PAYROLL
-- =====================================================================

CREATE TABLE `SalaryComponent` (
  `id`              BIGINT AUTO_INCREMENT,
  `employee_id`     BIGINT NOT NULL,
  `component_type`  VARCHAR(20) NOT NULL, -- earning, deduction
  `name`            VARCHAR(100) NOT NULL,
  `amount`          DECIMAL(15,2) NOT NULL DEFAULT 0,
  `is_active`       BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`id`),
  KEY `idx_salarycomponent_employee` (`employee_id`),
  CONSTRAINT `fk_salarycomponent_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `PayrollRun` (
  `id`            BIGINT AUTO_INCREMENT,
  `period_month`  INT NOT NULL,
  `period_year`   INT NOT NULL,
  `status`        VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, processing, completed
  `processed_at`  DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payrollrun_period` (`period_month`, `period_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Payslip` (
  `id`               BIGINT AUTO_INCREMENT,
  `payroll_run_id`   BIGINT NOT NULL,
  `employee_id`      BIGINT NOT NULL,
  `gross_salary`     DECIMAL(15,2) NOT NULL DEFAULT 0,
  `pph21_amount`     DECIMAL(15,2) NOT NULL DEFAULT 0,
  `bpjs_amount`      DECIMAL(15,2) NOT NULL DEFAULT 0,
  `total_deduction`  DECIMAL(15,2) NOT NULL DEFAULT 0,
  `net_salary`       DECIMAL(15,2) NOT NULL DEFAULT 0,
  `pdf_url`          VARCHAR(255) NULL,
  `bank_account_no`  VARCHAR(30) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payslip_run_employee` (`payroll_run_id`, `employee_id`),
  KEY `idx_payslip_employee` (`employee_id`),
  CONSTRAINT `fk_payslip_run`
    FOREIGN KEY (`payroll_run_id`) REFERENCES `PayrollRun`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_payslip_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MODULE: KPI (Key Performance Indicator)
-- =====================================================================

CREATE TABLE `KpiGoal` (
  `id`            BIGINT AUTO_INCREMENT,
  `employee_id`   BIGINT NOT NULL,
  `period`        VARCHAR(20) NOT NULL, -- e.g. '2026-Q1'
  `title`         VARCHAR(150) NOT NULL,
  `weight`        DECIMAL(5,2) NOT NULL DEFAULT 0,
  `target_value`  VARCHAR(100) NULL,
  PRIMARY KEY (`id`),
  KEY `idx_kpigoal_employee` (`employee_id`),
  CONSTRAINT `fk_kpigoal_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `KpiAppraisal` (
  `id`               BIGINT AUTO_INCREMENT,
  `goal_id`          BIGINT NOT NULL,
  `appraiser_id`     BIGINT NOT NULL,
  `appraisal_type`   VARCHAR(20) NOT NULL, -- manager, peer, self
  `score`            DECIMAL(5,2) NOT NULL DEFAULT 0,
  `comments`         TEXT NULL,
  `submitted_at`     DATETIME NULL,
  PRIMARY KEY (`id`),
  KEY `idx_kpiappraisal_goal` (`goal_id`),
  KEY `idx_kpiappraisal_appraiser` (`appraiser_id`),
  CONSTRAINT `fk_kpiappraisal_goal`
    FOREIGN KEY (`goal_id`) REFERENCES `KpiGoal`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_kpiappraisal_appraiser`
    FOREIGN KEY (`appraiser_id`) REFERENCES `Employee`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `KpiTask` (
  `id`           BIGINT AUTO_INCREMENT,
  `goal_id`      BIGINT NOT NULL,
  `employee_id`  BIGINT NOT NULL,
  `title`        VARCHAR(150) NOT NULL,
  `description`  TEXT NULL,
  `status`       VARCHAR(20) NOT NULL DEFAULT 'todo', -- todo, in_progress, done
  `due_date`     DATE NULL,
  PRIMARY KEY (`id`),
  KEY `idx_kpitask_goal` (`goal_id`),
  KEY `idx_kpitask_employee` (`employee_id`),
  CONSTRAINT `fk_kpitask_goal`
    FOREIGN KEY (`goal_id`) REFERENCES `KpiGoal`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_kpitask_employee`
    FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- END OF SCHEMA
-- =====================================================================
