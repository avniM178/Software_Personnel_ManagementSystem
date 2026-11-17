SOFTWARE PERSONNEL MANAGEMENT SYSTEM (SPMS)
=============================================

1. Open this folder in VS Code.
2. Edit config.py and enter your MySQL password.
3. Install packages:
       python3 -m pip install -r requirements.txt
4. Confirm database spms_db contains:
       users, departments, employees, attendance, leave_requests, salary
5. Login requirements:
       users table must contain username and password columns.
       role is optional.
   Password may be plain text for a classroom demo or SHA-256 hash.
   Example hash for Admin@123 can be inserted using MySQL SHA2().
6. Start:
       python3 main.py

Project screens:
- Login
- Overview dashboard with record counts
- Employees
- Departments
- Attendance
- Leave Requests
- Salary
- User Accounts

IMPORTANT DATABASE NOTES
------------------------
Your employees table screenshot matches the employee fields expected.
The remaining management screens inspect each table using SHOW COLUMNS,
so they do not assume fixed column names.

This is an intermediate college project starter, not a production HR/payroll
system. Generic screens provide CRUD, not full business workflows. For example,
leave approval, payroll calculations, attendance rules, role permissions,
password reset and PDF/Excel reports should be implemented and tested as
separate features.

Before using delete, understand your foreign-key relationships. A referenced
record may not be deletable.

If your users table does not have username/password columns, do not change
your database blindly. Run DESCRIBE users and adjust the login SELECT and
password field mapping in modules/login.py.
