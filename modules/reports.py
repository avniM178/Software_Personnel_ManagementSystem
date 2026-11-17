
import customtkinter as ctk
from tkinter import filedialog, messagebox
from database import create_connection

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from datetime import datetime, date
from decimal import Decimal


NAVY = "#17243A"
TEAL = "#168C89"
BG = "#F3F5F8"
WHITE = "#FFFFFF"
TEXT = "#202C3D"
MUTED = "#8490A0"


class ReportsFrame(ctk.CTkFrame):

    REPORTS = {
        "Employee Details": "employees",
        "Department Details": "departments",
        "Attendance Records": "attendance",
        "Leave Requests": "leave_requests",
        "Salary Records": "salary"
    }

    def __init__(self, master):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.pack(fill="both", expand=True)

        self.columns = []
        self.records = []

        self.create_interface()
        self.load_report()

    def create_interface(self):

        self.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            self,
            text="Reports & Exports",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=TEXT
        )
        heading.grid(
            row=0, column=0, sticky="w",
            padx=20, pady=(15, 5)
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Generate and export personnel reports in PDF and Excel formats.",
            text_color=MUTED
        )
        subtitle.grid(
            row=1, column=0, sticky="w",
            padx=20, pady=(0, 18)
        )

        selection_card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=12
        )
        selection_card.grid(
            row=2, column=0, sticky="ew",
            padx=10, pady=5
        )
        selection_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            selection_card,
            text="Select Report",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT
        ).grid(
            row=0, column=0, padx=18, pady=18
        )

        self.report_menu = ctk.CTkOptionMenu(
            selection_card,
            values=list(self.REPORTS.keys()),
            fg_color=TEAL,
            button_color=NAVY,
            button_hover_color=TEAL,
            command=lambda choice: self.load_report()
        )
        self.report_menu.grid(
            row=0, column=1, sticky="w",
            padx=12, pady=18
        )

        ctk.CTkButton(
            selection_card,
            text="Load Report",
            fg_color=NAVY,
            hover_color=TEAL,
            command=self.load_report
        ).grid(
            row=0, column=2, padx=18, pady=18
        )

        self.count_label = ctk.CTkLabel(
            self,
            text="Records: 0",
            text_color=TEAL,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.count_label.grid(
            row=3, column=0, sticky="w",
            padx=20, pady=(15, 8)
        )

        preview_card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=12
        )
        preview_card.grid(
            row=4, column=0, sticky="nsew",
            padx=10, pady=5
        )
        self.grid_rowconfigure(4, weight=1)

        self.preview = ctk.CTkTextbox(
            preview_card,
            fg_color=WHITE,
            text_color=TEXT,
            font=("Courier", 12),
            wrap="none"
        )
        self.preview.pack(
            fill="both", expand=True,
            padx=12, pady=12
        )

        export_card = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=12
        )
        export_card.grid(
            row=5, column=0, sticky="ew",
            padx=10, pady=12
        )

        ctk.CTkLabel(
            export_card,
            text="Export your report",
            text_color=TEXT,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(
            anchor="w", padx=18, pady=(15, 8)
        )

        buttons = ctk.CTkFrame(
            export_card, fg_color="transparent"
        )
        buttons.pack(
            anchor="w", padx=15, pady=(0, 15)
        )

        ctk.CTkButton(
            buttons,
            text="Export as PDF",
            width=160,
            height=40,
            fg_color="#B83A45",
            hover_color="#922D36",
            command=self.export_pdf
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons,
            text="Export as Excel",
            width=160,
            height=40,
            fg_color="#16804A",
            hover_color="#10663A",
            command=self.export_excel
        ).pack(side="left", padx=5)

    def get_data(self):

        report_name = self.report_menu.get()
        table_name = self.REPORTS[report_name]

        conn = None
        cursor = None

        try:
            conn = create_connection()

            if not conn:
                raise Exception("Could not connect to the database.")

            cursor = conn.cursor()

            # Table names come only from the fixed REPORTS dictionary.
            cursor.execute(f"SELECT * FROM `{table_name}`")

            self.columns = [item[0] for item in cursor.description]
            self.records = cursor.fetchall()

            return True

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load report:\n{error}"
            )
            self.columns = []
            self.records = []
            return False

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def display_value(self, value):

        if value is None:
            return ""

        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d %H:%M:%S") \
                if isinstance(value, datetime) else value.strftime("%Y-%m-%d")

        if isinstance(value, Decimal):
            return str(value)

        return str(value)

    def load_report(self):

        if not self.get_data():
            self.count_label.configure(text="Records: unavailable")
            self.preview.delete("1.0", "end")
            return

        self.count_label.configure(
            text=f"Records: {len(self.records)}"
        )

        self.preview.delete("1.0", "end")

        if not self.records:
            self.preview.insert(
                "end",
                "No records found in this table."
            )
            return

        # Display column names.
        header = " | ".join(str(col) for col in self.columns)
        self.preview.insert("end", header + "\n")
        self.preview.insert("end", "-" * min(len(header), 180) + "\n")

        # Preview at most 100 rows to keep the interface responsive.
        for row in self.records[:100]:
            values = [
                self.display_value(value).replace("\n", " ")
                for value in row
            ]
            self.preview.insert(
                "end",
                " | ".join(values) + "\n"
            )

        if len(self.records) > 100:
            self.preview.insert(
                "end",
                f"\nPreview limited to 100 of {len(self.records)} records."
            )

    def export_pdf(self):

        if not self.get_data():
            return

        if not self.records:
            messagebox.showwarning(
                "No Data",
                "There are no records to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.report_menu.get().replace(' ', '_')}.pdf"
        )

        if not path:
            return

        try:
            document = SimpleDocTemplate(
                path,
                pagesize=landscape(A4),
                rightMargin=25,
                leftMargin=25,
                topMargin=30,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "ReportTitle",
                parent=styles["Title"],
                alignment=TA_CENTER,
                textColor=colors.HexColor(NAVY),
                fontSize=18,
                spaceAfter=8
            )

            subtitle_style = ParagraphStyle(
                "ReportSubtitle",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                textColor=colors.grey,
                fontSize=9,
                spaceAfter=15
            )

            story = [
                Paragraph(
                    "SOFTWARE PERSONNEL MANAGEMENT SYSTEM",
                    title_style
                ),
                Paragraph(
                    self.report_menu.get() + " Report",
                    subtitle_style
                ),
                Paragraph(
                    f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                    subtitle_style
                ),
                Paragraph(
                    f"Total Records: {len(self.records)}",
                    subtitle_style
                ),
                Spacer(1, 10)
            ]

            table_data = [
                [str(col) for col in self.columns]
            ]

            for record in self.records:
                table_data.append([
                    self.display_value(value)[:200]
                    for value in record
                ])

            report_table = Table(
                table_data,
                repeatRows=1
            )

            report_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),
                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BACKGROUND", (0, 1), (-1, -1),
                 colors.HexColor("#F3F5F8")),
                ("GRID", (0, 0), (-1, -1),
                 0.4, colors.HexColor("#D5DCE5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ]))

            story.append(report_table)
            document.build(story)

            messagebox.showinfo(
                "Export Successful",
                f"PDF report saved successfully:\n{path}"
            )

        except Exception as error:
            messagebox.showerror(
                "PDF Export Error",
                str(error)
            )

    def export_excel(self):

        if not self.get_data():
            return

        if not self.records:
            messagebox.showwarning(
                "No Data",
                "There are no records to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Excel Report",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"{self.report_menu.get().replace(' ', '_')}.xlsx"
        )

        if not path:
            return

        try:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "SPMS Report"

            sheet.merge_cells(
                start_row=1,
                start_column=1,
                end_row=1,
                end_column=len(self.columns)
            )

            title_cell = sheet.cell(
                row=1, column=1,
                value="SOFTWARE PERSONNEL MANAGEMENT SYSTEM"
            )
            title_cell.font = Font(
                bold=True, size=16, color="FFFFFF"
            )
            title_cell.fill = PatternFill(
                "solid", fgColor="17243A"
            )
            title_cell.alignment = Alignment(
                horizontal="center"
            )

            sheet.append([
                self.report_menu.get() + " Report"
            ])
            sheet.append([
                "Generated on",
                datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            ])
            sheet.append([
                "Total Records",
                len(self.records)
            ])
            sheet.append([])

            header_row = 6

            for col_index, column in enumerate(
                self.columns, start=1
            ):
                cell = sheet.cell(
                    row=header_row,
                    column=col_index,
                    value=str(column)
                )
                cell.font = Font(
                    bold=True, color="FFFFFF"
                )
                cell.fill = PatternFill(
                    "solid", fgColor="168C89"
                )
                cell.alignment = Alignment(
                    horizontal="center"
                )

            for row_index, record in enumerate(
                self.records, start=header_row + 1
            ):
                for col_index, value in enumerate(
                    record, start=1
                ):
                    if isinstance(value, Decimal):
                        value = float(value)
                    elif isinstance(value, (datetime, date)):
                        value = value.isoformat()

                    cell = sheet.cell(
                        row=row_index,
                        column=col_index,
                        value=value
                    )
                    cell.alignment = Alignment(
                        vertical="center"
                    )

            # Adjust column widths.
            for column_index, column_name in enumerate(
                self.columns, start=1
            ):
                width = len(str(column_name))

                for record in self.records:
                    width = max(
                        width,
                        len(self.display_value(
                            record[column_index - 1]
                        ))
                    )

                sheet.column_dimensions[
                    get_column_letter(column_index)
                ].width = min(max(width + 3, 14), 35)

            sheet.freeze_panes = "A7"
            sheet.auto_filter.ref = (
                f"A{header_row}:"
                f"{get_column_letter(len(self.columns))}"
                f"{header_row + len(self.records)}"
            )

            workbook.save(path)

            messagebox.showinfo(
                "Export Successful",
                f"Excel report saved successfully:\n{path}"
            )

        except Exception as error:
            messagebox.showerror(
                "Excel Export Error",
                str(error)
            )
