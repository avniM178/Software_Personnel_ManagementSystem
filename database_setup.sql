USE spms_db;

-- Login module expects users.username and users.password.
-- Run only if your existing users table does NOT already have these columns.
-- Inspect first with: DESCRIBE users;

-- Example only; adapt this INSERT to your existing users table:
-- INSERT INTO users (username, password, role)
-- VALUES ('admin', SHA2('Admin@123', 256), 'Admin');

-- Existing employee table from your screenshot:
-- employee_id, employee_name, email, phone, gender, designation,
-- department_id, joining_date, employment_status, created_at

-- Check all six table structures:
SHOW TABLES;
DESCRIBE users;
DESCRIBE departments;
DESCRIBE employees;
DESCRIBE attendance;
DESCRIBE leave_requests;
DESCRIBE salary;
