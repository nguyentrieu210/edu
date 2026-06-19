import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class FeeSchedule(Document):
    # Type Annotations for v15+
    student: str
    program_enrollment: str | None
    total_amount: float
    due_date: str
    status: str

    def validate(self) -> None:
        if self.due_date and getdate(self.due_date) < getdate(nowdate()):
            frappe.throw("Due Date cannot be less than the current date.")

    def on_submit(self) -> None:
        if self.status == "Draft":
            self.status = "Invoice Pending"

        if self.status == "Invoice Pending":
            self.make_invoice()

    def make_invoice(self) -> str:
        """Create & submit a Fee Invoice for this schedule and mark it Invoiced.

        Reused by on_submit and by the regenerate_invoice API (after a previous
        invoice was cancelled), so the schedule never gets stuck in
        'Invoice Pending'.
        """
        invoice = frappe.get_doc({
            "doctype": "Fee Invoice",
            "student": self.student,
            "program_enrollment": self.program_enrollment,
            "fee_schedule": self.name,
            "posting_date": nowdate(),
            "due_date": self.due_date,
            "total_amount": self.total_amount,
            "status": "Unpaid"
        })
        invoice.insert()
        invoice.submit()
        self.db_set("status", "Invoiced")
        frappe.msgprint(f"Đã tạo hóa đơn {invoice.name}.")
        return invoice.name
