
import hashlib
import hmac
import customtkinter as ctk
from tkinter import messagebox
from database import create_connection

NAVY = "#17243A"
TEAL = "#168C89"
TEXT = "#202C3D"
MUTED = "#8490A0"


def verify_password(password, stored_hash):
    """Verify the original SPMS PBKDF2-SHA256 password format."""
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations)
        ).hex()

        return hmac.compare_digest(calculated_hash, expected_hash)

    except (ValueError, TypeError):
        return False


class LoginFrame(ctk.CTkFrame):

    def __init__(self, master, on_login):
        super().__init__(master, fg_color="#F3F5F8", corner_radius=0)

        self.on_login = on_login
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # LEFT PANEL
        left = ctk.CTkFrame(
            self,
            fg_color=NAVY,
            corner_radius=0
        )
        left.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            left,
            text="SPMS",
            text_color="white",
            font=ctk.CTkFont(size=38, weight="bold")
        ).pack(anchor="w", padx=55, pady=(65, 8))

        ctk.CTkLabel(
            left,
            text="PEOPLE MANAGEMENT PLATFORM",
            text_color="#9EADBF",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=58)

        ctk.CTkFrame(
            left,
            fg_color=TEAL,
            width=55,
            height=4
        ).pack(anchor="w", padx=58, pady=(90, 25))

        ctk.CTkLabel(
            left,
            text="Manage people.\nEmpower progress.",
            text_color="white",
            justify="left",
            font=ctk.CTkFont(size=34, weight="bold")
        ).pack(anchor="w", padx=58)

        ctk.CTkLabel(
            left,
            text="A unified workspace for employee records,\n"
                 "attendance, leave and workforce administration.",
            text_color="#C4CFDC",
            justify="left",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=60, pady=(22, 0))

        ctk.CTkLabel(
            left,
            text="EMPLOYEE RECORDS   •   ATTENDANCE   •   ANALYTICS",
            text_color="#9EADBF",
            font=ctk.CTkFont(size=9, weight="bold")
        ).pack(side="bottom", anchor="w", padx=58, pady=35)

        # RIGHT PANEL
        right = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=0
        )
        right.grid(row=0, column=1, sticky="nsew")

        panel = ctk.CTkFrame(
            right,
            fg_color="transparent",
            width=370
        )
        panel.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            panel,
            text="Welcome back",
            text_color=TEXT,
            font=ctk.CTkFont(size=29, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            panel,
            text="Sign in to continue to your SPMS workspace.",
            text_color=MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(6, 28))

        ctk.CTkLabel(
            panel,
            text="USERNAME",
            text_color=TEXT,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w")

        self.username = ctk.CTkEntry(
            panel,
            width=370,
            height=45,
            placeholder_text="Enter your username"
        )
        self.username.pack(pady=(7, 20))

        ctk.CTkLabel(
            panel,
            text="PASSWORD",
            text_color=TEXT,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w")

        self.password = ctk.CTkEntry(
            panel,
            width=370,
            height=45,
            show="•",
            placeholder_text="Enter your password"
        )
        self.password.pack(pady=(7, 10))

        self.show_password = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            panel,
            text="Show password",
            variable=self.show_password,
            command=self.toggle_password,
            text_color=MUTED
        ).pack(anchor="w", pady=(0, 22))

        ctk.CTkButton(
            panel,
            text="SIGN IN   →",
            width=370,
            height=48,
            fg_color=TEAL,
            hover_color="#117471",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.login
        ).pack()

        self.password.bind(
            "<Return>",
            lambda event: self.login()
        )

        ctk.CTkLabel(
            panel,
            text="SECURE ADMINISTRATOR LOGIN",
            text_color=MUTED,
            font=ctk.CTkFont(size=9, weight="bold")
        ).pack(pady=(28, 0))

    def toggle_password(self):
        self.password.configure(
            show="" if self.show_password.get() else "•"
        )

    def login(self):

        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing details",
                "Please enter your username and password."
            )
            return

        conn = None
        cursor = None

        try:
            conn = create_connection()

            if conn is None:
                raise ConnectionError("Unable to connect to MySQL.")

            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT username, password_hash, role
                FROM users
                WHERE username = %s
                LIMIT 1
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user is None:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )
                return

            if not verify_password(
                password,
                user["password_hash"]
            ):
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )
                return

            messagebox.showinfo(
                "Login Successful",
                "Welcome to SPMS!"
            )

            self.on_login({
                "username": user["username"],
                "role": user["role"]
            })

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()
