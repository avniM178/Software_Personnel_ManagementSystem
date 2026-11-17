
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import create_connection
from datetime import datetime, date, timedelta


# ===================== THEME =====================

NAVY = "#17243A"
TEAL = "#168C89"
BG = "#F3F5F8"
WHITE = "#FFFFFF"
TEXT = "#202C3D"
MUTED = "#8490A0"
RED = "#B94B55"


class AttendanceFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=BG, corner_radius=0)

        self.pack(fill="both", expand=True)

        self.employee_map = {}
        self.selected_attendance_id = None

        self.create_interface()
        self.load_employees()
        self.load_attendance()

    # ===================== DATABASE =====================

    def get_connection(self):
        conn = create_connection()

        if conn is None:
            raise ConnectionError("Could not connect to MySQL.")

        return conn

    # ===================== MAIN INTERFACE =====================

    def create_interface(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # HEADER

        ctk.CTkLabel(
            self,
            text="Attendance Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w", pady=(5, 4))

        ctk.CTkLabel(
            self,
            text="Track employee attendance, working hours and daily records.",
            font=ctk.CTkFont(size=13),
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(0, 18))

        # MAIN CONTENT

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=2, column=0, sticky="nsew")

        main.grid_columnconfigure(0, weight=0)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # LEFT FORM

        self.create_form(main)

        # RIGHT TABLE

        self.create_table(main)

    # ===================== ATTENDANCE FORM =====================

    def create_form(self, parent):

        form = ctk.CTkScrollableFrame(
            parent,
            width=280,
            fg_color=WHITE,
            corner_radius=12
        )

        form.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 15)
        )

        ctk.CTkLabel(
            form,
            text="Mark Attendance",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=12, pady=(15, 18))

        # EMPLOYEE

        self.add_label(form, "EMPLOYEE")

        self.employee_dropdown = ctk.CTkOptionMenu(
            form,
            values=["Loading employees..."],
            fg_color=TEAL,
            height=40
        )

        self.employee_dropdown.pack(
            fill="x", padx=12, pady=(3, 12)
        )

        # DATE

        self.add_label(form, "ATTENDANCE DATE")

        self.date_entry = ctk.CTkEntry(
            form,
            height=38,
            placeholder_text="YYYY-MM-DD"
        )

        self.date_entry.pack(
            fill="x", padx=12, pady=(3, 12)
        )

        self.date_entry.insert(0, date.today().isoformat())

        # STATUS

        self.add_label(form, "ATTENDANCE STATUS")

        self.status_dropdown = ctk.CTkOptionMenu(
            form,
            values=["Present", "Absent", "Late", "Half Day"],
            fg_color=TEAL,
            height=40
        )

        self.status_dropdown.pack(
            fill="x", padx=12, pady=(3, 12)
        )

        self.status_dropdown.set("Present")

        # CHECK IN

        self.add_label(form, "CHECK-IN TIME")

        self.checkin_entry = ctk.CTkEntry(
            form,
            height=38,
            placeholder_text="HH:MM (e.g. 09:00)"
        )

        self.checkin_entry.pack(
            fill="x", padx=12, pady=(3, 12)
        )

        # CHECK OUT

        self.add_label(form, "CHECK-OUT TIME")

        self.checkout_entry = ctk.CTkEntry(
            form,
            height=38,
            placeholder_text="HH:MM (e.g. 17:00)"
        )

        self.checkout_entry.pack(
            fill="x", padx=12, pady=(3, 12)
        )

        ctk.CTkLabel(
            form,
            text="Use 24-hour time format.",
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=12, pady=(0, 12))

        # BUTTONS

        buttons = [
            ("SAVE ATTENDANCE", TEAL, self.save_attendance),
            ("UPDATE RECORD", NAVY, self.update_attendance),
            ("DELETE RECORD", RED, self.delete_attendance),
            ("CLEAR FORM", "#E9EEF3", self.clear_form)
        ]

        for label, color, command in buttons:

            ctk.CTkButton(
                form,
                text=label,
                height=39,
                fg_color=color,
                text_color=NAVY if label == "CLEAR FORM" else WHITE,
                hover_color=color,
                command=command
            ).pack(fill="x", padx=12, pady=5)

    # ===================== RIGHT TABLE =====================

    def create_table(self, parent):

        right = ctk.CTkFrame(
            parent,
            fg_color=WHITE,
            corner_radius=12
        )

        right.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # SEARCH TOOLBAR

        toolbar = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=12
        )

        toolbar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            toolbar,
            height=38,
            placeholder_text="Search employee name..."
        )

        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.load_attendance()
        )

        self.filter_date = ctk.CTkEntry(
            toolbar,
            width=125,
            height=38,
            placeholder_text="YYYY-MM-DD"
        )

        self.filter_date.grid(
            row=0,
            column=1,
            padx=5
        )

        ctk.CTkButton(
            toolbar,
            text="SEARCH",
            width=75,
            height=38,
            fg_color=TEAL,
            command=self.load_attendance
        ).grid(row=0, column=2, padx=4)

        ctk.CTkButton(
            toolbar,
            text="RESET",
            width=65,
            height=38,
            fg_color=NAVY,
            command=self.reset_search
        ).grid(row=0, column=3, padx=4)

        # TABLE

        table_frame = ctk.CTkFrame(
            right,
            fg_color=WHITE
        )

        table_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 8)
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            fieldbackground=WHITE,
            rowheight=36,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=NAVY,
            foreground=WHITE,
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", TEAL)],
            foreground=[("selected", WHITE)]
        )

        columns = (
            "id",
            "employee",
            "date",
            "checkin",
            "checkout",
            "hours",
            "status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "employee": "Employee",
            "date": "Date",
            "checkin": "Check In",
            "checkout": "Check Out",
            "hours": "Working Hours",
            "status": "Status"
        }

        widths = {
            "id": 50,
            "employee": 155,
            "date": 105,
            "checkin": 90,
            "checkout": 90,
            "hours": 110,
            "status": 90
        }

        for col in columns:

            self.tree.heading(
                col,
                text=headings[col]
            )

            self.tree.column(
                col,
                width=widths[col],
                minwidth=60
            )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_record
        )

        # BOTTOM REPORT AREA

        bottom = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        bottom.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=10
        )

        self.count_label = ctk.CTkLabel(
            bottom,
            text="Records: 0",
            text_color=MUTED
        )

        self.count_label.pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            bottom,
            text="MONTHLY REPORT",
            width=145,
            height=35,
            fg_color=NAVY,
            command=self.monthly_report
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            bottom,
            text="REFRESH",
            width=85,
            height=35,
            fg_color=TEAL,
            command=self.refresh
        ).pack(side="right", padx=4)

    # ===================== HELPER FUNCTIONS =====================

    def add_label(self, parent, text):

        ctk.CTkLabel(
            parent,
            text=text,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=12,
            pady=(9, 3)
        )

    def format_time(self, value):

        if value is None:
            return ""

        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes = remainder // 60
            return f"{hours:02d}:{minutes:02d}"

        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")

        return str(value)[:5]

    def calculate_hours(self, checkin, checkout):

        if not checkin or not checkout:
            return "-"

        try:
            start = datetime.strptime(
                self.format_time(checkin),
                "%H:%M"
            )

            end = datetime.strptime(
                self.format_time(checkout),
                "%H:%M"
            )

            minutes = int((end - start).total_seconds() / 60)

            if minutes < 0:
                return "-"

            hours, remaining = divmod(minutes, 60)

            return f"{hours}h {remaining}m"

        except (ValueError, TypeError):
            return "-"

    def validate_time(self, value, label):

        if not value:
            return None

        try:
            datetime.strptime(value, "%H:%M")
            return value

        except ValueError:
            raise ValueError(
                f"{label} must use HH:MM format, for example 09:30."
            )

    # ===================== LOAD EMPLOYEES =====================

    def load_employees(self):

        conn = cursor = None

        try:

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT employee_id, employee_name
                FROM employees
                WHERE employment_status = 'Active'
                ORDER BY employee_name
            """)

            rows = cursor.fetchall()

            self.employee_map.clear()

            options = ["Select employee"]

            for employee_id, employee_name in rows:

                display = f"{employee_id} - {employee_name}"

                self.employee_map[display] = employee_id

                options.append(display)

            self.employee_dropdown.configure(
                values=options
            )

            self.employee_dropdown.set(
                "Select employee"
            )

        except Exception as error:

            messagebox.showerror(
                "Employee Loading Error",
                str(error)
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ===================== GET FORM DATA =====================

    def get_form_data(self):

        employee_display = self.employee_dropdown.get()

        if employee_display not in self.employee_map:
            raise ValueError("Please select an employee.")

        employee_id = self.employee_map[employee_display]

        attendance_date = self.date_entry.get().strip()

        try:
            datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            )

        except ValueError:
            raise ValueError(
                "Date must be in YYYY-MM-DD format."
            )

        status = self.status_dropdown.get()

        allowed_status = [
            "Present",
            "Absent",
            "Late",
            "Half Day"
        ]

        if status not in allowed_status:
            raise ValueError("Invalid attendance status.")

        checkin = self.validate_time(
            self.checkin_entry.get().strip(),
            "Check-in time"
        )

        checkout = self.validate_time(
            self.checkout_entry.get().strip(),
            "Check-out time"
        )

        if checkout and not checkin:
            raise ValueError(
                "Enter check-in time before check-out time."
            )

        if checkin and checkout:

            start = datetime.strptime(checkin, "%H:%M")
            end = datetime.strptime(checkout, "%H:%M")

            if end <= start:
                raise ValueError(
                    "Check-out time must be later than check-in time."
                )

        if status == "Absent" and (checkin or checkout):
            raise ValueError(
                "Absent employees should not have check-in or check-out times."
            )

        return (
            employee_id,
            attendance_date,
            checkin,
            checkout,
            status
        )

    # ===================== SAVE ATTENDANCE =====================

    def save_attendance(self):

        conn = cursor = None

        try:

            data = self.get_form_data()

            employee_id, attendance_date, checkin, checkout, status = data

            conn = self.get_connection()
            cursor = conn.cursor()

            # Check duplicate employee attendance on same date

            cursor.execute("""
                SELECT attendance_id
                FROM attendance
                WHERE employee_id = %s
                AND attendance_date = %s
            """, (employee_id, attendance_date))

            existing = cursor.fetchone()

            if existing:

                messagebox.showwarning(
                    "Duplicate Attendance",
                    "Attendance already exists for this employee on this date.\n\nUse UPDATE RECORD to modify it."
                )

                return

            cursor.execute("""
                INSERT INTO attendance (
                    employee_id,
                    attendance_date,
                    check_in,
                    check_out,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                employee_id,
                attendance_date,
                checkin,
                checkout,
                status
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Attendance saved successfully!"
            )

            self.clear_form()
            self.load_attendance()

        except Exception as error:

            if conn:
                conn.rollback()

            messagebox.showerror(
                "Save Attendance Error",
                str(error)
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ===================== SELECT RECORD =====================

    def select_record(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        self.selected_attendance_id = values[0]

        employee_display = values[1]

        for display in self.employee_map:

            if display.endswith(" - " + employee_display):
                self.employee_dropdown.set(display)
                break

        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, values[2])

        self.checkin_entry.delete(0, "end")
        self.checkin_entry.insert(0, values[3])

        self.checkout_entry.delete(0, "end")
        self.checkout_entry.insert(0, values[4])

        self.status_dropdown.set(values[6])

    # ===================== UPDATE ATTENDANCE =====================

    def update_attendance(self):

        if not self.selected_attendance_id:

            messagebox.showwarning(
                "Select Record",
                "Select an attendance record from the table first."
            )

            return

        conn = cursor = None

        try:

            data = self.get_form_data()

            employee_id, attendance_date, checkin, checkout, status = data

            conn = self.get_connection()
            cursor = conn.cursor()

            # Avoid violating unique employee/date constraint

            cursor.execute("""
                SELECT attendance_id
                FROM attendance
                WHERE employee_id = %s
                AND attendance_date = %s
                AND attendance_id != %s
            """, (
                employee_id,
                attendance_date,
                self.selected_attendance_id
            ))

            duplicate = cursor.fetchone()

            if duplicate:

                raise ValueError(
                    "Another attendance record already exists for this employee on this date."
                )

            cursor.execute("""
                UPDATE attendance
                SET employee_id = %s,
                    attendance_date = %s,
                    check_in = %s,
                    check_out = %s,
                    status = %s
                WHERE attendance_id = %s
            """, (
                employee_id,
                attendance_date,
                checkin,
                checkout,
                status,
                self.selected_attendance_id
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Attendance updated successfully!"
            )

            self.clear_form()
            self.load_attendance()

        except Exception as error:

            if conn:
                conn.rollback()

            messagebox.showerror(
                "Update Error",
                str(error)
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ===================== DELETE ATTENDANCE =====================

    def delete_attendance(self):

        if not self.selected_attendance_id:

            messagebox.showwarning(
                "Select Record",
                "Select an attendance record first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this attendance record?"
        )

        if not confirm:
            return

        conn = cursor = None

        try:

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM attendance
                WHERE attendance_id = %s
            """, (self.selected_attendance_id,))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Attendance record deleted successfully."
            )

            self.clear_form()
            self.load_attendance()

        except Exception as error:

            if conn:
                conn.rollback()

            messagebox.showerror(
                "Delete Error",
                str(error)
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ===================== LOAD ATTENDANCE HISTORY =====================

    def load_attendance(self):

        conn = cursor = None

        try:

            conn = self.get_connection()
            cursor = conn.cursor()

            search = self.search_entry.get().strip()
            filter_date = self.filter_date.get().strip()

            sql = """
                SELECT
                    a.attendance_id,
                    e.employee_id,
                    e.employee_name,
                    a.attendance_date,
                    a.check_in,
                    a.check_out,
                    a.status
                FROM attendance a
                INNER JOIN employees e
                    ON a.employee_id = e.employee_id
                WHERE 1=1
            """

            params = []

            if search:

                sql += """
                    AND (
                        e.employee_name LIKE %s
                        OR e.email LIKE %s
                    )
                """

                term = f"%{search}%"

                params.extend([term, term])

            if filter_date:

                try:
                    datetime.strptime(filter_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        "Filter date must be YYYY-MM-DD."
                    )

                sql += " AND a.attendance_date = %s"
                params.append(filter_date)

            sql += " ORDER BY a.attendance_date DESC, a.attendance_id DESC"

            cursor.execute(sql, tuple(params))

            rows = cursor.fetchall()

            self.tree.delete(
                *self.tree.get_children()
            )

            for row in rows:

                (
                    attendance_id,
                    employee_id,
                    employee_name,
                    attendance_date,
                    checkin,
                    checkout,
                    status
                ) = row

                checkin_text = self.format_time(checkin)
                checkout_text = self.format_time(checkout)

                working_hours = self.calculate_hours(
                    checkin,
                    checkout
                )

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        attendance_id,
                        employee_name,
                        attendance_date,
                        checkin_text,
                        checkout_text,
                        working_hours,
                        status
                    )
                )

            self.count_label.configure(
                text=f"Total records: {len(rows)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Attendance Loading Error",
                str(error)
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ===================== MONTHLY REPORT =====================

    def monthly_report(self):

        month_window = ctk.CTkToplevel(self)

        month_window.title("Monthly Attendance Report")
        month_window.geometry("390x270")
        month_window.resizable(False, False)

        month_window.transient(self.winfo_toplevel())
        month_window.grab_set()

        ctk.CTkLabel(
            month_window,
            text="Monthly Attendance Report",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            month_window,
            text="Enter month (YYYY-MM)",
            text_color=MUTED
        ).pack(pady=5)

        month_entry = ctk.CTkEntry(
            month_window,
            width=220,
            height=38,
            placeholder_text="2026-11"
        )

        month_entry.pack(pady=8)

        month_entry.insert(
            0,
            date.today().strftime("%Y-%m")
        )

        def generate_report():

            conn = cursor = None

            try:

                month_text = month_entry.get().strip()

                month_start = datetime.strptime(
                    month_text,
                    "%Y-%m"
                ).date()

                if month_start.month == 12:
                    next_month = date(
                        month_start.year + 1, 1, 1
                    )
                else:
                    next_month = date(
                        month_start.year,
                        month_start.month + 1,
                        1
                    )

                conn = self.get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        COUNT(*),
                        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN status = 'Half Day' THEN 1 ELSE 0 END),
                        COALESCE(
                            SUM(
                                CASE
                                    WHEN check_in IS NOT NULL
                                    AND check_out IS NOT NULL
                                    AND check_out >= check_in
                                    THEN TIME_TO_SEC(
                                        TIMEDIFF(check_out, check_in)
                                    )
                                    ELSE 0
                                END
                            ), 0
                        )
                    FROM attendance
                    WHERE attendance_date >= %s
                    AND attendance_date < %s
                """, (
                    month_start,
                    next_month
                ))

                result = cursor.fetchone()

                total = result[0] or 0
                present = result[1] or 0
                absent = result[2] or 0
                late = result[3] or 0
                half_day = result[4] or 0
                total_seconds = result[5] or 0

                total_hours = int(total_seconds // 3600)
                remaining_minutes = int(
                    (total_seconds % 3600) // 60
                )

                report = (
                    f"MONTH: {month_text}\n\n"
                    f"Total Records: {total}\n"
                    f"Present: {present}\n"
                    f"Absent: {absent}\n"
                    f"Late: {late}\n"
                    f"Half Day: {half_day}\n\n"
                    f"Total Working Hours: "
                    f"{total_hours}h {remaining_minutes}m"
                )

                messagebox.showinfo(
                    "Monthly Attendance Report",
                    report,
                    parent=month_window
                )

            except ValueError:
                messagebox.showerror(
                    "Invalid Month",
                    "Enter the month in YYYY-MM format.",
                    parent=month_window
                )

            except Exception as error:
                messagebox.showerror(
                    "Report Error",
                    str(error),
                    parent=month_window
                )

            finally:

                if cursor:
                    cursor.close()

                if conn:
                    conn.close()

        ctk.CTkButton(
            month_window,
            text="GENERATE REPORT",
            width=220,
            height=40,
            fg_color=TEAL,
            command=generate_report
        ).pack(pady=18)

    # ===================== CLEAR FORM =====================

    def clear_form(self):

        self.employee_dropdown.set("Select employee")

        self.date_entry.delete(0, "end")
        self.date_entry.insert(
            0,
            date.today().isoformat()
        )

        self.status_dropdown.set("Present")

        self.checkin_entry.delete(0, "end")
        self.checkout_entry.delete(0, "end")

        self.selected_attendance_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # ===================== RESET SEARCH =====================

    def reset_search(self):

        self.search_entry.delete(0, "end")
        self.filter_date.delete(0, "end")

        self.load_attendance()

    # ===================== REFRESH =====================

    def refresh(self):

        self.clear_form()
        self.load_employees()
        self.load_attendance()
