import frappe
from frappe.model.document import Document

ABSENT_STATUSES = ("Absent with Permission", "Absent without Permission")


class StudentAttendance(Document):
    def validate(self):
        self._guard_duplicate()
        self._sync_quick_fields()

    def after_insert(self):
        self.update_student_health()

    def on_update(self):
        # DocType này không submittable nên dùng after_insert/on_update thay cho on_submit.
        self.update_student_health()

    def _guard_duplicate(self):
        # Bất biến §1.4/§8.1: duy nhất theo (program_enrollment, class_session).
        if not (self.program_enrollment and self.class_session):
            return
        dup = frappe.db.exists(
            "Student Attendance",
            {
                "program_enrollment": self.program_enrollment,
                "class_session": self.class_session,
                "name": ["!=", self.name or ""],
            },
        )
        if dup:
            frappe.throw(
                f"Đã có điểm danh ({dup}) cho đăng ký này tại buổi học này.",
                title="Trùng điểm danh",
            )

    def _sync_quick_fields(self):
        """Suy ra class_id / student / attendance_date từ buổi học để tiện truy vấn nhanh."""
        if not self.class_session:
            return
        session = frappe.db.get_value(
            "Class Session", self.class_session, ["class_id", "session_date"], as_dict=True
        )
        if not session:
            return
        if not self.class_id:
            self.class_id = session.class_id
        if not self.attendance_date:
            self.attendance_date = session.session_date
        if not self.student and self.program_enrollment:
            self.student = frappe.db.get_value(
                "Program Enrollment", self.program_enrollment, "student"
            )

    def update_student_health(self):
        if not self.student:
            return
        attendances = frappe.get_all(
            "Student Attendance",
            filters={"student": self.student},
            fields=["status", "attendance_date"],
            order_by="attendance_date desc, creation desc",
            limit_page_length=3,
        )
        if not attendances:
            return

        absent_count = 0
        for att in attendances:
            if att.status in ABSENT_STATUSES:
                absent_count += 1
            else:
                break  # Dừng đếm nếu có buổi không vắng xen ngang

        new_health = "Đang học đều"
        if absent_count >= 3:
            new_health = "Khẩn cấp"
        elif absent_count == 2:
            new_health = "Cảnh báo"
        elif absent_count == 1:
            new_health = "Cần theo dõi"

        frappe.db.set_value("Student", self.student, "health_status", new_health)
