import frappe
from frappe.model.document import Document

from edu.education_erp import metrics


class StudentAssessment(Document):
    def validate(self):
        # Suy ra student/class_id từ enrollment nếu chưa có (tiện nhập liệu theo Enrollment).
        if self.program_enrollment and not self.student:
            self.student = frappe.db.get_value(
                "Program Enrollment", self.program_enrollment, "student"
            )

    def after_insert(self):
        metrics.recompute_student_metrics(self.student)

    def on_update(self):
        metrics.recompute_student_metrics(self.student)

    def on_trash(self):
        metrics.recompute_student_metrics(self.student)
