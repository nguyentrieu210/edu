"""Tự tính tiến độ, chuyên cần và điểm trung bình (Giai đoạn 2, §4.3/§5.1/§5.2/§11).

Tất cả công thức nằm ở backend; UI chỉ hiển thị. Module này chỉ phụ thuộc `frappe`.
"""

import frappe
from frappe.utils import flt

PRESENT_STATUSES = ("Present", "Late")  # có mặt hợp lệ


def compute_weighted_average(student):
    """weighted_average = SUM(normalized_score * weight) / SUM(weight); normalized = score/max*100."""
    rows = frappe.get_all(
        "Student Assessment",
        filters={"student": student},
        fields=["score", "max_score", "weight"],
    )
    num = den = 0.0
    for r in rows:
        max_score = flt(r.max_score) or 100.0
        weight = flt(r.weight) or 1.0
        normalized = (flt(r.score) / max_score * 100.0) if max_score else 0.0
        num += normalized * weight
        den += weight
    return round(num / den, 2) if den else 0.0


def compute_attendance_rate(student):
    """Chỉ tính buổi đã hoàn thành (§5.1); buổi chưa Completed chưa vào chuyên cần chính thức.

    Bản ghi điểm danh không gắn class_session (dữ liệu cũ) vẫn được tính.
    """
    rows = frappe.get_all(
        "Student Attendance",
        filters={"student": student},
        fields=["status", "class_session"],
    )
    session_names = list({r.class_session for r in rows if r.class_session})
    completed = set()
    if session_names:
        completed = set(
            frappe.get_all(
                "Class Session",
                filters={"name": ["in", session_names], "session_status": "Completed"},
                pluck="name",
            )
        )

    counted = present = 0
    for r in rows:
        if r.class_session and r.class_session not in completed:
            continue
        counted += 1
        if r.status in PRESENT_STATUSES:
            present += 1
    return round(present / counted * 100, 2) if counted else 0.0


def get_active_class(student):
    enr = frappe.get_all(
        "Program Enrollment",
        filters={"student": student, "docstatus": 1, "enrollment_status": "Active"},
        fields=["class_id"],
        order_by="creation desc",
        limit=1,
    )
    return enr[0].class_id if enr else None


def compute_class_progress(class_id):
    """Trả về (completed, total, percent)."""
    total = int(frappe.db.get_value("Class", class_id, "total_sessions") or 0)
    if not total:
        total = frappe.db.count("Class Session", {"class_id": class_id})
    completed = frappe.db.count(
        "Class Session", {"class_id": class_id, "session_status": "Completed"}
    )
    percent = round(completed / total * 100, 2) if total else 0.0
    return completed, total, percent


def recompute_class_progress(class_id):
    if not class_id or not frappe.db.exists("Class", class_id):
        return None
    completed, total, percent = compute_class_progress(class_id)
    frappe.db.set_value("Class", class_id, "progress", percent)
    return completed, total, percent


def recompute_student_metrics(student):
    """Tính lại average_score, attendance_rate, progress cho một học viên."""
    if not student or not frappe.db.exists("Student", student):
        return None
    updates = {
        "average_score": compute_weighted_average(student),
        "attendance_rate": compute_attendance_rate(student),
    }
    class_id = get_active_class(student)
    if class_id:
        completed, total, _ = compute_class_progress(class_id)
        updates["progress"] = f"Buổi {completed}/{total}" if total else "Chưa có lịch"
    frappe.db.set_value("Student", student, updates)
    return updates


def recompute_all_metrics():
    """Tính lại toàn bộ (dùng cho scheduler hoặc chạy tay)."""
    for class_id in frappe.get_all("Class", pluck="name"):
        recompute_class_progress(class_id)
    for student in frappe.get_all("Student", pluck="name"):
        recompute_student_metrics(student)
