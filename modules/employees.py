
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import create_connection
import re

NAVY = "#17243A"
TEAL = "#168C89"
BG = "#F3F5F8"
WHITE = "#FFFFFF"
TEXT = "#202C3D"
MUTED = "#8490A0"


class EmployeeManagementFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=BG, corner_radius=0)

        self.pack(fill="both", expand=True)
        self.selected_id = None

        self.create_interface()
        self.load_employees()

    def create_interface(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # HEADER
        ctk.CTkLabel(
            self,
            text="Employee Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w", pady=(5, 4))

        ctk.CTkLabel(
            self,
            text="Manage employee information and personnel records.",
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(0, 18))

        # MAIN CONTENT
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=2, column=0, sticky="nsew")

        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # EMPLOYEE FORM
        form = ctk.CTkScrollableFrame(
            main,
            width=270,
            fg_color=WHITE,
            corner_radius=12
        )
        form.grid(row=0, column=0, sticky="ns", padx=(0, 15))

        ctk.CTkLabel(
            form,
            text="Employee Details",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=12, pady=15)

        self.fields = {}

        field_names = [
            ("employee_name", "Employee Name"),
            ("email", "Email Address"),
            ("phone", "Phone Number"),
            ("gender", "Gender"),
            ("designation", "Designation"),
            ("department_id", "Department ID"),
            ("joining_date", "Joining Date (YYYY-MM-DD)")
        ]

        for key, label in field_names:

            ctk.CTkLabel(
                form,
                text=label.upper(),
                text_color=TEXT,
                font=ctk.CTkFont(size=10, weight="bold")
            ).pack(anchor="w", padx=12, pady=(9, 3))

            if key == "gender":

                widget = ctk.CTkOptionMenu(
                    form,
                    values=["Male", "Female", "Other"],
                    fg_color=TEAL
                )

            else:

                widget = ctk.CTkEntry(
                    form,
                    height=36,
                    placeholder_text=f"Enter {label}"
                )

            widget.pack(fill="x", padx=12)

            self.fields[key] = widget

        ctk.CTkLabel(
            form,
            text="EMPLOYMENT STATUS",
            text_color=TEXT,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=12, pady=(12, 3))

        self.status = ctk.CTkOptionMenu(
            form,
            values=["Active", "Inactive"],
            fg_color=TEAL
        )
        self.status.pack(fill="x", padx=12)

        # BUTTONS
        ctk.CTkButton(
            form,
            text="ADD EMPLOYEE",
            fg_color=TEAL,
            hover_color="#117471",
            command=self.add_employee
        ).pack(fill="x", padx=12, pady=(20, 5))

        ctk.CTkButton(
            form,
            text="UPDATE EMPLOYEE",
            fg_color=NAVY,
            hover_color="#263B57",
            command=self.update_employee
        ).pack(fill="x", padx=12, pady=5)

        ctk.CTkButton(
            form,
            text="DEACTIVATE EMPLOYEE",
            fg_color="#B94B55",
            hover_color="#963A43",
            command=self.deactivate_employee
        ).pack(fill="x", padx=12, pady=5)

        ctk.CTkButton(
            form,
            text="CLEAR FORM",
            fg_color="#E9EEF3",
            text_color=NAVY,
            hover_color="#DCE4EC",
            command=self.clear_form
        ).pack(fill="x", padx=12, pady=(5, 15))

        # EMPLOYEE TABLE
        right = ctk.CTkFrame(
            main,
            fg_color=WHITE,
            corner_radius=12
        )
        right.grid(row=0, column=1, sticky="nsew")

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

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
            placeholder_text="Search employee name, email or designation...",
            height=38
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.load_employees()
        )

        ctk.CTkButton(
            toolbar,
            text="SEARCH",
            width=85,
            fg_color=TEAL,
            command=self.load_employees
        ).grid(row=0, column=1, padx=3)

        ctk.CTkButton(
            toolbar,
            text="REFRESH",
            width=85,
            fg_color=NAVY,
            command=self.refresh
        ).grid(row=0, column=2, padx=3)

        # TREEVIEW
        table_frame = ctk.CTkFrame(
            right,
            fg_color=WHITE
        )
        table_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground=TEXT,
            rowheight=35,
            fieldbackground="white",
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=NAVY,
            foreground="white",
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", TEAL)],
            foreground=[("selected", "white")]
        )

        columns = (
            "employee_id",
            "employee_name",
            "email",
            "phone",
            "designation",
            "department_id",
            "joining_date",
            "employment_status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = [
            "ID", "Employee Name", "Email", "Phone",
            "Designation", "Department", "Joining Date", "Status"
        ]

        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=125, minwidth=85)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_employee
        )

        self.count_label = ctk.CTkLabel(
            right,
            text="",
            text_color=MUTED
        )
        self.count_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 10)
        )

    # DATABASE CONNECTION

    def get_connection(self):
        conn = create_connection()

        if conn is None:
            raise ConnectionError("MySQL connection failed.")

        return conn

    # VALIDATION

    def collect_data(self):

        data = {}

        for key, widget in self.fields.items():
            data[key] = widget.get().strip()

        data["employment_status"] = self.status.get()

        if not data["employee_name"]:
            raise ValueError("Employee name is required.")

        if not data["email"]:
            raise ValueError("Email address is required.")

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            data["email"]
        ):
            raise ValueError("Enter a valid email address.")

        if not data["phone"]:
            data["phone"] = None
        elif not re.fullmatch(r"[0-9+ -]{7,15}", data["phone"]):
            raise ValueError("Enter a valid phone number.")

        if data["department_id"]:
            try:
                data["department_id"] = int(data["department_id"])
            except ValueError:
                raise ValueError("Department ID must be a number.")
        else:
            data["department_id"] = None

        if data["joining_date"]:
            try:
                from datetime import date
                date.fromisoformat(data["joining_date"])
            except ValueError:
                raise ValueError("Date must be YYYY-MM-DD.")
        else:
            data["joining_date"] = None

        for key in ["gender", "designation"]:
            if not data[key]:
                data[key] = None

        return data

    # LOAD EMPLOYEES

    def load_employees(self):

        conn = cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            search = self.search_entry.get().strip()

            sql = """
                SELECT employee_id, employee_name, email,
                       phone, designation, department_id,
                       joining_date, employment_status
                FROM employees
            """

            params = ()

            if search:
                sql += """
                    WHERE employee_name LIKE %s
                    OR email LIKE %s
                    OR designation LIKE %s
                """
                term = f"%{search}%"
                params = (term, term, term)

            sql += " ORDER BY employee_id DESC"

            cursor.execute(sql, params)

            rows = cursor.fetchall()

            self.tree.delete(*self.tree.get_children())

            for row in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=[
                        "" if value is None else str(value)
                        for value in row
                    ]
                )

            self.count_label.configure(
                text=f"Total employees displayed: {len(rows)}"
            )

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ADD EMPLOYEE

    def add_employee(self):

        conn = cursor = None

        try:
            data = self.collect_data()

            conn = self.get_connection()
            cursor = conn.cursor()

            sql = """
                INSERT INTO employees
                (
                    employee_name, email, phone, gender,
                    designation, department_id, joining_date,
                    employment_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                data["employee_name"],
                data["email"],
                data["phone"],
                data["gender"],
                data["designation"],
                data["department_id"],
                data["joining_date"],
                data["employment_status"]
            )

            cursor.execute(sql, values)
            conn.commit()

            messagebox.showinfo(
                "Success",
                "Employee added successfully!"
            )

            self.clear_form()
            self.load_employees()

        except Exception as error:
            if conn:
                conn.rollback()

            messagebox.showerror("Error", str(error))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # SELECT EMPLOYEE

    def select_employee(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        self.selected_id = values[0]

        mapping = {
            "employee_name": values[1],
            "email": values[2],
            "phone": values[3],
            "designation": values[4],
            "department_id": values[5],
            "joining_date": values[6]
        }

        for key, value in mapping.items():

            widget = self.fields[key]

            widget.delete(0, "end")
            widget.insert(0, value)

        # Gender is not displayed in the table.
        # Fetch it from the database.

        conn = cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT gender FROM employees WHERE employee_id=%s",
                (self.selected_id,)
            )

            result = cursor.fetchone()

            if result and result[0]:
                self.fields["gender"].set(result[0])

            self.status.set(values[7] or "Active")

        except Exception as error:
            messagebox.showerror("Error", str(error))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # UPDATE EMPLOYEE

    def update_employee(self):

        if not self.selected_id:
            messagebox.showwarning(
                "Select Employee",
                "Select an employee from the table first."
            )
            return

        conn = cursor = None

        try:
            data = self.collect_data()

            conn = self.get_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE employees
                SET employee_name=%s,
                    email=%s,
                    phone=%s,
                    gender=%s,
                    designation=%s,
                    department_id=%s,
                    joining_date=%s,
                    employment_status=%s
                WHERE employee_id=%s
            """

            values = (
                data["employee_name"],
                data["email"],
                data["phone"],
                data["gender"],
                data["designation"],
                data["department_id"],
                data["joining_date"],
                data["employment_status"],
                self.selected_id
            )

            cursor.execute(sql, values)
            conn.commit()

            messagebox.showinfo(
                "Updated",
                "Employee information updated successfully."
            )

            self.clear_form()
            self.load_employees()

        except Exception as error:
            if conn:
                conn.rollback()

            messagebox.showerror("Update Error", str(error))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # DEACTIVATE EMPLOYEE

    def deactivate_employee(self):

        if not self.selected_id:
            messagebox.showwarning(
                "Select Employee",
                "Select an employee first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivation",
            "Are you sure you want to deactivate this employee?"
        )

        if not confirm:
            return

        conn = cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE employees
                SET employment_status='Inactive'
                WHERE employee_id=%s
                """,
                (self.selected_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Employee deactivated successfully."
            )

            self.clear_form()
            self.load_employees()

        except Exception as error:
            if conn:
                conn.rollback()

            messagebox.showerror("Error", str(error))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # CLEAR FORM

    def clear_form(self):

        for key, widget in self.fields.items():

            if isinstance(widget, ctk.CTkOptionMenu):

                if key == "gender":
                    widget.set("Male")

            else:
                widget.delete(0, "end")

        self.status.set("Active")
        self.selected_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # REFRESH

    def refresh(self):

        self.search_entry.delete(0, "end")
        self.clear_form()
        self.load_employees()
