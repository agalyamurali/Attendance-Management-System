-- =====================================================================
-- Mini Attendance Management System — Database Schema
-- Twite AI Technologies — Technical Assessment
-- =====================================================================
-- Design notes (also explained in README):
--
-- 1. `users` and `employees` are intentionally SEPARATE tables.
--    `users` = login accounts for people operating the system (admins).
--    `employees` = the people whose attendance is being tracked.
--    They are not linked because this assessment has no employee
--    self-login requirement. Admin marks attendance on employees' behalf.
--
-- 2. Status columns (`employees.status`, `attendance.status`,
--    `users.role`) are VARCHAR, NOT a MySQL ENUM type.
--    This is an intentional trade-off:
--      - MySQL ENUM   -> stronger DB-level enforcement, but changing
--                        the allowed values later requires ALTER TABLE.
--      - VARCHAR      -> DB stays flexible; validity is enforced by the
--                        application (Pydantic + Python Enum), which is
--                        the single source of truth for business rules.
--    Since the API is the only write path into this database, the
--    application-level guarantee is sufficient here, and it keeps the
--    system easy to extend live in the interview (new status = one line
--    of Python, no migration).
--
-- 3. Duplicate attendance prevention IS enforced at the DB level via
--    UNIQUE(employee_id, attendance_date), because this protects data
--    integrity even if application logic has a bug or a race condition —
--    unlike status validity, this is not something we want to rely on
--    the application alone to guarantee.
--
-- 4. Employee deletion is a SOFT DELETE, not a hard delete.
--    Attendance records are historical business data (proof of presence/
--    absence on a given day) and must never disappear just because an
--    employee record changes. The "Delete Employee" action in the API
--    sets employees.status = 'INACTIVE' rather than removing the row.
--    The employees -> attendance foreign key uses ON DELETE RESTRICT
--    (MySQL's default), which means the database will refuse a hard
--    DELETE on any employee that still has attendance rows. This makes
--    accidental data loss a hard error instead of a silent cascade,
--    and keeps the soft-delete behavior enforced at two levels:
--    the service layer chooses to deactivate rather than delete, and
--    the database physically blocks deletion of an employee with
--    attendance history even if that service rule were ever bypassed.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS attendance_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE attendance_db;

-- ---------------------------------------------------------------------
-- Table: users
-- Login accounts for administrators operating the system.
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,      -- bcrypt hash, never plain text
    role            VARCHAR(20)     NOT NULL DEFAULT 'ADMIN',
                                                     -- app-level enum: ADMIN
                                                     -- (kept as VARCHAR for future roles)
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_username UNIQUE (username)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: employees
-- The people whose attendance is tracked.
-- ---------------------------------------------------------------------
CREATE TABLE employees (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_code   VARCHAR(20)     NOT NULL,       -- human-facing ID, e.g. EMP001
    name            VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    mobile          VARCHAR(15)     NOT NULL,
    department      VARCHAR(50)     NOT NULL,
    designation     VARCHAR(50)     NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'ACTIVE',
                                                     -- app-level enum: ACTIVE, INACTIVE
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_employees_employee_code UNIQUE (employee_code),
    CONSTRAINT uq_employees_email UNIQUE (email)
) ENGINE=InnoDB;

-- Index to support department filtering (GET /api/employees?department=IT)
CREATE INDEX idx_employees_department ON employees (department);

-- Index to support status filtering (GET /api/employees?status=ACTIVE)
CREATE INDEX idx_employees_status ON employees (status);

-- Composite index to support the common combined filter
-- (department + status together), e.g. "Active employees in IT"
CREATE INDEX idx_employees_department_status ON employees (department, status);

-- ---------------------------------------------------------------------
-- Table: attendance
-- One row per employee per date.
-- ---------------------------------------------------------------------
CREATE TABLE attendance (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_id         BIGINT UNSIGNED NOT NULL,
    attendance_date     DATE            NOT NULL,
    check_in            TIME            NULL,       -- nullable: e.g. ABSENT has no check-in
    check_out           TIME            NULL,
    status              VARCHAR(15)     NOT NULL,
                                                     -- app-level enum: PRESENT, ABSENT,
                                                     -- HALF_DAY, ON_LEAVE
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_attendance_employee
        FOREIGN KEY (employee_id) REFERENCES employees(id)
        ON DELETE RESTRICT,
        -- Attendance history is preserved deliberately (see note 4 above).
        -- RESTRICT means MySQL will reject any attempt to hard-delete an
        -- employee row while attendance records referencing it still
        -- exist. In normal operation the API never even attempts that
        -- hard delete — "Delete Employee" performs a soft delete
        -- (status -> INACTIVE) instead. RESTRICT here is a safety net,
        -- not the primary mechanism.

    CONSTRAINT uq_attendance_employee_date
        UNIQUE (employee_id, attendance_date)
        -- THE core business rule enforced at the DB level:
        -- one attendance record per employee per day, no duplicates,
        -- even under concurrent requests.
) ENGINE=InnoDB;

-- Index to support "attendance on a given date" queries
-- (e.g. dashboard "present today / absent today", GET /api/attendance?date=...)
CREATE INDEX idx_attendance_date ON attendance (attendance_date);

-- Note: idx on (employee_id, attendance_date) is already provided by the
-- UNIQUE constraint above, which MySQL uses as an index automatically.
-- This also serves "employee-wise attendance history" queries efficiently.

-- =====================================================================
-- Seed data: one demo admin account
-- Username: admin
-- purposes — never store or log plain-text passwords in a real system)
-- Hash generated via passlib/bcrypt — see backend/app/core/security.py
-- =====================================================================
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$wTCmGTDX2DCSxa8iXOebOul2Xc3.Dg13K979QEVukwlwkUNfsnwuu', 'ADMIN');
