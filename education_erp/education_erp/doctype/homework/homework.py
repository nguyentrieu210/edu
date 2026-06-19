import frappe
from frappe.model.document import Document


class Homework(Document):
    def validate(self):
        if not self.status:
            self.status = "Draft"
        if self.target == "Individual" and not self.student:
            frappe.throw("Bài tập giao riêng cần chọn học viên.")
