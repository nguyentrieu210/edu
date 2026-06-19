import frappe
from frappe.model.document import Document

class Student(Document):
    # Type Annotations for v15+
    full_name: str
    guardian: str | None
    progress: str | None
    attendance_status: str | None
    average_score: float

    def validate(self) -> None:
        if not self.full_name:
            frappe.throw("Student Full Name is required.")
