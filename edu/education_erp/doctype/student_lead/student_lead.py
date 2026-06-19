import frappe
from frappe.model.document import Document

class StudentLead(Document):
    # Type Annotations
    lead_name: str
    phone: str | None
    email: str | None
    source: str | None
    status: str | None

    def validate(self) -> None:
        if not self.lead_name:
            frappe.throw("Họ và tên là bắt buộc.")
