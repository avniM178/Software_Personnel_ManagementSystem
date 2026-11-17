
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from database import create_connection
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


NAVY = "#17243A"
TEAL = "#168C89"
BG = "#F3F5F8"
WHITE = "#FFFFFF"
TEXT = "#202C3D"
MUTED = "#8490A0"


# --------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------

def get_table_data(table):
    """Return table columns, records and primary key."""

    allowed = {
        "employees", "departments", "attendance",
        "leave_requests", "salary", "users"
    }

    if table not in allowed:
        raise ValueError("Invalid table.")

    conn = create_connection()

    if not conn:
        raise Exception("Database connection failed.")

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        metadata = cursor.fetchall()

        columns = [row["Field"] for row in metadata]
        primary_key = next(
            (row["Field"] for row in metadata if row["Key"] == "PRI"),
            None
        )

        cursor.execute(f"SELECT * FROM `{table}`")
        records = cursor.fetchall()

        return columns, records, primary_key, metadata

    finally:
        cursor.close()
        conn.close()


def get_value(row, candidates):
    """Find the first matching column in a database row."""

    for candidate in candidates:
        for key in row:
            if key.lower() == candidate.lower():
                return row[key]

    return None


# --------------------------------------------------
# DASHBOARD ANALYTICS
# --------------------------------------------------

class AnalyticsFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=BG)
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=1)
        self.create_interface()

    def count(self, table):
        try:
            _, records, _, _ = get_table_data(table)
            return len(records)
        except Exception:
            return None

    def create_interface(self):

        ctk.CTkLabel(
            self,
            text="Workforce Analytics",
            text_color=TEXT,
            font=ctk.CTkFont(size=25, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(5, 18))

        stats = [
            ("Employees", "employees"),
            ("Departments", "departments"),
            ("Attendance", "attendance"),
            ("Leave Requests", "leave_requests")
        ]

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew")

        for i, (label, table) in enumerate(stats):

            cards.grid_columnconfigure(i, weight=1)

            value = self.count(table)

            card = ctk.CTkFrame(
                cards, fg_color=WHITE, corner_radius=12
            )
            card.grid(
                row=0, column=i, sticky="ew", padx=5
            )

            ctk.CTkLabel(
                card, text=label, text_color=MUTED
            ).pack(anchor="w", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                card,
                text="—" if value is None else str(value),
                text_color=NAVY,
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack(anchor="w", padx=15, pady=(0, 15))

        chart_card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=12
        )
        chart_card.grid(
            row=2, column=0, sticky="ew", pady=20
        )

        ctk.CTkLabel(
            chart_card,
            text="PERSONNEL OVERVIEW",
            text_color=TEAL,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=18, pady=15)

        chart = ctk.CTkCanvas(
            chart_card,
            height=220,
            bg=WHITE,
            highlightthickness=0
        )
        chart.pack(fill="x", padx=15, pady=(0, 15))

        values = [
            self.count("employees"),
            self.count("departments"),
            self.count("attendance"),
            self.count("leave_requests")
        ]

        labels = [
            "Employees", "Departments",
            "Attendance", "Leave Requests"
        ]

        valid_values = [v for v in values if v is not None]
        maximum = max(valid_values, default=0)

        for i, (label, value) in enumerate(zip(labels, values)):

            x = 100 + i * 190
            chart.create_text(
                x, 195, text=label,
                fill=TEXT, font=("Arial", 9)
            )

            if value is None:
                chart.create_text(
                    x, 95, text="N/A",
                    fill=MUTED
                )
                continue

            height = 130 * value / maximum if maximum else 0

            chart.create_rectangle(
                x - 35, 170 - height,
                x + 35, 170,
                fill=TEAL,
                outline=""
            )

            chart.create_text(
                x, 155 - height,
                text=str(value),
                fill=NAVY,
                font=("Arial", 11, "bold")
            )

        ctk.CTkButton(
            self,
            text="Refresh Analytics",
            fg_color=NAVY,
            hover_color=TEAL,
            command=lambda: self.refresh(master=self.master)
        ).grid(row=3, column=0, sticky="w", pady=5)

    def refresh(self, master=None):
        parent = self.master
        for widget in parent.winfo_children():
            widget.destroy()
        AnalyticsFrame(parent)


# --------------------------------------------------
# LEAVE APPROVAL
# --------------------------------------------------

class LeaveApprovalFrame(ctk.CTkFrame):

    STATUS_CANDIDATES = [
        "status", "leave_status",
        "approval_status", "request_status"
    ]

    def __init__(self, master, user=None):
        super().__init__(master, fg_color=BG)
        self.pack(fill="both", expand=True)

        self.user = user or {}
        self.records = []
        self.columns = []
        self.primary_key = None
        self.status_column = None

        self.create_interface()
        self.load_requests()

    def create_interface(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self,
            text="Leave Approval Management",
            text_color=TEXT,
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(5, 8))

        ctk.CTkLabel(
            self,
            text="Review employee leave requests and update their status.",
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.tree = ttk.Treeview(self, show="headings")

        self.tree.grid(
            row=2, column=0, sticky="nsew", pady=5
        )

        scrollbar = ttk.Scrollbar(
            self, orient="vertical",
            command=self.tree.yview
        )
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        buttons = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        buttons.grid(row=3, column=0, sticky="w", pady=15)

        ctk.CTkButton(
            buttons,
            text="Approve",
            fg_color="#16804A",
            hover_color="#10663A",
            command=lambda: self.update_status("approve")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons,
            text="Reject",
            fg_color="#B83A45",
            hover_color="#922D36",
            command=lambda: self.update_status("reject")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons,
            text="Refresh",
            fg_color=NAVY,
            hover_color=TEAL,
            command=self.load_requests
        ).pack(side="left", padx=5)

    def load_requests(self):

        try:
            (
                self.columns,
                self.records,
                self.primary_key,
                metadata
            ) = get_table_data("leave_requests")

            self.status_column = next(
                (
                    col for col in self.columns
                    if col.lower() in self.STATUS_CANDIDATES
                ),
                None
            )

            self.tree.delete(*self.tree.get_children())

            self.tree["columns"] = self.columns

            for column in self.columns:
                self.tree.heading(column, text=column)
                self.tree.column(
                    column, width=130, minwidth=80
                )

            for row in self.records:
                self.tree.insert(
                    "",
                    "end",
                    iid=str(row[self.primary_key])
                    if self.primary_key else None,
                    values=[
                        str(row.get(col, ""))
                        for col in self.columns
                    ]
                )

            if not self.status_column:
                messagebox.showwarning(
                    "Status Column Not Found",
                    "The leave_requests table has no recognized "
                    "status column. Approval cannot be performed "
                    "until its status column is identified."
                )

            if not self.primary_key:
                messagebox.showwarning(
                    "Primary Key Not Found",
                    "The leave_requests table needs a primary key "
                    "to update individual requests safely."
                )

        except Exception as error:
            messagebox.showerror(
                "Leave Error", str(error)
            )

    def update_status(self, action):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Request",
                "Please select a leave request first."
            )
            return

        if not self.status_column or not self.primary_key:
            messagebox.showerror(
                "Cannot Update",
                "A status column and primary key are required."
            )
            return

        row = next(
            (
                item for item in self.records
                if str(item[self.primary_key]) == str(selected[0])
            ),
            None
        )

        if not row:
            return

        metadata = None

        try:
            _, _, _, metadata = get_table_data("leave_requests")
        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            return

        status_info = next(
            (
                item for item in metadata
                if item["Field"] == self.status_column
            ),
            {}
        )

        column_type = status_info.get("Type", "").lower()

        # Support common enum status values where possible.
        enum_values = []
        if column_type.startswith("enum("):
            enum_values = [
                value.strip("'")
                for value in column_type[5:-1].split(",")
            ]

        if action == "approve":
            preferred = ["Approved", "Accepted", "Granted"]
        else:
            preferred = ["Rejected", "Declined", "Denied"]

        new_status = next(
            (
                value for value in enum_values
                if value.lower() in [x.lower() for x in preferred]
            ),
            preferred[0]
        )

        request_id = row[self.primary_key]

        if not messagebox.askyesno(
            "Confirm Decision",
            f"Are you sure you want to set this request to "
            f"{new_status}?"
        ):
            return

        conn = None
        cursor = None

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute(
                f"UPDATE `leave_requests` "
                f"SET `{self.status_column}` = %s "
                f"WHERE `{self.primary_key}` = %s",
                (new_status, request_id)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                f"Leave request {new_status.lower()} successfully."
            )

            self.load_requests()

        except Exception as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Update Error", str(error)
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# --------------------------------------------------
# SALARY PAYSLIP GENERATION
# --------------------------------------------------

class PayslipFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=BG)
        self.pack(fill="both", expand=True)

        self.columns = []
        self.records = []
        self.primary_key = None

        self.create_interface()
        self.load_salary()

    def create_interface(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self,
            text="Salary & Payslip Generation",
            text_color=TEXT,
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(5, 8))

        ctk.CTkLabel(
            self,
            text="Select a salary record and generate its PDF payslip.",
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=2, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            self, orient="vertical",
            command=self.tree.yview
        )
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        buttons = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        buttons.grid(row=3, column=0, sticky="w", pady=15)

        ctk.CTkButton(
            buttons,
            text="Generate PDF Payslip",
            fg_color=TEAL,
            hover_color=NAVY,
            command=self.generate_payslip
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons,
            text="Refresh",
            fg_color=NAVY,
            hover_color=TEAL,
            command=self.load_salary
        ).pack(side="left", padx=5)

    def load_salary(self):

        try:
            (
                self.columns,
                self.records,
                self.primary_key,
                _
            ) = get_table_data("salary")

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = self.columns

            for column in self.columns:
                self.tree.heading(column, text=column)
                self.tree.column(
                    column, width=140, minwidth=80
                )

            for row in self.records:
                self.tree.insert(
                    "",
                    "end",
                    iid=str(row[self.primary_key])
                    if self.primary_key else None,
                    values=[
                        str(row.get(col, ""))
                        for col in self.columns
                    ]
                )

        except Exception as error:
            messagebox.showerror(
                "Salary Error", str(error)
            )

    def generate_payslip(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Salary",
                "Please select a salary record."
            )
            return

        if not self.primary_key:
            messagebox.showerror(
                "Missing Primary Key",
                "The salary table needs a primary key "
                "to identify a selected salary record."
            )
            return

        record = next(
            (
                row for row in self.records
                if str(row[self.primary_key]) == str(selected[0])
            ),
            None
        )

        if not record:
            return

        employee_name = get_value(
            record,
            ["employee_name", "name"]
        ) or "Employee"

        path = filedialog.asksaveasfilename(
            title="Save Employee Payslip",
            defaultextension=".pdf",
            initialfile=f"Payslip_{employee_name}.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not path:
            return

        try:
            document = SimpleDocTemplate(
                path,
                pagesize=A4
            )

            styles = getSampleStyleSheet()

            story = [
                Paragraph(
                    "SOFTWARE PERSONNEL MANAGEMENT SYSTEM",
                    styles["Title"]
                ),
                Paragraph(
                    "EMPLOYEE SALARY PAYSLIP",
                    styles["Heading2"]
                ),
                Spacer(1, 20)
            ]

            data = [
                ["Salary Information", "Value"]
            ]

            for column in self.columns:
                value = record.get(column)

                if isinstance(value, Decimal):
                    value = str(value)
                elif hasattr(value, "isoformat"):
                    value = value.isoformat()

                data.append([
                    str(column).replace("_", " ").title(),
                    "" if value is None else str(value)
                ])

            table = Table(
                data,
                colWidths=[190, 300]
            )

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),
                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1),
                 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1),
                 colors.HexColor("#F3F5F8")),
                ("PADDING", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
            ]))

            story.append(table)
            story.append(Spacer(1, 25))
            story.append(Paragraph(
                f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                styles["Normal"]
            ))

            document.build(story)

            messagebox.showinfo(
                "Payslip Generated",
                f"Payslip saved successfully:\n{path}"
            )

        except Exception as error:
            messagebox.showerror(
                "Payslip Error", str(error)
            )
