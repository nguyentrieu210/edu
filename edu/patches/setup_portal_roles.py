"""Tạo role portal (Education Teacher / Education Student) và cấp quyền read/write
theo doctype. Việc lọc theo phạm vi dữ liệu do permission_query_conditions +
has_permission đảm nhiệm (xem permissions.py)."""

import frappe
from frappe.permissions import add_permission, update_permission_property

ROLE_TEACHER = "Education Teacher"
ROLE_STUDENT = "Education Student"

# doctype -> {who: (perm flags)}  r=read, w=write, c=create
GRANTS = {
    "Course": {"teacher": ("r",), "student": ("r",)},
    "Curriculum Module": {"teacher": ("r",), "student": ("r",)},
    "Lesson Template": {"teacher": ("r",), "student": ("r",)},
    "Class": {"teacher": ("r",), "student": ("r",)},
    "Class Session": {"teacher": ("r", "w"), "student": ("r",)},
    "Program Enrollment": {"teacher": ("r",), "student": ("r",)},
    "Student": {"teacher": ("r",), "student": ("r",)},
    "Student Attendance": {"teacher": ("r", "w", "c"), "student": ("r",)},
    "Student Assessment": {"teacher": ("r", "w", "c"), "student": ("r",)},
    "Homework": {"teacher": ("r", "w", "c"), "student": ("r",)},
    "Homework Submission": {"teacher": ("r", "w"), "student": ("r", "w", "c")},
    "Learning Material": {"teacher": ("r", "w", "c"), "student": ("r",)},
    "Fee Invoice": {"student": ("r",)},
}


def _ensure_role(role):
    if not frappe.db.exists("Role", role):
        frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def execute():
    _ensure_role(ROLE_TEACHER)
    _ensure_role(ROLE_STUDENT)
    role_map = {"teacher": ROLE_TEACHER, "student": ROLE_STUDENT}

    for doctype, grants in GRANTS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for who, flags in grants.items():
            role = role_map[who]
            try:
                add_permission(doctype, role, 0)
            except Exception:
                pass
            update_permission_property(doctype, role, 0, "read", 1 if "r" in flags else 0)
            update_permission_property(doctype, role, 0, "write", 1 if "w" in flags else 0)
            update_permission_property(doctype, role, 0, "create", 1 if "c" in flags else 0)

    frappe.db.commit()
