import json

import frappe
import requests
from frappe.utils import getdate, add_days, flt, nowdate

from edu.education_erp.doctype.class_session.class_session import (
    find_session_conflicts,
)
from edu.education_erp import metrics

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

def _get_doc_checked(doctype, name, ptype="read"):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission(ptype)
    return doc


def _require_create(doctype):
    if not frappe.has_permission(doctype, "create"):
        frappe.throw(f"Bạn không có quyền tạo {doctype}.", frappe.PermissionError)


def _set_student_status(student, status):
    doc = _get_doc_checked("Student", student, "write")
    doc.student_status = status
    doc.save()


CLIENT_DOCTYPE_ALIASES = {
    "CRM Lead": "Student Lead",
}

CLIENT_WRITE_FIELDS = {
    "Class": {
        "class_name", "course", "teacher", "substitute_teacher", "classroom",
        "start_date", "schedule_template", "start_time", "end_time",
        "total_sessions", "max_capacity", "standard_fee", "status",
    },
    "Course": {"course_name", "description", "base_fee"},
    "Curriculum Module": {"course", "module_name", "sequence", "description"},
    "Fee Invoice": {
        "student", "program_enrollment", "posting_date", "due_date", "items",
        "discount_amount", "discount_reason", "tax_amount",
    },
    "Homework": {
        "title", "class_id", "class_session", "target", "student", "assigned_date",
        "due_date", "status", "description", "materials",
    },
    "Internal Task": {"title", "description", "assigned_to", "due_date", "priority", "status"},
    "Learning Material": {
        "title", "material_type", "course", "class_id", "url", "is_public", "description",
    },
    "Lesson Template": {
        "curriculum_module", "course", "lesson_no", "title", "duration_minutes",
        "kanji", "vocabulary", "grammar", "reading", "listening", "kaiwa",
        "homework", "materials",
    },
    "Onboarding Task": {"is_completed"},
    "Room Booking": {
        "classroom", "booking_date", "start_time", "end_time", "purpose", "booked_by", "status",
    },
    "Student": {
        "full_name", "user", "guardian", "health_status", "date_of_birth", "gender",
        "email", "phone", "source", "occupation", "rating", "message_response",
        "student_status",
    },
    "Student Appointment": {"lead", "appointment_date", "appointment_time", "purpose", "status"},
    "Student Assessment": {
        "student", "class_id", "program_enrollment", "class_session", "assessment_name",
        "assessment_type", "score", "max_score", "weight", "notes",
    },
    "Student Lead": {
        "lead_name", "phone", "email", "source", "status", "date_of_birth", "gender",
        "occupation", "guardian_name", "guardian_phone", "lost_reason",
    },
    "Teacher": {"teacher_name", "user", "phone", "email", "status"},
}

CLIENT_CHILD_FIELDS = {
    ("Fee Invoice", "items"): {"item_name", "amount"},
}

CLIENT_DELETE_DOCTYPES = {
    "Class", "Course", "Curriculum Module", "Fee Invoice", "Fee Payment",
    "Homework", "Learning Material", "Lesson Template", "Room Booking",
    "Student", "Student Appointment", "Student Lead", "Teacher",
}

PROTECTED_CLIENT_FIELDS = {
    "doctype", "name", "owner", "creation", "modified", "modified_by",
    "idx", "docstatus", "amended_from",
}


def _normalize_doctype(doctype):
    return CLIENT_DOCTYPE_ALIASES.get(doctype, doctype)


def _parse_payload(value):
    if isinstance(value, str):
        return frappe.parse_json(value)
    return value or {}


def _sanitize_child_rows(parent_doctype, table_field, rows):
    allowed = CLIENT_CHILD_FIELDS.get((parent_doctype, table_field))
    if allowed is None:
        frappe.throw(f"Field {table_field} is not writable from this screen.")
    if isinstance(rows, str):
        rows = frappe.parse_json(rows)
    if not isinstance(rows, list):
        frappe.throw(f"Field {table_field} must be a list.")

    clean_rows = []
    for row in rows:
        row = _parse_payload(row)
        clean_rows.append({k: v for k, v in row.items() if k in allowed})
    return clean_rows


def _sanitize_client_values(doctype, values):
    doctype = _normalize_doctype(doctype)
    allowed = CLIENT_WRITE_FIELDS.get(doctype)
    if not allowed:
        frappe.throw(f"Frontend writes are not enabled for {doctype}.", frappe.PermissionError)

    values = _parse_payload(values)
    clean = {}
    blocked = []
    for field, value in values.items():
        if field in PROTECTED_CLIENT_FIELDS:
            blocked.append(field)
            continue
        if field not in allowed:
            blocked.append(field)
            continue
        if (doctype, field) in CLIENT_CHILD_FIELDS:
            clean[field] = _sanitize_child_rows(doctype, field, value)
        else:
            clean[field] = value

    if blocked:
        blocked_fields = ", ".join(str(field) for field in sorted(blocked, key=str))
        frappe.throw(f"Fields are not writable from this screen: {blocked_fields}.")
    return clean


def _enforce_create_rules(doctype, values):
    fixed_status = {
        "Homework": ("status", "Draft"),
        "Internal Task": ("status", "To Do"),
        "Room Booking": ("status", "Booked"),
        "Student Appointment": ("status", "Scheduled"),
        "Student Lead": ("status", "New"),
    }
    if doctype in fixed_status:
        field, expected = fixed_status[doctype]
        requested = values.get(field)
        if requested not in (None, "", expected):
            frappe.throw(f"{doctype} must be created as {expected}.")
        values[field] = expected

    if doctype == "Student Appointment" and values.get("lead"):
        _get_doc_checked("Student Lead", values["lead"], "read")

    if doctype == "Fee Invoice":
        if values.get("student"):
            _get_doc_checked("Student", values["student"], "read")
        if values.get("program_enrollment"):
            enrollment = _get_doc_checked("Program Enrollment", values["program_enrollment"], "read")
            if values.get("student") and enrollment.student != values["student"]:
                frappe.throw("Enrollment does not belong to this student.")

    return values


def _enforce_update_rules(doctype, doc, values):
    if doctype == "Student Lead":
        next_status = values.get("status")
        if next_status == "Enrolled":
            frappe.throw("Use convert_lead_to_student to mark a lead as Enrolled.")
        if next_status == "Lost" and not (values.get("lost_reason") or doc.get("lost_reason")):
            frappe.throw("Lost leads require a lost reason.")

    if doctype == "Student Appointment" and "status" in values:
        if doc.status != "Scheduled" and values["status"] != doc.status:
            frappe.throw("Only scheduled appointments can change status from this screen.")

    return values


@frappe.whitelist()
def create_document(doc):
    doc = _parse_payload(doc)
    doctype = _normalize_doctype(doc.get("doctype"))
    if not doctype:
        frappe.throw("Missing doctype.")
    _require_create(doctype)
    values = dict(doc)
    values.pop("doctype", None)
    values = _sanitize_client_values(doctype, values)
    values = _enforce_create_rules(doctype, values)

    new_doc = frappe.get_doc({"doctype": doctype, **values})
    new_doc.insert()
    return {"name": new_doc.name, "doctype": doctype}


@frappe.whitelist()
def update_document(doctype, name, values=None, fieldname=None, value=None):
    doctype = _normalize_doctype(doctype)
    if values is None:
        if isinstance(fieldname, dict):
            values = fieldname
        else:
            if not fieldname:
                frappe.throw("Missing fieldname.")
            values = {fieldname: value}
    values = _sanitize_client_values(doctype, values)
    if not values:
        return {"name": name, "doctype": doctype}

    doc = _get_doc_checked(doctype, name, "write")
    values = _enforce_update_rules(doctype, doc, values)
    doc.update(values)
    doc.save()
    return {"name": doc.name, "doctype": doctype}


@frappe.whitelist()
def delete_document(doctype, name):
    doctype = _normalize_doctype(doctype)
    if doctype not in CLIENT_DELETE_DOCTYPES:
        frappe.throw(f"Frontend delete is not enabled for {doctype}.", frappe.PermissionError)

    doc = _get_doc_checked(doctype, name, "delete")
    if getattr(doc, "docstatus", 0) == 1:
        frappe.throw(f"{doctype} {name} is submitted. Cancel it instead of deleting it.")
    frappe.delete_doc(doctype, name)
    return {"name": name, "doctype": doctype, "deleted": True}


@frappe.whitelist()
def get_csrf_token():
    return frappe.sessions.get_csrf_token()

@frappe.whitelist()
def get_students():
    return frappe.get_list(
        "Student", 
        fields=["name", "full_name", "progress", "average_score", "attendance_status", "health_status", "student_status", "date_of_birth", "gender", "email", "phone", "source", "occupation", "rating", "message_response", "creation"], 
        order_by="creation desc"
    )

@frappe.whitelist()
def get_payments():
    return frappe.get_list(
        "Fee Payment",
        fields=["name", "student", "payment_date", "payment_method", "amount", "reference_no"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_dashboard_stats():
    students_count = len(frappe.get_list("Student", pluck="name", limit_page_length=0))
    
    invoices = frappe.get_list(
        "Fee Invoice",
        filters={"docstatus": 1},
        fields=["total_amount", "outstanding_amount"],
    )
    
    total_amount = sum(inv.total_amount or 0 for inv in invoices)
    outstanding_amount = sum(inv.outstanding_amount or 0 for inv in invoices)
    paid_amount = max(0, total_amount - outstanding_amount)
    
    return {
        "students_count": students_count,
        "paid_amount": paid_amount,
        "outstanding_amount": outstanding_amount
    }

@frappe.whitelist()
def get_unpaid_invoices(student):
    return frappe.get_list(
        "Fee Invoice",
        filters={"student": student, "status": ["in", ["Unpaid", "Partially Paid"]], "docstatus": 1},
        fields=["name", "total_amount", "outstanding_amount", "due_date"],
        order_by="due_date asc"
    )

@frappe.whitelist()
def create_payment(student, payment_date, payment_method, amount, invoice, reference_no=None, reference_date=None):
    _require_create("Fee Payment")
    # Bất biến §3.7/§14.1 FIN-02: chỉ thu tiền trên hóa đơn đã submit và chưa hủy.
    inv = _get_doc_checked("Fee Invoice", invoice, "read")
    if inv.docstatus != 1:
        frappe.throw("Chỉ được thu tiền trên hóa đơn đã duyệt (submitted).")
    if inv.status == "Cancelled":
        frappe.throw("Hóa đơn đã hủy, không thể thu tiền.")

    if inv.student != student:
        frappe.throw("Invoice does not belong to this student.")

    payment = frappe.get_doc({
        "doctype": "Fee Payment",
        "student": student,
        "posting_date": payment_date,
        "payment_date": payment_date,
        "payment_method": payment_method,
        "amount": float(amount),
        "reference_no": reference_no,
        "reference_date": reference_date,
        "references": [
            {
                "invoice": invoice,
                "allocated_amount": float(amount)
            }
        ]
    })
    payment.insert()
    payment.submit()
    return payment.name

@frappe.whitelist()
def get_leads():
    return frappe.get_list(
        "Student Lead",
        fields=["name", "lead_name", "phone", "email", "source", "status", "creation", "date_of_birth", "gender", "occupation", "guardian_name", "guardian_phone"],
        order_by="creation desc"
    )

@frappe.whitelist()
def create_lead(lead_name, phone, email=None, source="Website", status="New", date_of_birth=None, gender=None, occupation=None, guardian_name=None, guardian_phone=None):
    _require_create("Student Lead")
    doc = frappe.get_doc({
        "doctype": "Student Lead",
        "lead_name": lead_name,
        "phone": phone,
        "email": email,
        "source": source,
        "status": status,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "occupation": occupation,
        "guardian_name": guardian_name,
        "guardian_phone": guardian_phone
    })
    doc.insert()
    return doc.name

@frappe.whitelist()
def convert_lead_to_student(lead_id):
    lead = _get_doc_checked("Student Lead", lead_id, "write")
    _require_create("Student")
    
    guardian_link = None
    if lead.get("guardian_name"):
        g_name = lead.guardian_name
        g_phone = lead.get("guardian_phone")
        
        # Check if guardian already exists
        existing_guardian = frappe.get_list("Guardian", filters={"guardian_name": g_name, "phone": g_phone}, limit=1)
        if existing_guardian:
            guardian_link = existing_guardian[0].name
        else:
            guardian = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": g_name,
                "phone": g_phone
            })
            guardian.insert()
            guardian_link = guardian.name
            
    # Create Student
    student = frappe.get_doc({
        "doctype": "Student",
        "full_name": lead.lead_name,
        "date_of_birth": lead.get("date_of_birth"),
        "gender": lead.get("gender"),
        "email": lead.email,
        "phone": lead.phone,
        "source": lead.source,
        "occupation": lead.get("occupation"),
        "guardian": guardian_link,
        "health_status": "Đang học đều"
    })
    student.insert()

    # Update Lead status to "Enrolled"
    lead.status = "Enrolled"
    lead.save()
    
    return {
        "student_id": student.name,
        "student_name": student.full_name
    }

@frappe.whitelist()
def get_teachers():
    return frappe.get_list(
        "Teacher",
        fields=["name", "teacher_name", "phone", "email", "status"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_courses():
    return frappe.get_list(
        "Course",
        fields=["name", "course_name", "description", "base_fee"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_curriculum(course):
    """Trả về cấu trúc chương trình: các học phần + giáo án từng buổi (§3.1)."""
    modules = frappe.get_list(
        "Curriculum Module",
        filters={"course": course},
        fields=["name", "module_name", "sequence", "description"],
        order_by="sequence asc, creation asc",
    )
    for m in modules:
        m["lessons"] = frappe.get_list(
            "Lesson Template",
            filters={"curriculum_module": m["name"]},
            fields=[
                "name", "lesson_no", "title", "duration_minutes",
                "kanji", "vocabulary", "grammar", "reading", "listening", "kaiwa",
                "homework", "materials",
            ],
            order_by="lesson_no asc, creation asc",
        )
    return modules


@frappe.whitelist()
def get_homework(class_id=None):
    filters = {}
    if class_id:
        filters["class_id"] = class_id
    rows = frappe.get_list(
        "Homework",
        filters=filters,
        fields=[
            "name", "title", "class_id", "class_session", "target", "student",
            "assigned_date", "due_date", "status", "description",
        ],
        order_by="creation desc",
    )
    for r in rows:
        r["submission_count"] = frappe.db.count("Homework Submission", {"homework": r["name"]})
    return rows


@frappe.whitelist()
def publish_homework(homework):
    """Chỉ Homework đã publish mới hiển thị trên portal học viên (§5.3)."""
    hw = _get_doc_checked("Homework", homework, "write")
    if hw.status != "Draft":
        frappe.throw(f"Chỉ publish bài tập đang Draft (hiện tại: {hw.status}).")
    hw.status = "Published"
    if not hw.assigned_date:
        hw.assigned_date = nowdate()
    hw.save()
    return {"status": "Published"}


@frappe.whitelist()
def close_homework(homework):
    hw = _get_doc_checked("Homework", homework, "write")
    if hw.status not in ("Published", "Draft"):
        frappe.throw(f"Không thể đóng bài tập ở trạng thái {hw.status}.")
    hw.status = "Closed"
    hw.save()
    return {"status": "Closed"}


@frappe.whitelist()
def get_materials(course=None, class_id=None, public_only=0):
    filters = {}
    if course:
        filters["course"] = course
    if class_id:
        filters["class_id"] = class_id
    if int(public_only or 0):
        filters["is_public"] = 1
    return frappe.get_list(
        "Learning Material",
        filters=filters,
        fields=["name", "title", "material_type", "course", "class_id", "url", "is_public", "description"],
        order_by="creation desc",
    )


@frappe.whitelist()
def get_classes():
    return frappe.get_list(
        "Class",
        fields=["name", "class_name", "course", "teacher", "start_date", "status"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_attendances(class_id=None, student=None):
    filters = {}
    if class_id:
        filters["class_id"] = class_id
    if student:
        filters["student"] = student
    return frappe.get_list(
        "Student Attendance",
        filters=filters,
        fields=["name", "class_id", "student", "attendance_date", "status"],
        order_by="attendance_date desc"
    )

@frappe.whitelist()
def get_assessments(class_id=None, student=None):
    filters = {}
    if class_id:
        filters["class_id"] = class_id
    if student:
        filters["student"] = student
    return frappe.get_list(
        "Student Assessment",
        filters=filters,
        fields=["name", "student", "class_id", "assessment_name", "score", "notes"],
        order_by="creation desc"
    )

@frappe.whitelist()
def get_class_sessions(class_id):
    _get_doc_checked("Class", class_id, "read")
    return frappe.get_list(
        "Class Session",
        filters={"class_id": class_id},
        fields=[
            "name", "session_date", "start_time", "end_time", "lesson_topic",
            "session_status", "teacher", "teacher_attendance_status",
        ],
        order_by="session_date asc, start_time asc",
    )


@frappe.whitelist()
def get_session_roster(class_session):
    """Danh sách điểm danh của một buổi: enrollment Active của lớp + bản ghi điểm danh đã có."""
    session_doc = _get_doc_checked("Class Session", class_session, "read")
    session = frappe._dict({
        "name": session_doc.name,
        "class_id": session_doc.class_id,
        "session_date": session_doc.session_date,
        "start_time": session_doc.start_time,
        "end_time": session_doc.end_time,
        "teacher": session_doc.teacher,
        "lesson_topic": session_doc.lesson_topic,
        "teacher_attendance_status": session_doc.teacher_attendance_status,
        "session_status": session_doc.session_status,
    })

    enrollments = frappe.get_list(
        "Program Enrollment",
        filters={"class_id": session.class_id, "docstatus": 1, "enrollment_status": "Active"},
        fields=["name", "student"],
    )
    existing = frappe.get_list(
        "Student Attendance",
        filters={"class_session": class_session},
        fields=["name", "program_enrollment", "status", "attendance_type", "minutes_late"],
    )
    by_enr = {a.program_enrollment: a for a in existing}

    rows = []
    for e in enrollments:
        ex = by_enr.get(e.name)
        rows.append({
            "program_enrollment": e.name,
            "student": e.student,
            "status": ex.status if ex else "Present",
            "attendance_type": ex.attendance_type if ex else "Regular",
            "minutes_late": ex.minutes_late if ex else 0,
            "attendance_name": ex.name if ex else None,
        })
    return {"session": session, "rows": rows}


@frappe.whitelist()
def save_session_attendance(class_session, rows, teacher_attendance_status=None):
    """Lưu điểm danh hàng loạt theo buổi học (§15.2 save_session_attendance).

    Mỗi (program_enrollment, class_session) duy nhất một bản ghi: có thì update, chưa có thì tạo.
    Chạy trong transaction của request.
    """
    if isinstance(rows, str):
        rows = json.loads(rows)

    session_doc = _get_doc_checked("Class Session", class_session, "write")
    session = frappe._dict({
        "class_id": session_doc.class_id,
        "session_date": session_doc.session_date,
    })

    saved = 0
    touched_students = set()
    for r in rows:
        pe = r.get("program_enrollment")
        if not pe:
            continue
        enrollment = _get_doc_checked("Program Enrollment", pe, "read")
        if enrollment.class_id != session.class_id:
            frappe.throw("Đăng ký học không thuộc lớp của buổi học này.")
        student = enrollment.student
        touched_students.add(student)
        status = r.get("status") or "Present"
        atype = r.get("attendance_type") or "Regular"
        minutes_late = int(r.get("minutes_late") or 0)

        existing = frappe.db.get_value(
            "Student Attendance",
            {"program_enrollment": pe, "class_session": class_session},
            "name",
        )
        if existing:
            doc = frappe.get_doc("Student Attendance", existing)
            doc.check_permission("write")
            doc.status = status
            doc.attendance_type = atype
            doc.minutes_late = minutes_late
            doc.save()
        else:
            frappe.get_doc({
                "doctype": "Student Attendance",
                "program_enrollment": pe,
                "class_session": class_session,
                "class_id": session.class_id,
                "student": student,
                "attendance_date": session.session_date,
                "status": status,
                "attendance_type": atype,
                "minutes_late": minutes_late,
            }).insert()
        saved += 1

    if teacher_attendance_status:
        session_doc.teacher_attendance_status = teacher_attendance_status
        session_doc.save()

    # Tính lại chuyên cần cho các học viên vừa điểm danh.
    for st in touched_students:
        metrics.recompute_student_metrics(st)
    return {"saved": saved}


@frappe.whitelist()
def complete_class_session(class_session):
    """Hoàn tất buổi học (§5, §15.2): yêu cầu đã điểm danh đủ học viên Active,
    đặt session_status = Completed, rồi tính lại tiến độ lớp + metrics học viên.
    """
    session = _get_doc_checked("Class Session", class_session, "write")

    active = frappe.get_list(
        "Program Enrollment",
        filters={"class_id": session.class_id, "docstatus": 1, "enrollment_status": "Active"},
        pluck="name",
    )
    if active:
        marked = set(
            frappe.get_list(
                "Student Attendance",
                filters={"class_session": class_session, "program_enrollment": ["in", active]},
                pluck="program_enrollment",
            )
        )
        missing = [a for a in active if a not in marked]
        if missing:
            frappe.throw(
                f"Chưa thể hoàn tất: còn {len(missing)} học viên Active chưa được điểm danh."
            )

    session.session_status = "Completed"
    session.save()

    metrics.recompute_class_progress(session.class_id)
    students = frappe.get_list(
        "Program Enrollment",
        filters={"class_id": session.class_id, "docstatus": 1, "enrollment_status": "Active"},
        pluck="student",
    )
    for st in set(students):
        metrics.recompute_student_metrics(st)

    return {"session_status": "Completed"}


@frappe.whitelist()
def recompute_student_metrics(student):
    _get_doc_checked("Student", student, "read")
    return metrics.recompute_student_metrics(student)


@frappe.whitelist()
def recompute_all_metrics():
    if not frappe.has_permission("Education Settings", "write"):
        frappe.throw("Bạn không có quyền tính lại toàn bộ chỉ số.", frappe.PermissionError)
    metrics.recompute_all_metrics()
    return {"ok": True}


@frappe.whitelist()
def generate_class_sessions(class_id):
    cls = _get_doc_checked("Class", class_id, "write")
    if not cls.schedule_template or not cls.total_sessions or not cls.start_date:
        frappe.throw("Vui lòng nhập Ngày khai giảng, Mẫu lịch học và Tổng số buổi để sinh lịch tự động.")
        
    template_map = {
        "2-4-6": [0, 2, 4], # Monday=0, Wed=2, Fri=4
        "3-5-7": [1, 3, 5],
        "T7-CN": [5, 6]
    }
    
    if cls.schedule_template == "Custom":
        frappe.throw("Tính năng sinh lịch tự động chưa hỗ trợ mẫu Custom.")

    allowed_weekdays = template_map.get(cls.schedule_template)

    # 1. Lập danh sách ngày dự kiến trước.
    planned_dates = []
    current_date = getdate(cls.start_date)
    while len(planned_dates) < cls.total_sessions:
        if current_date.weekday() in allowed_weekdays:
            planned_dates.append(current_date)
        current_date = add_days(current_date, 1)

    # 2. Kiểm tra xung đột giáo viên/phòng với LỚP KHÁC trước khi xóa lịch cũ (§10.6).
    for d in planned_dates:
        conflicts = find_session_conflicts(
            d,
            cls.start_time,
            cls.end_time,
            teacher=cls.teacher,
            classroom=cls.classroom,
            exclude_class=class_id,
        )
        if conflicts:
            c = conflicts[0]
            frappe.throw(
                f"Không thể sinh lịch: ngày {d} trùng {c['type']} với buổi {c['session']} "
                f"(lớp {c['class_id']}).",
                title="Xung đột lịch",
            )

    # 3. Hợp lệ -> xóa lịch cũ rồi tạo lịch mới.
    existing_sessions = frappe.get_list("Class Session", filters={"class_id": class_id}, fields=["name", "session_status"])
    protected = frappe.get_list(
        "Student Attendance",
        filters={"class_id": class_id},
        fields=["name"],
        limit_page_length=1,
    )
    if protected:
        frappe.throw("Lớp đã có dữ liệu điểm danh, không được xóa và sinh lại lịch. Hãy dùng quy trình hủy/đổi buổi.")
    for session in existing_sessions:
        frappe.delete_doc("Class Session", session.name)

    for idx, d in enumerate(planned_dates):
        session = frappe.get_doc({
            "doctype": "Class Session",
            "class_id": class_id,
            "session_date": d,
            "start_time": cls.start_time,
            "end_time": cls.end_time,
            "teacher": cls.teacher,
            "classroom": cls.classroom,
            "session_status": "Scheduled",
            "session_type": "Regular",
            "lesson_topic": f"Buổi {idx + 1}",
        })
        session.insert()

    return f"Đã tạo {len(planned_dates)} buổi học."

@frappe.whitelist()
def calculate_teacher_salary(teacher, month, year, rate_per_session):
    _get_doc_checked("Teacher", teacher, "read")
    sessions = frappe.get_list(
        "Class Session",
        filters={
            "teacher": teacher,
            "teacher_attendance_status": "Present",
        },
        fields=["name", "session_date"]
    )
    
    valid_sessions = []
    for s in sessions:
        if s.session_date.month == int(month) and s.session_date.year == int(year):
            valid_sessions.append(s)

    total_sessions = len(valid_sessions)
    total_salary = total_sessions * float(rate_per_session)
    return {
        "total_sessions_taught": total_sessions,
        "total_salary": total_salary
    }

@frappe.whitelist()
def get_student_cards():
    return frappe.get_list(
        "Student Card",
        fields=["name", "student", "card_number", "issue_date", "status"],
        order_by="creation desc"
    )

@frappe.whitelist()
def create_student_card(student, card_number, issue_date, status="Active"):
    _require_create("Student Card")
    doc = frappe.get_doc({
        "doctype": "Student Card",
        "student": student,
        "card_number": card_number,
        "issue_date": issue_date,
        "status": status
    })
    doc.insert()
    return doc.name

@frappe.whitelist()
def get_consultation_logs(lead_id):
    _get_doc_checked("Student Lead", lead_id, "read")
    return frappe.get_list(
        "Consultation Log",
        filters={"lead": lead_id},
        fields=["name", "contact_date", "notes", "next_follow_up", "creation"],
        order_by="contact_date desc, creation desc"
    )

@frappe.whitelist()
def add_consultation_log(lead_id, notes, contact_date, next_follow_up=None):
    _get_doc_checked("Student Lead", lead_id, "write")
    _require_create("Consultation Log")
    doc = frappe.get_doc({
        "doctype": "Consultation Log",
        "lead": lead_id,
        "contact_date": contact_date,
        "notes": notes,
        "next_follow_up": next_follow_up or None
    })
    doc.insert()
    return doc.name

@frappe.whitelist()
def get_placement_tests(lead_id):
    _get_doc_checked("Student Lead", lead_id, "read")
    return frappe.get_list(
        "Placement Test",
        filters={"lead": lead_id},
        fields=["name", "test_date", "score", "recommended_course", "status", "creation"],
        order_by="test_date desc, creation desc"
    )

@frappe.whitelist()
def add_placement_test(lead_id, test_date, score, recommended_course=None):
    _get_doc_checked("Student Lead", lead_id, "write")
    _require_create("Placement Test")
    doc = frappe.get_doc({
        "doctype": "Placement Test",
        "lead": lead_id,
        "test_date": test_date,
        "score": float(score),
        "recommended_course": recommended_course or None,
        "status": "Evaluated"
    })
    doc.insert()
    return doc.name


@frappe.whitelist()
def regenerate_invoice(fee_schedule):
    """Tạo lại hóa đơn cho một Lịch thu đã duyệt nhưng hóa đơn trước đó đã bị hủy."""
    sched = _get_doc_checked("Fee Schedule", fee_schedule, "write")
    if sched.docstatus != 1:
        frappe.throw("Lịch thu chưa được duyệt, không thể tạo hóa đơn.")

    active = frappe.get_list(
        "Fee Invoice",
        filters={"fee_schedule": fee_schedule, "docstatus": 1},
        limit=1,
    )
    if active:
        frappe.throw(f"Đã tồn tại hóa đơn hiệu lực {active[0].name} cho lịch thu này.")

    return sched.make_invoice()


@frappe.whitelist()
def get_enrollments(class_id=None, student=None):
    filters = {}
    if class_id:
        filters["class_id"] = class_id
    if student:
        filters["student"] = student
    return frappe.get_list(
        "Program Enrollment",
        filters=filters,
        fields=[
            "name", "student", "class_id", "enrollment_type", "enrollment_status",
            "enrollment_date", "list_price", "net_fee", "docstatus", "creation",
        ],
        order_by="creation desc",
    )


@frappe.whitelist()
def get_class_enrollment_info(class_id):
    """Thông tin để chốt học phí + kiểm tra sĩ số khi gán học viên vào lớp."""
    class_doc = _get_doc_checked("Class", class_id, "read")
    cls = frappe._dict({
        "class_name": class_doc.class_name,
        "course": class_doc.course,
        "standard_fee": class_doc.standard_fee,
        "max_capacity": class_doc.max_capacity,
        "teacher": class_doc.teacher,
    })
    base_fee = flt(frappe.db.get_value("Course", cls.course, "base_fee")) if cls.course else 0.0
    active_count = frappe.db.count(
        "Program Enrollment",
        {"class_id": class_id, "docstatus": 1, "enrollment_status": "Active"},
    )
    return {
        "class_name": cls.class_name,
        "standard_fee": flt(cls.standard_fee),
        "base_fee": base_fee,
        "list_price": flt(cls.standard_fee) or base_fee,
        "max_capacity": int(cls.max_capacity or 0),
        "active_count": active_count,
    }


@frappe.whitelist()
def create_enrollment(
    student,
    class_id,
    enrollment_date=None,
    enrollment_type="Official",
    list_price=None,
    discount_type=None,
    discount_value=0,
    discount_reason=None,
    submit=1,
):
    """Tạo (và submit) đăng ký học trong một transaction.

    Khi submit: chốt snapshot học phí, chặn trùng đăng ký Active, chặn vượt sĩ số,
    sinh onboarding + lịch thu + hóa đơn. Lỗi bất kỳ bước nào -> rollback toàn bộ.
    """
    _require_create("Program Enrollment")
    _get_doc_checked("Student", student, "read")
    _get_doc_checked("Class", class_id, "read")
    doc = frappe.get_doc({
        "doctype": "Program Enrollment",
        "student": student,
        "class_id": class_id,
        "enrollment_type": enrollment_type or "Official",
        "enrollment_status": "Pending",
        "enrollment_date": enrollment_date or nowdate(),
        "list_price": flt(list_price) if list_price not in (None, "") else None,
        "discount_type": discount_type or None,
        "discount_value": flt(discount_value),
        "discount_reason": discount_reason,
    })
    doc.insert()
    if int(submit):
        doc.submit()
    return {
        "name": doc.name,
        "enrollment_status": doc.enrollment_status,
        "net_fee": doc.net_fee,
    }


def _get_active_enrollment(program_enrollment):
    enr = _get_doc_checked("Program Enrollment", program_enrollment, "write")
    if enr.docstatus != 1:
        frappe.throw("Chỉ thao tác trên đăng ký đã duyệt (submitted).")
    return enr


@frappe.whitelist()
def defer_enrollment(program_enrollment, leave_from_date, leave_to_date, reason=None):
    """Bảo lưu (§10.2): Active -> Deferred, lưu bản ghi Student Deferment (audit)."""
    enr = _get_active_enrollment(program_enrollment)
    if enr.enrollment_status != "Active":
        frappe.throw(f"Chỉ bảo lưu đăng ký đang Active (hiện tại: {enr.enrollment_status}).")

    deferment = frappe.get_doc({
        "doctype": "Student Deferment", "student": enr.student, "class_id": enr.class_id,
        "leave_from_date": leave_from_date, "leave_to_date": leave_to_date,
        "reason": reason, "status": "Approved",
    })
    deferment.insert()
    deferment.submit()
    enr.enrollment_status = "Deferred"
    enr.save()
    _set_student_status(enr.student, "Bảo lưu")
    return {"enrollment_status": "Deferred", "deferment": deferment.name}


@frappe.whitelist()
def resume_enrollment(program_enrollment):
    """Tiếp tục học (§10.2): Deferred -> Active."""
    enr = _get_active_enrollment(program_enrollment)
    if enr.enrollment_status != "Deferred":
        frappe.throw(f"Chỉ tiếp tục đăng ký đang bảo lưu (hiện tại: {enr.enrollment_status}).")
    enr.enrollment_status = "Active"
    enr.save()
    _set_student_status(enr.student, "Đang học")
    return {"enrollment_status": "Active"}


@frappe.whitelist()
def drop_enrollment(program_enrollment, reason=None, refund_invoice=None, refund_amount=0, refund_date=None):
    """Nghỉ học (§10.3): -> Dropped. Giữ nguyên lịch sử. Tùy chọn tạo Fee Refund (Draft)
    để vai trò tài chính duyệt; KHÔNG tự chốt số tiền hoàn (chính sách là quyết định nghiệp vụ §22).
    """
    enr = _get_active_enrollment(program_enrollment)
    if enr.enrollment_status in ("Dropped", "Completed", "Transferred"):
        frappe.throw(f"Đăng ký đã ở trạng thái {enr.enrollment_status}, không thể nghỉ học.")

    enr.enrollment_status = "Dropped"
    enr.save()
    _set_student_status(enr.student, "Nghỉ học")

    refund = None
    if refund_invoice and flt(refund_amount) > 0:
        refund_inv = _get_doc_checked("Fee Invoice", refund_invoice, "read")
        if refund_inv.student != enr.student:
            frappe.throw("Hóa đơn hoàn tiền không thuộc học viên của đăng ký này.")
        _require_create("Fee Refund")
        ref = frappe.get_doc({
            "doctype": "Fee Refund", "student": enr.student, "invoice_reference": refund_invoice,
            "refund_amount": flt(refund_amount), "refund_date": refund_date or nowdate(),
            "reason": reason or "Nghỉ học", "status": "Draft",
        })
        ref.insert()  # để finance submit sau
        refund = ref.name

    metrics.recompute_student_metrics(enr.student)
    return {"enrollment_status": "Dropped", "refund": refund}


@frappe.whitelist()
def transfer_enrollment(program_enrollment, to_class, transfer_date=None, reason=None,
                        new_list_price=None, new_discount_type=None, new_discount_value=0,
                        new_discount_reason=None):
    """Chuyển lớp (§10.1, REQ-TRF-001) trong một transaction:
    lưu Class Transfer (audit) -> đóng enrollment cũ (Transferred) -> tạo enrollment mới ở lớp đích.
    Lịch sử attendance/assessment/payment giữ nguyên ở enrollment cũ.
    """
    enr = _get_active_enrollment(program_enrollment)
    if enr.enrollment_status != "Active":
        frappe.throw(f"Chỉ chuyển lớp khi đăng ký đang Active (hiện tại: {enr.enrollment_status}).")
    if to_class == enr.class_id:
        frappe.throw("Lớp đích trùng với lớp hiện tại.")
    _get_doc_checked("Class", to_class, "read")

    transfer = frappe.get_doc({
        "doctype": "Class Transfer", "student": enr.student, "from_class": enr.class_id,
        "to_class": to_class, "transfer_date": transfer_date or nowdate(),
        "reason": reason, "status": "Approved",
    })
    transfer.insert()
    transfer.submit()

    enr.enrollment_status = "Transferred"
    enr.save()

    new_enr = create_enrollment(
        student=enr.student, class_id=to_class, enrollment_date=transfer_date or nowdate(),
        list_price=new_list_price, discount_type=new_discount_type,
        discount_value=new_discount_value, discount_reason=new_discount_reason, submit=1,
    )
    metrics.recompute_student_metrics(enr.student)
    return {"old_status": "Transferred", "transfer": transfer.name, "new_enrollment": new_enr["name"]}


@frappe.whitelist()
def get_my_context():
    """Xác định người dùng hiện tại là giáo viên/học viên (lấy từ session, không tin client)."""
    from edu.education_erp import permissions as perm
    user = frappe.session.user
    t = perm.teacher_of(user)
    s = perm.student_of(user)
    return {
        "user": user,
        "is_teacher": bool(t),
        "is_student": bool(s),
        "teacher": t,
        "student": s,
        "is_admin": perm.is_admin(user),
    }


@frappe.whitelist()
def get_my_teacher_overview():
    """Dashboard giáo viên: chỉ lớp được phân công + buổi dạy hôm nay (§5, §9.1)."""
    from edu.education_erp import permissions as perm
    t = perm.teacher_of(frappe.session.user)
    if not t:
        frappe.throw("Tài khoản hiện tại không gắn với hồ sơ giáo viên.")
    cids = perm.teacher_class_ids(t)
    classes = frappe.get_list(
        "Class", filters={"name": ["in", cids]},
        fields=["name", "class_name", "status", "progress"],
    ) if cids else []
    sessions_today = frappe.get_list(
        "Class Session",
        filters={"class_id": ["in", cids], "session_date": nowdate()},
        fields=["name", "class_id", "start_time", "end_time", "lesson_topic", "session_status"],
        order_by="start_time asc",
    ) if cids else []
    return {"teacher": t, "classes": classes, "sessions_today": sessions_today}


@frappe.whitelist()
def get_my_student_overview():
    """Dashboard học viên: chỉ dữ liệu của bản thân (§6, §9.1, SEC-02)."""
    from edu.education_erp import permissions as perm
    s = perm.student_of(frappe.session.user)
    if not s:
        frappe.throw("Tài khoản hiện tại không gắn với hồ sơ học viên.")
    profile = frappe.db.get_value(
        "Student", s,
        ["full_name", "progress", "attendance_rate", "average_score", "health_status"],
        as_dict=True,
    )
    cids = perm.student_class_ids(s)
    homework = frappe.get_list(
        "Homework",
        filters={"class_id": ["in", cids], "status": "Published"},
        fields=["name", "title", "due_date", "class_id"],
        order_by="due_date asc",
    ) if cids else []
    invoices = frappe.get_list(
        "Fee Invoice",
        filters={"student": s, "docstatus": 1},
        fields=["name", "total_amount", "outstanding_amount", "status", "due_date"],
        order_by="due_date asc",
    )
    assessments = frappe.get_list(
        "Student Assessment",
        filters={"student": s},
        fields=["assessment_name", "assessment_type", "score", "max_score"],
        order_by="creation desc",
        limit_page_length=10,
    )
    return {"student": s, "profile": profile, "homework": homework, "invoices": invoices, "recent_assessments": assessments}


@frappe.whitelist()
def ai_chat(messages, temperature=0.7, max_tokens=1024, response_format=None, model=None):
    """Proxy gọi Groq (OpenAI-compatible) phía server để không lộ API key ra trình duyệt.

    Cấu hình khóa trong site_config.json: "groq_api_key": "gsk_...".
    Tùy chọn: "groq_model" để đổi model mặc định.
    Trả về nội dung text của câu trả lời (data.choices[0].message.content).
    """
    api_key = frappe.conf.get("groq_api_key")
    if not api_key:
        frappe.throw("Chưa cấu hình 'groq_api_key' trong site_config.json.")
    if not (frappe.has_permission("Student", "read") or frappe.has_permission("Class", "read")):
        frappe.throw("Bạn không có quyền sử dụng trợ lý AI.", frappe.PermissionError)

    if isinstance(messages, str):
        messages = json.loads(messages)
    if isinstance(response_format, str):
        try:
            response_format = json.loads(response_format)
        except (ValueError, TypeError):
            response_format = None

    payload = {
        "model": frappe.conf.get("groq_model") or DEFAULT_GROQ_MODEL,
        "messages": messages,
        "temperature": max(0.0, min(float(temperature), 1.0)),
    }
    if max_tokens:
        payload["max_tokens"] = min(int(max_tokens), 2048)
    if response_format:
        payload["response_format"] = response_format

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as e:
        frappe.throw(f"Không kết nối được tới dịch vụ AI: {e}")

    if resp.status_code != 200:
        frappe.log_error(resp.text[:1000], "Groq AI error")
        frappe.throw(f"Lỗi dịch vụ AI (HTTP {resp.status_code}).")

    data = resp.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
    if not content:
        frappe.throw("Phản hồi rỗng từ dịch vụ AI.")
    return content
