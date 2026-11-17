from tkinter import messagebox
import customtkinter as ctk
from modules.data_manager import DataManagerFrame
from database import create_connection

NAVY = "#17243A"
TEAL = "#168C89"
BG = "#F3F5F8"
WHITE = "#FFFFFF"
TEXT = "#202C3D"
MUTED = "#8490A0"


class DashboardFrame(ctk.CTkFrame):

    TABLES = {
        "Employees": "employees",
        "Departments": "departments",
        "Attendance": "attendance",
        "Leave Requests": "leave_requests",
        "Salary": "salary",
        "User Accounts": "users",
    }

    def __init__(self, master, user=None, on_logout=None):
        super().__init__(master, fg_color=BG, corner_radius=0)

        self.user = user or {
            "username": "Admin",
            "role": "Admin"
        }

        self.on_logout = on_logout

        role = str(self.user.get("role", "")).strip().lower()

        # Unknown roles receive restricted access.
        if role in ("admin", "administrator"):
            self.allowed_pages = [
                "Overview", "Analytics", *self.TABLES.keys(),
                "Reports", "Leave Approval", "Payslips"
            ]

        elif role in ("hr", "human resources", "hr manager"):
            self.allowed_pages = [
                "Overview", "Analytics", "Employees",
                "Departments", "Attendance", "Leave Requests",
                "Salary", "Reports", "Leave Approval", "Payslips"
            ]

        else:
            self.allowed_pages = ["Overview"]

        self.pack(fill="both", expand=True)
        self.buttons = {}

        self._shell()
        self.show_page("Overview")

    def _shell(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        side = ctk.CTkFrame(
            self, width=230,
            fg_color=NAVY, corner_radius=0
        )
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        ctk.CTkLabel(
            side, text="SPMS",
            text_color=WHITE,
            font=ctk.CTkFont(size=30, weight="bold")
        ).pack(anchor="w", padx=24, pady=(28, 2))

        ctk.CTkLabel(
            side,
            text="PEOPLE MANAGEMENT PLATFORM",
            text_color="#9EADBF",
            font=ctk.CTkFont(size=9, weight="bold")
        ).pack(anchor="w", padx=25, pady=(0, 28))

        for name in self.allowed_pages:

            button = ctk.CTkButton(
                side,
                text=name,
                anchor="w",
                height=41,
                fg_color="transparent",
                hover_color="#263B57",
                text_color="#D2DCE7",
                command=lambda p=name: self.show_page(p)
            )

            button.pack(fill="x", padx=13, pady=3)
            self.buttons[name] = button

        ctk.CTkLabel(
            side,
            text="SOFTWARE PERSONNEL\nMANAGEMENT SYSTEM",
            text_color="#8292A7",
            font=ctk.CTkFont(size=9, weight="bold")
        ).pack(side="bottom", anchor="w", padx=22, pady=24)

        area = ctk.CTkFrame(
            self, fg_color=BG, corner_radius=0
        )
        area.grid(row=0, column=1, sticky="nsew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(
            area, fg_color=WHITE,
            height=62, corner_radius=0
        )
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.heading = ctk.CTkLabel(
            top, text="Overview",
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.heading.grid(
            row=0, column=0,
            sticky="w", padx=24, pady=17
        )

        ctk.CTkLabel(
            top,
            text=f"{self.user.get('username', 'Admin')}  ·  "
                 f"{self.user.get('role', 'Admin')}",
            text_color=MUTED
        ).grid(row=0, column=1, padx=12)

        ctk.CTkButton(
            top,
            text="Sign out",
            width=90,
            height=34,
            fg_color="#E9EEF3",
            hover_color="#DCE4EC",
            text_color=NAVY,
            command=self._logout
        ).grid(row=0, column=2, padx=18)

        self.page = ctk.CTkFrame(
            area, fg_color=BG, corner_radius=0
        )
        self.page.grid(
            row=1, column=0,
            sticky="nsew", padx=22, pady=20
        )
        self.page.grid_columnconfigure(0, weight=1)

    def show_page(self, name):

        if name not in self.allowed_pages:
            messagebox.showerror(
                "Access Denied",
                "You do not have permission to access this page."
            )
            return

        for key, button in self.buttons.items():
            button.configure(
                fg_color=TEAL if key == name else "transparent",
                text_color=WHITE if key == name else "#D2DCE7"
            )

        for widget in self.page.winfo_children():
            widget.destroy()

        self.heading.configure(text=name)

        if name == "Overview":
            self._overview()

        elif name == "Analytics":
            from modules.advanced_features import AnalyticsFrame
            AnalyticsFrame(self.page)

        elif name == "Leave Approval":
            from modules.advanced_features import LeaveApprovalFrame
            LeaveApprovalFrame(self.page, self.user)

        elif name == "Payslips":
            from modules.advanced_features import PayslipFrame
            PayslipFrame(self.page)

        elif name == "Employees":
            from modules.employees import EmployeeManagementFrame
            EmployeeManagementFrame(self.page)

        elif name == "Reports":
            from modules.reports import ReportsFrame
            ReportsFrame(self.page)

        else:
            DataManagerFrame(
                self.page,
                self.TABLES[name],
                name
            )

    def _count(self, table):

        conn = None
        cur = None

        try:
            if table not in self.TABLES.values():
                return "—"

            conn = create_connection()

            if not conn:
                return "—"

            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM `{table}`")
            return cur.fetchone()[0]

        except Exception:
            return "—"

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def _overview(self):

        ctk.CTkLabel(
            self.page,
            text="Welcome to your workspace",
            text_color=TEXT,
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            self.page,
            text="A central view of your personnel operations.",
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w", pady=(0, 20))

        cards = ctk.CTkFrame(
            self.page, fg_color="transparent"
        )
        cards.grid(row=2, column=0, sticky="ew")

        for i, (label, table) in enumerate([
            ("Employees", "employees"),
            ("Departments", "departments"),
            ("Attendance records", "attendance"),
            ("Leave requests", "leave_requests")
        ]):

            cards.grid_columnconfigure(i, weight=1)

            card = ctk.CTkFrame(
                cards, fg_color=WHITE, corner_radius=12
            )
            card.grid(
                row=0, column=i,
                sticky="ew", padx=5
            )

            ctk.CTkLabel(
                card, text=label, text_color=MUTED
            ).pack(anchor="w", padx=15, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=str(self._count(table)),
                text_color=NAVY,
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack(anchor="w", padx=15, pady=(0, 16))

        info = ctk.CTkFrame(
            self.page, fg_color=WHITE, corner_radius=12
        )
        info.grid(row=3, column=0, sticky="ew", pady=20)

        ctk.CTkLabel(
            info,
            text="PERSONNEL OPERATIONS",
            text_color=TEAL,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 5))

        ctk.CTkLabel(
            info,
           text="Welcome to your workspace! Nexora brings people, processes, and technology together to create a smarter and more connected workplace. Stay organized, monitor performance, manage your workforce, and discover new opportunities for growth — all from one central platform. Innovate with purpose. Grow with confidence. Build the future together.",
            text_color=TEXT,
            wraplength=850,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def _logout(self):
        if self.on_logout:
            self.on_logout()
