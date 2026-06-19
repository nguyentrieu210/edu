import frappe
from frappe.model.document import Document


class HomeworkSubmission(Document):
    def validate(self):
        # Bất biến §8.1: duy nhất (homework, program_enrollment).
        if self.homework and self.program_enrollment:
            dup = frappe.db.exists(
                "Homework Submission",
                {
                    "homework": self.homework,
                    "program_enrollment": self.program_enrollment,
                    "name": ["!=", self.name or ""],
                },
            )
            if dup:
                frappe.throw(
                    f"Đã có bài nộp ({dup}) cho bài tập này của đăng ký này.",
                    title="Trùng bài nộp",
                )
        if self.program_enrollment and not self.student:
            self.student = frappe.db.get_value(
                "Program Enrollment", self.program_enrollment, "student"
            )
