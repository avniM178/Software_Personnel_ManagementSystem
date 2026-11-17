import customtkinter as ctk
from modules.login import LoginFrame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def main():
    root = ctk.CTk()
    root.title("SPMS | Software Personnel Management System")
    root.geometry("1250x760")
    root.minsize(1000, 650)
    LoginFrame(root, on_login=lambda user: open_dashboard(root, user))
    root.mainloop()

def open_dashboard(root, user):
    from modules.dashboard import DashboardFrame
    for widget in root.winfo_children():
        widget.destroy()
    DashboardFrame(root, user=user, on_logout=lambda: back_to_login(root))

def back_to_login(root):
    for widget in root.winfo_children():
        widget.destroy()
    LoginFrame(root, on_login=lambda user: open_dashboard(root, user))

if __name__ == "__main__":
    main()
