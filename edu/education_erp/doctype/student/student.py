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

    def after_insert(self) -> None:
        # Tự tạo tài khoản đăng nhập + gửi mail (nếu bật trong Education Settings).
        from edu.education_erp.api import _provision_user_for
        _provision_user_for("Student", self.name, self.full_name, self.get("email"), "Student")
