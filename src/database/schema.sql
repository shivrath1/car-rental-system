-- =====================================================================
-- Car Rental System — Database Schema
-- =====================================================================
-- This file defines all tables for the Car Rental System.
-- It is executed automatically by DBConnection on first run when the
-- database file does not yet exist, so no manual setup is required.
--
-- Uses Single Table Inheritance (STI) for the users table:
-- one table holds Customers, Admins, and Guests, differentiated by
-- the 'role' column. Role-specific fields are nullable.
-- =====================================================================


-- ---------------------------------------------------------------------
-- USERS table
-- Stores all user types: customer, admin, guest (Single Table Inheritance)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE,                          -- login ID; NULL for guests
    password_hash   TEXT,                                 -- hashed password; NULL for guests
    full_name       TEXT NOT NULL,                        -- display name; used by everyone
    email           TEXT NOT NULL,
    phone           TEXT,
    role            TEXT NOT NULL CHECK(role IN ('customer', 'admin', 'guest')),

    -- Role-specific (nullable) columns
    loyalty_points  INTEGER DEFAULT 0,                    -- customers only
    admin_level     TEXT,                                 -- admins only ('super', 'regular')

    is_active       INTEGER NOT NULL DEFAULT 1,           -- 0 = deactivated, 1 = active
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ---------------------------------------------------------------------
-- CARS table
-- Holds physical car records. Soft-deleted via is_active flag so that
-- past bookings still reference valid car data.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cars (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    make            TEXT NOT NULL,
    model           TEXT NOT NULL,
    year            INTEGER,
    mileage         REAL,
    base_rate       REAL NOT NULL,                        -- daily base rental rate

    is_available    INTEGER NOT NULL DEFAULT 1,           -- 0 = currently rented, 1 = available
    is_active       INTEGER NOT NULL DEFAULT 1,           -- 0 = soft-deleted, 1 = active

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ---------------------------------------------------------------------
-- BOOKINGS table
-- Central table linking users (any type) and cars with rental details.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    car_id          INTEGER NOT NULL,

    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    duration_days   INTEGER,                              -- derived from dates for convenience

    status          TEXT NOT NULL CHECK(status IN ('confirmed', 'cancelled', 'overridden', 'completed')),
    total_amount    REAL NOT NULL,
    payment_status  TEXT CHECK(payment_status IN ('paid', 'refunded', 'pending', 'failed')),

    notes           TEXT,                                 -- admin override notes, etc

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (car_id)  REFERENCES cars(id)
);


-- ---------------------------------------------------------------------
-- PRICE_BREAKDOWNS table
-- Smart pricing detail per booking. One-to-one with bookings (UNIQUE FK).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS price_breakdowns (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id          INTEGER NOT NULL UNIQUE,          -- UNIQUE enforces 1:1

    base_rate           REAL NOT NULL,                    -- per-day base rate at time of booking
    duration_discount   REAL DEFAULT 0,                   -- discount for longer rentals
    loyalty_discount    REAL DEFAULT 0,                   -- customer loyalty discount
    seasonal_charge     REAL DEFAULT 0,                   -- peak season surcharge
    lead_time_charge    REAL DEFAULT 0,                   -- last-minute booking surcharge

    final_rate          REAL NOT NULL,                    -- final per-day rate after adjustments
    duration_days       INTEGER NOT NULL,
    total_amount        REAL NOT NULL,                    -- final_rate * duration_days

    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);


-- ---------------------------------------------------------------------
-- PAYMENTS table
-- Tracks all financial transactions for bookings.
-- Positive amount = charge, negative amount = refund.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id          INTEGER NOT NULL,

    amount              REAL NOT NULL,                    -- positive: charge, negative: refund
    payment_method      TEXT,                             -- e.g. 'card', 'cash'
    transaction_ref     TEXT,                             -- gateway reference (mock for this project)
    status              TEXT NOT NULL CHECK(status IN ('success', 'failed', 'pending', 'refunded')),

    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);


-- ---------------------------------------------------------------------
-- INDEXES — for query performance
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_username    ON users(username);
CREATE INDEX IF NOT EXISTS idx_cars_available    ON cars(is_available, is_active);
CREATE INDEX IF NOT EXISTS idx_bookings_user     ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_car      ON bookings(car_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status   ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_payments_booking  ON payments(booking_id);


-- ---------------------------------------------------------------------
-- SEED DATA — Default admin account
-- This ensures there's always at least one admin to access the system.
-- Password is 'admin123' (hashed using SHA-256 by the AuthService).
-- The hash below is the SHA-256 of 'admin123' for first-run login.
-- IMPORTANT: change this password immediately after first login in production.
-- ---------------------------------------------------------------------
INSERT OR IGNORE INTO users (username, password_hash, full_name, email, phone, role, admin_level)
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'System Administrator',
    'admin@carrental.local',
    '+64-000-000-0000',
    'admin',
    'super'
);