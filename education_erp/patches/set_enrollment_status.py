import frappe


def execute():
    """Backfill enrollment_status cho dữ liệu cũ sau khi thêm field nghiệp vụ.

    docstatus=1 (đã submit) -> Active; docstatus=0 (draft) -> Pending.
    Cancelled (docstatus=2) giữ nguyên giá trị mặc định.
    """
    if not frappe.db.has_column("Program Enrollment", "enrollment_status"):
        return

    frappe.db.sql(
        """
        UPDATE `tabProgram Enrollment`
        SET enrollment_status = 'Active'
        WHERE docstatus = 1
          AND (enrollment_status IS NULL OR enrollment_status = '' OR enrollment_status = 'Pending')
        """
    )
    frappe.db.sql(
        """
        UPDATE `tabProgram Enrollment`
        SET enrollment_status = 'Pending'
        WHERE docstatus = 0
          AND (enrollment_status IS NULL OR enrollment_status = '')
        """
    )
