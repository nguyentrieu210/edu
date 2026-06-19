"""Phân quyền theo phạm vi dữ liệu cho portal Giáo viên/Học viên (GĐ3, §9.1, SEC-01/02).

- permission_query_conditions: lọc danh sách (list/report) theo phạm vi.
- has_permission: chặn truy cập trực tiếp document ngoài phạm vi (HTTP 403).

Admin/Giáo vụ (Administrator, System Manager, Education Manager, Academic Manager)
bỏ qua mọi giới hạn. Người dùng không phải teacher/student không bị thêm ràng buộc
(giữ nguyên quyền theo role - ví dụ Kế toán).
"""

import frappe

BYPASS_ROLES = {"System Manager", "Education Manager", "Academic Manager", "Administrator"}


def is_admin(user):
    if user == "Administrator":
        return True
    return bool(BYPASS_ROLES & set(frappe.get_roles(user)))


def teacher_of(user):
    return frappe.db.get_value("Teacher", {"user": user}, "name")


def student_of(user):
    return frappe.db.get_value("Student", {"user": user}, "name")


def teacher_class_ids(teacher):
    ids = frappe.get_all("Class", filters={"teacher": teacher}, pluck="name")
    ids += frappe.get_all("Class", filters={"substitute_teacher": teacher}, pluck="name")
    return list(set(ids))


def student_class_ids(student):
    return list(
        set(frappe.get_all("Program Enrollment", {"student": student, "docstatus": 1}, pluck="class_id"))
    )


def _in(field, values):
    if not values:
        return "1=0"
    joined = ", ".join(frappe.db.escape(v) for v in values)
    return f"{field} in ({joined})"


def _eq(field, value):
    return f"{field} = {frappe.db.escape(value)}"


# ---- permission_query_conditions ------------------------------------------

def class_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    t = teacher_of(user)
    if t:
        return _in("`tabClass`.name", teacher_class_ids(t))
    s = student_of(user)
    if s:
        return _in("`tabClass`.name", student_class_ids(s))
    return ""


def student_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    s = student_of(user)
    if s:
        return _eq("`tabStudent`.name", s)
    t = teacher_of(user)
    if t:
        cids = teacher_class_ids(t)
        sids = (
            frappe.get_all(
                "Program Enrollment",
                filters={"class_id": ["in", cids], "docstatus": 1},
                pluck="student",
            )
            if cids
            else []
        )
        return _in("`tabStudent`.name", list(set(sids)))
    return ""


def enrollment_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    s = student_of(user)
    if s:
        return _eq("`tabProgram Enrollment`.student", s)
    t = teacher_of(user)
    if t:
        return _in("`tabProgram Enrollment`.class_id", teacher_class_ids(t))
    return ""


def attendance_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    s = student_of(user)
    if s:
        return _eq("`tabStudent Attendance`.student", s)
    t = teacher_of(user)
    if t:
        return _in("`tabStudent Attendance`.class_id", teacher_class_ids(t))
    return ""


def assessment_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    s = student_of(user)
    if s:
        return _eq("`tabStudent Assessment`.student", s)
    t = teacher_of(user)
    if t:
        return _in("`tabStudent Assessment`.class_id", teacher_class_ids(t))
    return ""


def session_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    t = teacher_of(user)
    if t:
        return _in("`tabClass Session`.class_id", teacher_class_ids(t))
    s = student_of(user)
    if s:
        return _in("`tabClass Session`.class_id", student_class_ids(s))
    return ""


def homework_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    t = teacher_of(user)
    if t:
        return _in("`tabHomework`.class_id", teacher_class_ids(t))
    s = student_of(user)
    if s:
        classes = _in("`tabHomework`.class_id", student_class_ids(s))
        return (
            f"(`tabHomework`.status = 'Published' and "
            f"(({classes} and `tabHomework`.target = 'Whole Class') "
            f"or `tabHomework`.student = {frappe.db.escape(s)}))"
        )
    return ""


def invoice_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    s = student_of(user)
    if s:
        return _eq("`tabFee Invoice`.student", s)
    t = teacher_of(user)
    if t:
        return "1=0"  # giáo viên không xem tài chính (§7.1)
    return ""


# ---- has_permission (truy cập document trực tiếp) -------------------------

def _scope_ok_class(class_id, user):
    t = teacher_of(user)
    if t:
        return class_id in teacher_class_ids(t)
    s = student_of(user)
    if s:
        return class_id in student_class_ids(s)
    return True


def class_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    return _scope_ok_class(doc.name, user)


def student_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    s = student_of(user)
    if s:
        return doc.name == s
    t = teacher_of(user)
    if t:
        return bool(
            frappe.db.exists(
                "Program Enrollment",
                {"student": doc.name, "class_id": ["in", teacher_class_ids(t)], "docstatus": 1},
            )
        )
    return True


def enrollment_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    s = student_of(user)
    if s:
        return doc.student == s
    t = teacher_of(user)
    if t:
        return doc.class_id in teacher_class_ids(t)
    return True


def attendance_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    s = student_of(user)
    if s:
        return doc.student == s
    return _scope_ok_class(doc.class_id, user)


def assessment_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    s = student_of(user)
    if s:
        return doc.student == s
    return _scope_ok_class(doc.class_id, user)


def session_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    return _scope_ok_class(doc.class_id, user)


def invoice_has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    s = student_of(user)
    if s:
        return doc.student == s
    if teacher_of(user):
        return False
    return True
