"""
Export service — converts a list of row-dicts into downloadable file
bytes (CSV or XLSX).

Why this is its own file, separate from attendance_service:
    "Turn data into a CSV/XLSX" is a generic, reusable capability, not
    an attendance business rule. Keeping it separate means if another
    export was ever needed (e.g. exporting the employee list), this
    file could be reused as-is — it knows nothing about attendance
    specifically, only "rows + column headers in, file bytes out."
"""

import csv
import io

from openpyxl import Workbook

# Column order/labels shared by both CSV and XLSX output, so the two
# formats are guaranteed to match each other exactly.
EXPORT_COLUMNS = [
    ("employee_code", "Employee Code"),
    ("employee_name", "Employee Name"),
    ("attendance_date", "Date"),
    ("check_in", "Check-In"),
    ("check_out", "Check-Out"),
    ("status", "Status"),
]


def to_csv_bytes(rows: list[dict]) -> bytes:
    """Build a CSV file in memory and return its raw bytes."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([label for _, label in EXPORT_COLUMNS])
    for row in rows:
        writer.writerow([row.get(key, "") for key, _ in EXPORT_COLUMNS])

    # csv.writer works with str, but Response bodies need bytes —
    # encode with utf-8-sig so Excel opens the CSV without mangling
    # special characters (the BOM signals "this is UTF-8" to Excel).
    return buffer.getvalue().encode("utf-8-sig")


def to_xlsx_bytes(rows: list[dict]) -> bytes:
    """Build an .xlsx workbook in memory and return its raw bytes."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"

    sheet.append([label for _, label in EXPORT_COLUMNS])
    for row in rows:
        sheet.append([row.get(key, "") for key, _ in EXPORT_COLUMNS])

    # Reasonable column widths so the file is readable without the
    # user manually resizing every column on open.
    for i, (_, label) in enumerate(EXPORT_COLUMNS, start=1):
        sheet.column_dimensions[chr(64 + i)].width = max(len(label) + 4, 14)

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()