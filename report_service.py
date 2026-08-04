"""
Report generation engine to create styled Excel summaries.
"""

import io
import pandas as pd


class ReportService:

    @staticmethod
    def generate_excel_report(df: pd.DataFrame) -> bytes:
        """
        Generates a formatted downloadable binary Excel report.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Báo_Cáo_OGSM", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Báo_Cáo_OGSM"]

            # Add simple corporate header format
            header_format = workbook.add_format({
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#003366",
                "font_color": "#FFFFFF",
                "border": 1
            })

            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_format)
                worksheet.set_column(col_num, col_num, 18)

        output.seek(0)
        return output.read()
