import frappe
from frappe.model.document import Document

class Teacher(Document):
	def after_insert(self) -> None:
		# Tự tạo tài khoản đăng nhập + gửi mail (nếu bật trong Education Settings).
		from edu.education_erp.api import _provision_user_for
		_provision_user_for("Teacher", self.name, self.get("teacher_name") or self.name, self.get("email"), "Teacher")
