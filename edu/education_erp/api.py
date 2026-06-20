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
    "Class Session": {"lesson_topic", "classroom"},
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
        "student_status", "student_image",
    },
    "Student Appointment": {"lead", "appointment_date", "appointment_time", "purpose", "status"},
    "Student Assessment": {
        "student", "class_id", "program_enrollment", "class_session", "assessment_name",
        "assessment_type", "score", "max_score", "weight", "notes",
    },
    "Student Lead": {
        "lead_name", "phone", "email", "source", "status", "date_of_birth", "gender",
        "occupation", "guardian_name", "guardian_phone", "lost_reason", "lead_image",
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
        fields=["name", "full_name", "student_image", "progress", "average_score", "attendance_status", "health_status", "student_status", "date_of_birth", "gender", "email", "phone", "source", "occupation", "rating", "message_response", "creation"],
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
        fields=["name", "lead_name", "phone", "email", "source", "status", "creation", "date_of_birth", "gender", "occupation", "guardian_name", "guardian_phone", "lead_image", "student"],
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

def _ensure_student_for_lead(lead):
    """Tạo (hoặc tái dùng) hồ sơ Student cho một lead — idempotent.

    Nếu lead.student đã có thì trả về luôn (tránh tạo trùng khi lead đi qua
    Học thử rồi mới Nhập học). Ngược lại: tìm/tạo Guardian, tạo Student, gán
    lead.student và lưu lại. KHÔNG đổi lead.status (nhánh gọi tự quyết định).
    Trả về document Student.
    """
    if lead.get("student"):
        return frappe.get_doc("Student", lead.student)

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

    # Ghi nhớ Student trên lead để các bước sau không tạo trùng.
    lead.student = student.name
    lead.save()

    return student


@frappe.whitelist()
def convert_lead_to_student(lead_id):
    lead = _get_doc_checked("Student Lead", lead_id, "write")
    student = _ensure_student_for_lead(lead)

    # Update Lead status to "Enrolled"
    if lead.status != "Enrolled":
        lead.status = "Enrolled"
        lead.save()

    return {
        "student_id": student.name,
        "student_name": student.full_name
    }


def _create_lead_appointment(lead_id, appointment_date, purpose, appointment_time=None):
    """Tạo một Lịch hẹn (Student Appointment) gắn với lead. Trả về tên doc."""
    _require_create("Student Appointment")
    doc = frappe.get_doc({
        "doctype": "Student Appointment",
        "lead": lead_id,
        "appointment_date": appointment_date or nowdate(),
        "appointment_time": appointment_time or None,
        "purpose": purpose,
        "status": "Scheduled",
    })
    doc.insert()
    return doc.name


# Các stage hợp lệ để chuyển tới.
LEAD_STAGE_TARGETS = {"Consulting", "Testing", "Trial", "Enrolled", "Lost"}


def _lead_step_from_status(status):
    """Bước đang ghi nhận suy ra từ trạng thái hiện tại của lead."""
    if status == "Testing":
        return "Testing"
    if status == "Trial":
        return "Trial"
    return "Consulting"


def _apply_lead_target(lead, target, payload, created):
    """ONBOARDING khi lead BƯỚC VÀO một stage đích — set trạng thái + tạo bản ghi
    cần thiết. Dùng chung cho record_lead_outcome và advance_lead_stage.
    Mọi create đi qua _require_create; throw giữa chừng -> transaction rollback."""
    lead_id = lead.name
    if target == "Testing":
        if payload.get("appointment_date"):
            created["appointment"] = _create_lead_appointment(
                lead_id, payload.get("appointment_date"), "Test đầu vào", payload.get("appointment_time"),
            )
        lead.status = "Testing"
        lead.save()

    elif target == "Trial":
        if not payload.get("class_id"):
            frappe.throw("Cần chọn lớp để ghi danh học thử.")
        student = _ensure_student_for_lead(lead)
        created["student"] = student.name
        created["enrollment"] = create_enrollment(
            student=student.name,
            class_id=payload.get("class_id"),
            enrollment_date=payload.get("enrollment_date") or nowdate(),
            enrollment_type="Trial",
            list_price=payload.get("list_price"),
            submit=int(payload.get("submit") or 0),
        )
        lead.status = "Trial"
        lead.save()

    elif target == "Enrolled":
        if not payload.get("class_id"):
            frappe.throw("Cần chọn lớp để nhập học chính thức.")
        student = _ensure_student_for_lead(lead)
        created["student"] = student.name
        created["enrollment"] = create_enrollment(
            student=student.name,
            class_id=payload.get("class_id"),
            enrollment_date=payload.get("enrollment_date") or nowdate(),
            enrollment_type="Official",
            list_price=payload.get("list_price"),
            submit=1,
        )
        if lead.status != "Enrolled":
            lead.status = "Enrolled"
            lead.save()

    elif target == "Consulting":
        lead.status = "Consulting"
        lead.save()

    elif target == "Stay":
        # Giữ nguyên stage (vd học thử cần thêm thời gian) — chỉ ghi nhận, không onboard lại.
        pass

    elif target == "Lost":
        reason = payload.get("lost_reason") or lead.get("lost_reason")
        if not reason:
            frappe.throw("Lead thất bại cần có lý do.")
        lead.lost_reason = reason
        lead.status = "Lost"
        lead.save()

    else:
        frappe.throw(f"Trạng thái '{target}' không hợp lệ.")


@frappe.whitelist()
def record_lead_outcome(lead_id, payload=None):
    """Ghi nhận KẾT QUẢ bước hiện tại + TỰ ĐỘNG chuyển sang bước tiếp theo — MỘT transaction.

    payload (dict|JSON):
      current_step?   : Consulting | Testing | Trial (mặc định suy từ lead.status)
      next_action     : Testing | Trial | Enrolled | Consulting | Lost
      # dữ liệu bước hiện tại
      Consulting/Trial: {contact_date?, notes?, result?, next_follow_up?}
      Testing         : {test_date?, score, level?, recommended_course?, test_notes?}
      # dữ liệu bước sau (theo next_action)
      Trial/Enrolled  : {class_id, enrollment_date?, list_price?}
      Testing         : {appointment_date?, appointment_time?}
      Lost            : {lost_reason}
      appointment?    : tên Student Appointment -> đánh dấu Completed
    Trả về: {status, created:{...}}
    """
    payload = _parse_payload(payload)
    lead = _get_doc_checked("Student Lead", lead_id, "write")
    current_step = payload.get("current_step") or _lead_step_from_status(lead.status)
    next_action = payload.get("next_action")
    if not next_action:
        frappe.throw("Thiếu 'Bước tiếp theo'.")

    created = {}

    # 1) Ghi nhận bước hiện tại
    if current_step == "Testing":
        if payload.get("score") in (None, ""):
            frappe.throw("Cần nhập điểm test đầu vào.")
        created["placement_test"] = add_placement_test(
            lead_id,
            payload.get("test_date") or nowdate(),
            payload.get("score"),
            payload.get("recommended_course"),
            payload.get("level"),
            payload.get("test_notes"),
        )
    else:  # Consulting / Trial -> ghi nhật ký tư vấn (có kết quả đánh giá)
        if payload.get("notes") or payload.get("result") or payload.get("next_follow_up"):
            created["consultation_log"] = add_consultation_log(
                lead_id,
                payload.get("notes"),
                payload.get("contact_date") or nowdate(),
                payload.get("next_follow_up"),
                payload.get("result"),
            )
        # Có ngày theo dõi tiếp -> tạo Lịch hẹn để hiện trong trang Lịch hẹn.
        if payload.get("next_follow_up"):
            created["appointment"] = _create_lead_appointment(
                lead_id, payload.get("next_follow_up"),
                "Theo dõi / tư vấn", payload.get("appointment_time"),
            )

    # Đánh dấu lịch hẹn liên quan là Hoàn thành (nếu ghi từ lịch hẹn)
    if payload.get("appointment"):
        appt = _get_doc_checked("Student Appointment", payload.get("appointment"), "write")
        if appt.status == "Scheduled":
            appt.status = "Completed"
            appt.save()

    # 2) Tự động chuyển sang bước tiếp theo
    _apply_lead_target(lead, next_action, payload, created)

    return {"status": lead.status, "created": created}


@frappe.whitelist()
def advance_lead_stage(lead_id, to_status, payload=None):
    """Lối tắt chuyển thẳng một stage (kéo-thả). Ghi dữ liệu kèm nếu có rồi onboard."""
    payload = _parse_payload(payload)
    lead = _get_doc_checked("Student Lead", lead_id, "write")
    created = {}
    if to_status == "Consulting" and payload.get("notes"):
        created["consultation_log"] = add_consultation_log(
            lead_id, payload.get("notes"), payload.get("contact_date") or nowdate(),
            payload.get("next_follow_up"), payload.get("result"),
        )
    elif to_status == "Testing" and payload.get("score") not in (None, ""):
        created["placement_test"] = add_placement_test(
            lead_id, payload.get("test_date") or nowdate(), payload.get("score"),
            payload.get("recommended_course"), payload.get("level"), payload.get("test_notes"),
        )
    _apply_lead_target(lead, to_status, payload, created)
    return {"status": lead.status, "created": created}


@frappe.whitelist()
def attach_file_to_lead(file_url, lead_id):
    """Gắn một File đã tải lên vào hồ sơ lead (sau khi lead được tạo)."""
    _get_doc_checked("Student Lead", lead_id, "write")
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    file_doc.check_permission("write")
    file_doc.attached_to_doctype = "Student Lead"
    file_doc.attached_to_name = lead_id
    file_doc.save()
    return file_doc.name


@frappe.whitelist()
def get_appointments(lead_id):
    _get_doc_checked("Student Lead", lead_id, "read")
    return frappe.get_list(
        "Student Appointment",
        filters={"lead": lead_id},
        fields=["name", "appointment_date", "appointment_time", "purpose", "status", "creation"],
        order_by="appointment_date desc, creation desc",
    )


@frappe.whitelist()
def get_all_appointments(status=None):
    """Liệt kê toàn bộ Lịch hẹn (Student Appointment) kèm tên/SĐT lead."""
    if not frappe.has_permission("Student Appointment", "read"):
        frappe.throw("Bạn không có quyền xem lịch hẹn.", frappe.PermissionError)
    filters = {}
    if status:
        filters["status"] = status
    appts = frappe.get_list(
        "Student Appointment",
        filters=filters,
        fields=["name", "lead", "appointment_date", "appointment_time", "purpose", "status", "creation"],
        order_by="appointment_date desc, appointment_time desc",
    )
    lead_ids = list({a.lead for a in appts if a.lead})
    lead_map = {}
    if lead_ids:
        for l in frappe.get_all(
            "Student Lead", filters={"name": ["in", lead_ids]},
            fields=["name", "lead_name", "phone", "lead_image", "status"],
        ):
            lead_map[l.name] = l
    for a in appts:
        info = lead_map.get(a.lead) or {}
        a["lead_name"] = info.get("lead_name") or a.lead
        a["lead_phone"] = info.get("phone")
        a["lead_image"] = info.get("lead_image")
        a["lead_status"] = info.get("status")
    return appts


@frappe.whitelist()
def get_lead_timeline(lead_id):
    """Gộp Consultation Log + Placement Test + Student Appointment thành một dòng
    thời gian chuẩn hóa, sắp xếp giảm dần theo ngày."""
    _get_doc_checked("Student Lead", lead_id, "read")
    items = []

    for log in get_consultation_logs(lead_id):
        items.append({
            "kind": "consultation",
            "date": log.get("contact_date") or log.get("creation"),
            "title": "Ghi nhận tư vấn",
            "detail": log.get("notes"),
            "result": log.get("result"),
            "status": None,
            "next_follow_up": log.get("next_follow_up"),
            "name": log.get("name"),
            "creation": log.get("creation"),
        })

    for test in get_placement_tests(lead_id):
        detail = f"Điểm: {test.get('score')}"
        if test.get("level"):
            detail += f" · Trình độ: {test.get('level')}"
        if test.get("recommended_course"):
            detail += f" · Khóa gợi ý: {test.get('recommended_course')}"
        if test.get("notes"):
            detail += f"\n{test.get('notes')}"
        items.append({
            "kind": "placement",
            "date": test.get("test_date") or test.get("creation"),
            "title": "Test đầu vào",
            "detail": detail,
            "result": test.get("level"),
            "status": test.get("status"),
            "name": test.get("name"),
            "creation": test.get("creation"),
        })

    for appt in get_appointments(lead_id):
        when = appt.get("appointment_date")
        items.append({
            "kind": "appointment",
            "date": when or appt.get("creation"),
            "title": appt.get("purpose") or "Lịch hẹn",
            "detail": (str(appt.get("appointment_time")) if appt.get("appointment_time") else None),
            "status": appt.get("status"),
            "name": appt.get("name"),
            "creation": appt.get("creation"),
        })

    items.sort(key=lambda x: (str(x.get("date") or ""), str(x.get("creation") or "")), reverse=True)
    return items


# ===================================================================
# Xuất / Nhập Excel + form mẫu cho Lead và Học viên
# ===================================================================

# (fieldname, nhãn cột) — đây cũng là cột của form mẫu & thứ tự đọc khi nhập.
LEAD_IMPORT_FIELDS = [
    ("lead_name", "Họ tên *"),
    ("phone", "Điện thoại"),
    ("email", "Email"),
    ("source", "Nguồn (Website/Facebook/Hotline/Word of Mouth/Other)"),
    ("date_of_birth", "Ngày sinh (YYYY-MM-DD)"),
    ("gender", "Giới tính (Nam/Nữ/Khác)"),
    ("occupation", "Nghề nghiệp"),
    ("guardian_name", "Người giám hộ"),
    ("guardian_phone", "SĐT người giám hộ"),
]

STUDENT_IMPORT_FIELDS = [
    ("full_name", "Họ tên *"),
    ("phone", "Điện thoại"),
    ("email", "Email"),
    ("date_of_birth", "Ngày sinh (YYYY-MM-DD)"),
    ("gender", "Giới tính (Nam/Nữ/Khác)"),
    ("source", "Nguồn"),
    ("occupation", "Nghề nghiệp"),
    ("student_status", "Trạng thái (Mới nhập học/Đang học/Bảo lưu/Đã tốt nghiệp/Nghỉ học)"),
    ("health_status", "Tình trạng học tập (Đang học đều/Cần theo dõi/Cảnh báo/Khẩn cấp/Ngừng học)"),
]


def _send_xlsx(rows, filename):
    """Trả file xlsx về trình duyệt (download)."""
    from frappe.utils.xlsxutils import make_xlsx

    xlsx = make_xlsx(rows, "Sheet1")
    frappe.response["filename"] = filename
    frappe.response["filecontent"] = xlsx.getvalue()
    frappe.response["type"] = "binary"


def _read_xlsx_rows(file_url):
    from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file

    rows = read_xlsx_file_from_attached_file(file_url=file_url)
    return rows or []


def _import_rows(doctype, fields, file_url):
    """Đọc xlsx (bỏ dòng tiêu đề) và tạo bản ghi theo thứ tự cột của form mẫu.
    Mỗi dòng dùng một savepoint riêng: dòng lỗi không làm hỏng cả batch."""
    _require_create(doctype)
    rows = _read_xlsx_rows(file_url)
    keys = [f for f, _ in fields]
    name_key = keys[0]
    created, errors = 0, []

    for line, row in enumerate(rows[1:], start=2):  # bỏ dòng tiêu đề
        values = {}
        for idx, key in enumerate(keys):
            cell = row[idx] if idx < len(row) else None
            if cell is None:
                continue
            text = str(cell).strip()
            if text:
                values[key] = text
        if not values.get(name_key):
            continue  # bỏ dòng trống

        sp = f"imp_{line}"
        frappe.db.savepoint(sp)
        try:
            frappe.get_doc({"doctype": doctype, **values}).insert()
            created += 1
        except Exception as e:
            frappe.db.rollback(save_point=sp)
            errors.append(f"Dòng {line}: {str(e)}")

    return {"created": created, "errors": errors, "total": max(len(rows) - 1, 0)}


@frappe.whitelist()
def download_lead_template():
    _send_xlsx([[label for _, label in LEAD_IMPORT_FIELDS]], "mau-nhap-lead.xlsx")


@frappe.whitelist()
def export_leads():
    if not frappe.has_permission("Student Lead", "read"):
        frappe.throw("Bạn không có quyền xem danh sách lead.", frappe.PermissionError)
    cols = [("name", "Mã lead")] + LEAD_IMPORT_FIELDS + [("status", "Trạng thái"), ("creation", "Ngày tạo")]
    header = [label for _, label in cols]
    rows = [header]
    for l in get_leads():
        rows.append([l.get(f) for f, _ in cols])
    _send_xlsx(rows, "danh-sach-lead.xlsx")


@frappe.whitelist()
def import_leads(file_url):
    return _import_rows("Student Lead", LEAD_IMPORT_FIELDS, file_url)


@frappe.whitelist()
def download_student_template():
    _send_xlsx([[label for _, label in STUDENT_IMPORT_FIELDS]], "mau-nhap-hoc-vien.xlsx")


@frappe.whitelist()
def export_students():
    if not frappe.has_permission("Student", "read"):
        frappe.throw("Bạn không có quyền xem danh sách học viên.", frappe.PermissionError)
    cols = [("name", "Mã học viên")] + STUDENT_IMPORT_FIELDS + [("creation", "Ngày tạo")]
    header = [label for _, label in cols]
    rows = [header]
    for s in get_students():
        rows.append([s.get(f) for f, _ in cols])
    _send_xlsx(rows, "danh-sach-hoc-vien.xlsx")


@frappe.whitelist()
def import_students(file_url):
    return _import_rows("Student", STUDENT_IMPORT_FIELDS, file_url)


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
        fields=[
            "name", "class_name", "course", "teacher", "start_date", "status",
            "progress", "max_capacity", "total_sessions", "standard_fee",
        ],
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

    student_ids = list({e.student for e in enrollments if e.student})
    student_map = {}
    if student_ids:
        for s in frappe.get_all(
            "Student", filters={"name": ["in", student_ids]},
            fields=["name", "full_name", "student_image"],
        ):
            student_map[s.name] = s

    rows = []
    for e in enrollments:
        ex = by_enr.get(e.name)
        s = student_map.get(e.student) or {}
        rows.append({
            "program_enrollment": e.name,
            "student": e.student,
            "student_name": s.get("full_name") or e.student,
            "student_image": s.get("student_image"),
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
        fields=["name", "contact_date", "result", "notes", "next_follow_up", "creation"],
        order_by="contact_date desc, creation desc"
    )

@frappe.whitelist()
def add_consultation_log(lead_id, notes, contact_date, next_follow_up=None, result=None):
    _get_doc_checked("Student Lead", lead_id, "write")
    _require_create("Consultation Log")
    doc = frappe.get_doc({
        "doctype": "Consultation Log",
        "lead": lead_id,
        "contact_date": contact_date,
        "result": result or None,
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
        fields=["name", "test_date", "score", "level", "recommended_course", "notes", "status", "creation"],
        order_by="test_date desc, creation desc"
    )

@frappe.whitelist()
def add_placement_test(lead_id, test_date, score, recommended_course=None, level=None, notes=None):
    _get_doc_checked("Student Lead", lead_id, "write")
    _require_create("Placement Test")
    doc = frappe.get_doc({
        "doctype": "Placement Test",
        "lead": lead_id,
        "test_date": test_date,
        "score": float(score),
        "level": level or None,
        "recommended_course": recommended_course or None,
        "notes": notes or None,
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
def get_refunds(status=None):
    """Liệt kê yêu cầu hoàn phí (Fee Refund) kèm tên học viên — cho màn Tài chính."""
    if not frappe.has_permission("Fee Refund", "read"):
        frappe.throw("Bạn không có quyền xem hoàn phí.", frappe.PermissionError)
    filters = {}
    if status:
        filters["status"] = status
    rows = frappe.get_list(
        "Fee Refund", filters=filters,
        fields=["name", "student", "invoice_reference", "refund_amount", "refund_date", "reason", "status", "docstatus", "creation"],
        order_by="creation desc",
    )
    for r in rows:
        r["student_name"] = _student_name(r.student) if r.get("student") else None
    return rows


@frappe.whitelist()
def approve_fee_refund(refund):
    """Duyệt hoàn phí: Fee Refund Draft -> Completed (submit)."""
    doc = _get_doc_checked("Fee Refund", refund, "submit")
    if doc.docstatus != 0:
        frappe.throw("Yêu cầu hoàn phí đã được xử lý.")
    doc.status = "Completed"
    doc.submit()
    return {"name": doc.name, "status": doc.status, "docstatus": doc.docstatus}


@frappe.whitelist()
def reject_fee_refund(refund, reason=None):
    """Từ chối hoàn phí: đánh dấu Cancelled (giữ bản ghi để truy vết)."""
    doc = _get_doc_checked("Fee Refund", refund, "write")
    if doc.docstatus != 0:
        frappe.throw("Yêu cầu hoàn phí đã được xử lý.")
    doc.status = "Cancelled"
    if reason:
        doc.reason = (doc.reason + " | " if doc.get("reason") else "") + f"Từ chối: {reason}"
    doc.save()
    return {"name": doc.name, "status": doc.status, "docstatus": doc.docstatus}


SESSION_STATUS_TARGETS = {"Scheduled", "Cancelled"}


@frappe.whitelist()
def set_session_status(class_session, status, reason=None):
    """Hủy/khôi phục lịch một buổi học (có kiểm soát). Không cho đụng buổi đã Completed/Locked."""
    if status not in SESSION_STATUS_TARGETS:
        frappe.throw(f"Trạng thái buổi '{status}' không hợp lệ.")
    doc = _get_doc_checked("Class Session", class_session, "write")
    if doc.session_status in ("Completed", "Locked"):
        frappe.throw(f"Buổi học đã {doc.session_status}, không thể đổi trạng thái.")
    doc.session_status = status
    if reason and doc.meta.has_field("lesson_topic") and not doc.get("lesson_topic"):
        doc.lesson_topic = reason
    doc.save()
    return {"name": doc.name, "session_status": doc.session_status}


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
def get_my_teacher_overview(as_teacher=None):
    """Dashboard giáo viên: chỉ lớp được phân công + buổi dạy hôm nay (§5, §9.1).
    Admin/System Manager có thể xem thử cổng (mặc định GV đầu tiên hoặc as_teacher)."""
    from edu.education_erp import permissions as perm
    admin = perm.is_admin(frappe.session.user)
    t = perm.teacher_of(frappe.session.user)
    if not t and admin:
        t = as_teacher or frappe.db.get_value("Teacher", {}, "name")
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
    _attach_class_names(sessions_today)
    teacher_name = frappe.db.get_value("Teacher", t, "teacher_name") or t
    return {"teacher": t, "teacher_name": teacher_name, "classes": classes,
            "sessions_today": sessions_today, "is_admin": admin}


@frappe.whitelist()
def get_my_student_overview(as_student=None):
    """Dashboard học viên: chỉ dữ liệu của bản thân (§6, §9.1, SEC-02).
    Admin/System Manager có thể xem thử cổng (mặc định HV đầu tiên hoặc as_student)."""
    from edu.education_erp import permissions as perm
    admin = perm.is_admin(frappe.session.user)
    s = perm.student_of(frappe.session.user)
    if not s and admin:
        s = as_student or frappe.db.get_value("Student", {}, "name")
    if not s:
        frappe.throw("Tài khoản hiện tại không gắn với hồ sơ học viên.")
    profile = frappe.db.get_value(
        "Student", s,
        ["full_name", "student_image", "progress", "attendance_rate", "average_score", "health_status"],
        as_dict=True,
    )
    cids = perm.student_class_ids(s)
    enrollments = frappe.get_list(
        "Program Enrollment",
        filters={"student": s, "docstatus": 1},
        fields=["name", "class_id", "enrollment_status", "enrollment_date", "net_fee"],
        order_by="creation desc",
    )
    enrollment_by_class = {e.class_id: e.name for e in enrollments if e.class_id}
    homework = frappe.get_list(
        "Homework",
        filters={"class_id": ["in", cids], "status": "Published"},
        fields=[
            "name", "title", "due_date", "class_id", "class_session", "target",
            "description", "materials", "assigned_date",
        ],
        order_by="due_date asc",
    ) if cids else []
    homework_names = [h.name for h in homework]
    submissions = frappe.get_list(
        "Homework Submission",
        filters={"student": s, "homework": ["in", homework_names]},
        fields=["name", "homework", "submission_date", "status", "content", "grade", "feedback"],
        order_by="creation desc",
    ) if homework_names else []
    submission_by_homework = {x.homework: x for x in submissions}
    for h in homework:
        h["program_enrollment"] = enrollment_by_class.get(h.class_id)
        h["submission"] = submission_by_homework.get(h.name)
    _attach_class_names(homework)
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
    sessions = frappe.get_list(
        "Class Session",
        filters={"class_id": ["in", cids], "session_date": [">=", nowdate()]},
        fields=["name", "class_id", "session_date", "start_time", "end_time", "lesson_topic", "session_status"],
        order_by="session_date asc, start_time asc",
        limit_page_length=12,
    ) if cids else []
    _attach_class_names(sessions)
    materials = frappe.get_list(
        "Learning Material",
        filters={"class_id": ["in", cids], "is_public": 1},
        fields=["name", "title", "material_type", "class_id", "course", "url", "description"],
        order_by="creation desc",
        limit_page_length=12,
    ) if cids else []
    return {
        "student": s,
        "is_admin": admin,
        "profile": profile,
        "enrollments": enrollments,
        "homework": homework,
        "invoices": invoices,
        "recent_assessments": assessments,
        "sessions": sessions,
        "materials": materials,
    }


@frappe.whitelist()
def submit_my_homework(homework, content=None):
    """Student portal submit/update homework for the current session user."""
    from edu.education_erp import permissions as perm
    s = perm.student_of(frappe.session.user)
    if not s:
        frappe.throw("Tai khoan hien tai khong gan voi ho so hoc vien.")

    hw = _get_doc_checked("Homework", homework, "read")
    if hw.status != "Published":
        frappe.throw("Chi nop duoc bai tap da publish.")

    class_ids = perm.student_class_ids(s)
    allowed = (hw.target == "Whole Class" and hw.class_id in class_ids) or (
        hw.target == "Individual" and hw.student == s
    )
    if not allowed:
        frappe.throw("Bai tap khong thuoc hoc vien hien tai.", frappe.PermissionError)

    program_enrollment = frappe.db.get_value(
        "Program Enrollment",
        {"student": s, "class_id": hw.class_id, "docstatus": 1},
        "name",
    )
    if not program_enrollment:
        frappe.throw("Khong tim thay dang ky hoc cho lop cua bai tap.")

    existing = frappe.db.exists(
        "Homework Submission",
        {"homework": homework, "program_enrollment": program_enrollment},
    )
    if existing:
        doc = frappe.get_doc("Homework Submission", existing)
        doc.content = content
        doc.submission_date = nowdate()
        doc.status = "Submitted"
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "Homework Submission",
            "homework": homework,
            "program_enrollment": program_enrollment,
            "student": s,
            "submission_date": nowdate(),
            "status": "Submitted",
            "content": content,
        })
        doc.insert(ignore_permissions=True)
    return {"name": doc.name, "status": doc.status, "submission_date": doc.submission_date}


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
    if not (
        frappe.has_permission("Student", "read")
        or frappe.has_permission("Class", "read")
        or frappe.has_permission("Student Lead", "read")
    ):
        frappe.throw("Bạn không có quyền sử dụng trợ lý AI.", frappe.PermissionError)

    if isinstance(messages, str):
        messages = json.loads(messages)
    if isinstance(response_format, str):
        try:
            response_format = json.loads(response_format)
        except (ValueError, TypeError):
            response_format = None

    payload = {
        "model": model or frappe.conf.get("groq_model") or DEFAULT_GROQ_MODEL,
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


LEAD_PARSE_SYSTEM_PROMPT = (
    "Bạn là trợ lý AI của IKE Ohashi. Hãy phân tích thông tin của học viên mới từ "
    "tài liệu (ảnh chụp/giấy tờ/tin nhắn) và trích xuất thành một đối tượng JSON chính "
    "xác có cấu trúc sau:\n"
    "{\n"
    '  "lead_name": "Họ và tên",\n'
    '  "phone": "Số điện thoại",\n'
    '  "email": "Địa chỉ email",\n'
    '  "source": "Chọn một trong: Website, Facebook, Hotline, Word of Mouth, Other",\n'
    '  "date_of_birth": "Ngày sinh định dạng YYYY-MM-DD",\n'
    '  "gender": "Chọn một trong: Nam, Nữ, Khác",\n'
    '  "occupation": "Nghề nghiệp",\n'
    '  "guardian_name": "Tên người giám hộ",\n'
    '  "guardian_phone": "Số điện thoại người giám hộ"\n'
    "}\n"
    'Nếu không tìm thấy trường nào, đặt giá trị là chuỗi rỗng "". Chỉ trả về JSON thô, '
    "không thêm markdown hay giải thích."
)

LEAD_PARSE_FIELDS = {
    "lead_name", "phone", "email", "source", "date_of_birth",
    "gender", "occupation", "guardian_name", "guardian_phone",
}

_IMAGE_MIME = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "webp": "image/webp", "gif": "image/gif",
}


def _extract_json(text):
    """Bóc JSON object đầu tiên từ phản hồi AI (kèm rào ```json nếu có)."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if cleaned.count("```") >= 2 else cleaned.strip("`")
        if cleaned.lstrip().lower().startswith("json"):
            cleaned = cleaned.lstrip()[4:]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    try:
        return json.loads(cleaned)
    except (ValueError, TypeError):
        frappe.throw("AI trả về kết quả không đúng định dạng JSON.")


@frappe.whitelist()
def ai_parse_lead_document(file_url):
    """Đọc một tài liệu đã tải lên (ảnh hoặc PDF) và trích xuất thông tin lead.

    - Ảnh (png/jpg/webp...): gửi tới model vision của Groq (cấu hình
      'groq_vision_model' trong site_config.json) dưới dạng base64 data URI.
    - PDF: trích text phía server bằng pdfplumber rồi đưa qua model văn bản.
    Trả về dict các field lead (lead_name, phone, email, ...).
    """
    import base64

    file_doc = frappe.get_doc("File", {"file_url": file_url})
    file_doc.check_permission("read")
    content = file_doc.get_content()
    if isinstance(content, str):
        content = content.encode("utf-8", "ignore")

    ext = (file_doc.file_name or file_url or "").rsplit(".", 1)[-1].lower()

    if ext in _IMAGE_MIME:
        vision_model = frappe.conf.get("groq_vision_model")
        if not vision_model:
            frappe.throw(
                "Chưa cấu hình 'groq_vision_model' trong site_config.json để đọc ảnh."
            )
        data_uri = f"data:{_IMAGE_MIME[ext]};base64,{base64.b64encode(content).decode()}"
        messages = [
            {"role": "system", "content": LEAD_PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": "Trích xuất thông tin học viên từ tài liệu này thành JSON."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]},
        ]
        raw = ai_chat(messages=messages, temperature=0.2, max_tokens=1024, model=vision_model)

    elif ext == "pdf":
        try:
            import io
            import pdfplumber
        except ImportError:
            frappe.throw("Chưa cài đặt 'pdfplumber' trên server để đọc PDF.")
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        if not text.strip():
            frappe.throw(
                "Không trích được văn bản từ PDF (có thể là PDF scan/ảnh). "
                "Hãy tải lên ảnh chụp thay thế."
            )
        messages = [
            {"role": "system", "content": LEAD_PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": text.strip()[:8000]},
        ]
        raw = ai_chat(messages=messages, temperature=0.2, max_tokens=1024)

    else:
        frappe.throw(f"Định dạng '{ext}' không được hỗ trợ. Hãy tải ảnh hoặc PDF.")

    parsed = _extract_json(raw)
    return {k: v for k, v in parsed.items() if k in LEAD_PARSE_FIELDS and v}


# ===================================================================
# READ APIs cho UI Sakura (Giai đoạn UI) — chỉ đọc, đi qua permission
# query của từng DocType, KHÔNG dùng ignore_permissions.
# ===================================================================

def _student_name(student):
    return frappe.db.get_value("Student", student, "full_name") or student


def _class_name(class_id):
    return frappe.db.get_value("Class", class_id, "class_name") or class_id


def _attach_class_names(rows, field="class_id", out="class_name"):
    """Gắn tên lớp (class_name) cho danh sách có field link Class -> hiển thị tên thay vì mã."""
    ids = list({r.get(field) for r in rows if r.get(field)})
    if ids:
        m = {c.name: c.class_name for c in frappe.get_all(
            "Class", filters={"name": ["in", ids]}, fields=["name", "class_name"])}
        for r in rows:
            r[out] = m.get(r.get(field)) or r.get(field)
    return rows


# ---------------------------------------------------------------------------
# Quản lý tài khoản đăng nhập (User) cho HV/GV
# ---------------------------------------------------------------------------
MANAGED_ROLES = {"Student", "Teacher", "Academic Manager"}


def _require_system_manager():
    if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
        frappe.throw("Chỉ quản trị viên mới được thao tác tài khoản.", frappe.PermissionError)


def _ensure_role(role):
    if not frappe.db.exists("Role", role):
        frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
            ignore_permissions=True)


def _split_name(full_name, email):
    parts = (full_name or email or "").split()
    if len(parts) > 1:
        return " ".join(parts[:-1]), parts[-1]
    return (full_name or email or ""), ""


def _create_login_user(email, full_name, role, send_welcome=True):
    """Tạo User mới (System User) + role, gửi welcome email (link đặt mật khẩu) nếu cần."""
    _ensure_role(role)
    first, last = _split_name(full_name, email)
    doc = frappe.get_doc({
        "doctype": "User", "email": email, "first_name": first, "last_name": last,
        "enabled": 1, "user_type": "System User", "send_welcome_email": 1 if send_welcome else 0,
        "roles": [{"role": role}],
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def _provision_user_for(profile_doctype, profile_name, full_name, email, role):
    """Hook tạo HV/GV -> tự tạo tài khoản + gửi mail. Không bao giờ throw (tránh rollback hồ sơ)."""
    try:
        if frappe.flags.in_install or frappe.flags.in_import or frappe.flags.in_patch:
            return None
        if not email:
            return None
        if not frappe.db.get_single_value("Education Settings", "auto_create_login"):
            return None
        if frappe.db.get_value(profile_doctype, profile_name, "user"):
            return None  # đã link sẵn
        user = frappe.db.get_value("User", {"email": email}, "name")
        if not user:
            user = _create_login_user(email, full_name, role, send_welcome=True)
        else:
            u = frappe.get_doc("User", user)
            if role not in [r.role for r in u.roles]:
                _ensure_role(role)
                u.append("roles", {"role": role})
                u.save(ignore_permissions=True)
        frappe.db.set_value(profile_doctype, profile_name, "user", user)
        return user
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auto-provision login user failed")
        return None


@frappe.whitelist()
def list_users(search=None):
    _require_system_manager()
    cond = {"name": ["not in", ["Guest", "Administrator"]]}
    kw = dict(filters=cond, fields=["name", "email", "full_name", "enabled"],
              order_by="creation desc", limit_page_length=300)
    if search:
        kw["or_filters"] = {"email": ["like", f"%{search}%"], "full_name": ["like", f"%{search}%"]}
    users = frappe.get_all("User", **kw)
    names = [u.name for u in users]
    roles_map = {}
    stu, tea = {}, {}
    if names:
        for r in frappe.get_all("Has Role", filters={"parent": ["in", names], "parenttype": "User"},
                                fields=["parent", "role"]):
            roles_map.setdefault(r.parent, []).append(r.role)
        stu = {s.user: s.name for s in frappe.get_all(
            "Student", filters={"user": ["in", names]}, fields=["name", "user"])}
        tea = {t.user: t.name for t in frappe.get_all(
            "Teacher", filters={"user": ["in", names]}, fields=["name", "user"])}
    for u in users:
        u["roles"] = roles_map.get(u.name, [])
        u["student"] = stu.get(u.name)
        u["teacher"] = tea.get(u.name)
    return users


@frappe.whitelist()
def create_user(email, full_name, role="Student", link_student=None, link_teacher=None, send_welcome=1):
    _require_system_manager()
    if frappe.db.exists("User", email):
        frappe.throw("Email này đã có tài khoản.")
    user = _create_login_user(email, full_name, role, send_welcome=int(send_welcome or 0) == 1)
    if link_student:
        frappe.db.set_value("Student", link_student, "user", user)
    if link_teacher:
        frappe.db.set_value("Teacher", link_teacher, "user", user)
    return user


@frappe.whitelist()
def set_user_enabled(user, enabled):
    _require_system_manager()
    if user in ("Administrator", "Guest"):
        frappe.throw("Không thể đổi tài khoản hệ thống.")
    frappe.db.set_value("User", user, "enabled", int(enabled))
    return {"ok": True}


@frappe.whitelist()
def set_user_role(user, role):
    _require_system_manager()
    if user in ("Administrator", "Guest"):
        frappe.throw("Không thể đổi tài khoản hệ thống.")
    _ensure_role(role)
    u = frappe.get_doc("User", user)
    u.set("roles", [r for r in u.roles if r.role not in MANAGED_ROLES])
    u.append("roles", {"role": role})
    u.save(ignore_permissions=True)
    return {"ok": True}


@frappe.whitelist()
def reset_user_password(user):
    _require_system_manager()
    if user in ("Administrator", "Guest"):
        frappe.throw("Không thao tác trên tài khoản hệ thống.")
    frappe.get_doc("User", user).reset_password(send_email=True)
    return {"ok": True}


@frappe.whitelist()
def change_my_password(old_password, new_password):
    from frappe.utils.password import check_password, update_password
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Chưa đăng nhập.")
    if not new_password or len(new_password) < 6:
        frappe.throw("Mật khẩu mới tối thiểu 6 ký tự.")
    try:
        check_password(user, old_password)
    except Exception:
        frappe.throw("Mật khẩu hiện tại không đúng.")
    update_password(user, new_password)
    return {"ok": True}


@frappe.whitelist()
def get_dashboard_overview():
    """Tổng hợp dữ liệu Dashboard admin (§11). Gộp từ các list đã có quyền."""
    today = getdate(nowdate())

    active_students = frappe.db.count("Student", {"student_status": "Đang học"})
    total_students = frappe.db.count("Student")
    new_this_month = frappe.db.count(
        "Student", {"creation": [">=", today.replace(day=1)]}
    )
    ongoing_classes = frappe.db.count("Class", {"status": "Ongoing"})
    upcoming_classes = frappe.db.count("Class", {"status": "Upcoming"})

    active_rates = frappe.get_list(
        "Student", filters={"student_status": "Đang học"}, fields=["attendance_rate"]
    )
    avg_att = (
        round(sum(flt(r.attendance_rate) for r in active_rates) / len(active_rates))
        if active_rates else 0
    )

    invoices = frappe.get_list(
        "Fee Invoice", filters={"docstatus": 1},
        fields=["name", "student", "outstanding_amount", "due_date"],
    )
    outstanding = sum(flt(i.outstanding_amount) for i in invoices)
    overdue = [
        i for i in invoices
        if flt(i.outstanding_amount) > 0 and i.due_date and getdate(i.due_date) < today
    ]

    sessions_today = frappe.get_list(
        "Class Session", filters={"session_date": nowdate()},
        fields=["name", "class_id", "start_time", "end_time", "lesson_topic",
                "teacher", "classroom", "session_status"],
        order_by="start_time asc",
    )
    _attach_class_names(sessions_today)

    classes = frappe.get_list(
        "Class", filters={"status": ["in", ["Ongoing", "Upcoming"]]},
        fields=["name", "class_name", "progress", "status", "max_capacity"],
        order_by="modified desc", limit_page_length=6,
    )
    class_progress = [
        {"name": c.class_name or c.name, "pct": flt(c.progress)} for c in classes
    ]

    # Cảnh báo cần xử lý
    alerts = []
    for i in overdue[:4]:
        alerts.append({
            "title": f"{_student_name(i.student)} · học phí quá hạn",
            "detail": f"{i.name} · {frappe.utils.fmt_money(flt(i.outstanding_amount))}",
            "level": "danger",
        })
    weak = frappe.get_list(
        "Student",
        filters={"student_status": "Đang học", "health_status": ["in", ["Cảnh báo", "Khẩn cấp"]]},
        fields=["full_name", "health_status", "attendance_rate"], limit_page_length=4,
    )
    for w in weak:
        alerts.append({
            "title": f"{w.full_name} · {w.health_status}",
            "detail": f"Chuyên cần {round(flt(w.attendance_rate))}%",
            "level": "warning" if w.health_status == "Cảnh báo" else "danger",
        })

    # Hoạt động gần đây: phiếu thu + đăng ký mới nhất
    activity = []
    for p in frappe.get_list("Fee Payment", filters={"docstatus": 1},
                             fields=["student", "amount", "creation"],
                             order_by="creation desc", limit_page_length=3):
        activity.append({
            "text": f"Thu học phí {_student_name(p.student)} · {frappe.utils.fmt_money(flt(p.amount))}",
            "time": p.creation, "dot": "#3f9b6e",
        })
    for e in frappe.get_list("Program Enrollment", filters={"docstatus": 1},
                             fields=["student", "class_id", "creation"],
                             order_by="creation desc", limit_page_length=3):
        activity.append({
            "text": f"Đăng ký {_student_name(e.student)} vào {_class_name(e.class_id)}",
            "time": e.creation, "dot": "#9b6fc4",
        })
    activity.sort(key=lambda a: a["time"], reverse=True)

    return {
        "tiles": {
            "active_students": active_students,
            "total_students": total_students,
            "new_this_month": new_this_month,
            "ongoing_classes": ongoing_classes,
            "upcoming_classes": upcoming_classes,
            "avg_attendance": avg_att,
            "outstanding": outstanding,
            "overdue_count": len(overdue),
        },
        "sessions_today": sessions_today,
        "class_progress": class_progress,
        "alerts": alerts,
        "activity": activity[:6],
    }


@frappe.whitelist()
def get_student_profile(student):
    """Hồ sơ học viên đầy đủ cho trang chi tiết (6 tab)."""
    _get_doc_checked("Student", student, "read")
    profile = frappe.db.get_value(
        "Student", student,
        ["name", "full_name", "student_image", "student_status", "health_status", "date_of_birth",
         "gender", "email", "phone", "source", "occupation", "progress",
         "attendance_rate", "average_score", "guardian"],
        as_dict=True,
    )
    guardian = None
    if profile and profile.guardian:
        guardian = frappe.db.get_value(
            "Guardian", profile.guardian, ["guardian_name", "phone"], as_dict=True
        )

    enrollments = frappe.get_list(
        "Program Enrollment", filters={"student": student},
        fields=["name", "class_id", "enrollment_type", "enrollment_status",
                "enrollment_date", "list_price", "net_fee", "creation"],
        order_by="creation desc",
    )
    _attach_class_names(enrollments)
    attendance = frappe.get_list(
        "Student Attendance", filters={"student": student},
        fields=["class_session", "attendance_date", "status", "attendance_type", "minutes_late"],
        order_by="attendance_date desc", limit_page_length=12,
    )
    assessments = frappe.get_list(
        "Student Assessment", filters={"student": student},
        fields=["assessment_name", "assessment_type", "class_session", "score",
                "max_score", "weight", "notes"],
        order_by="creation desc", limit_page_length=20,
    )
    invoices = frappe.get_list(
        "Fee Invoice", filters={"student": student, "docstatus": 1},
        fields=["name", "total_amount", "outstanding_amount", "status", "due_date", "posting_date"],
        order_by="due_date asc",
    )
    total = sum(flt(i.total_amount) for i in invoices)
    outstanding = sum(flt(i.outstanding_amount) for i in invoices)
    return {
        "profile": profile,
        "guardian": guardian,
        "enrollments": enrollments,
        "attendance": attendance,
        "assessments": assessments,
        "invoices": invoices,
        "fees": {"total": total, "paid": total - outstanding, "outstanding": outstanding},
    }


@frappe.whitelist()
def get_class_roster(class_id):
    """Danh sách học viên của lớp kèm chuyên cần/điểm TB/trạng thái."""
    _get_doc_checked("Class", class_id, "read")
    enrollments = frappe.get_list(
        "Program Enrollment",
        filters={"class_id": class_id, "docstatus": 1,
                 "enrollment_status": ["in", ["Active", "Deferred"]]},
        fields=["name", "student", "enrollment_status", "enrollment_date", "net_fee"],
    )
    rows = []
    for e in enrollments:
        s = frappe.db.get_value(
            "Student", e.student,
            ["full_name", "student_image", "attendance_rate", "average_score", "health_status"],
            as_dict=True,
        ) or frappe._dict()
        invoices = frappe.get_list(
            "Fee Invoice",
            filters={"student": e.student, "program_enrollment": e.name, "docstatus": 1},
            fields=["total_amount", "outstanding_amount"],
        )
        invoice_total = sum(flt(i.total_amount) for i in invoices)
        outstanding = sum(flt(i.outstanding_amount) for i in invoices)
        rows.append({
            "enrollment": e.name,
            "student": e.student,
            "name": s.get("full_name") or e.student,
            "student_image": s.get("student_image"),
            "attendance_rate": flt(s.get("attendance_rate")),
            "average_score": s.get("average_score"),
            "health_status": s.get("health_status"),
            "enrollment_status": e.enrollment_status,
            "enrollment_date": e.enrollment_date,
            "net_fee": flt(e.net_fee),
            "invoice_total": invoice_total,
            "paid_amount": max(0, invoice_total - outstanding),
            "outstanding_amount": outstanding,
        })
    return rows


@frappe.whitelist()
def get_sessions_by_range(from_date, to_date):
    """Buổi học trong khoảng ngày (cho lịch tuần/tháng)."""
    sessions = frappe.get_list(
        "Class Session",
        filters={"session_date": ["between", [from_date, to_date]]},
        fields=["name", "class_id", "session_date", "start_time", "end_time",
                "lesson_topic", "classroom", "teacher", "session_status"],
        order_by="session_date asc, start_time asc",
    )
    names = {}
    for cid in {s.class_id for s in sessions if s.class_id}:
        names[cid] = frappe.db.get_value("Class", cid, "class_name") or cid
    for s in sessions:
        s["class_name"] = names.get(s.class_id, s.class_id)
    return sessions


@frappe.whitelist()
def get_invoices(status=None):
    """Danh sách hóa đơn đã submit (kèm tên học viên) cho trang Tài chính."""
    filters = {"docstatus": 1}
    if status and status not in ("all", "Tất cả"):
        filters["status"] = status
    invoices = frappe.get_list(
        "Fee Invoice", filters=filters,
        fields=["name", "student", "program_enrollment", "total_amount",
                "outstanding_amount", "status", "due_date", "posting_date"],
        order_by="posting_date desc",
    )
    for i in invoices:
        i["student_name"] = _student_name(i.student)
    return invoices


@frappe.whitelist()
def get_invoice_detail(invoice):
    """Chi tiết một hóa đơn + lịch sử phiếu thu đã phân bổ."""
    inv = _get_doc_checked("Fee Invoice", invoice, "read")
    refs = frappe.get_all(
        "Fee Payment Reference", filters={"invoice": invoice},
        fields=["parent", "allocated_amount"],
    )
    pays = []
    for r in refs:
        p = frappe.db.get_value(
            "Fee Payment", r.parent,
            ["payment_date", "payment_method", "docstatus"], as_dict=True,
        )
        if p and p.docstatus == 1:
            pays.append({
                "date": p.payment_date, "amount": flt(r.allocated_amount),
                "method": p.payment_method,
            })
    pays.sort(key=lambda x: x["date"] or "")
    return {
        "name": inv.name,
        "student": inv.student,
        "student_name": _student_name(inv.student),
        "student_image": frappe.db.get_value("Student", inv.student, "student_image") if inv.student else None,
        "program_enrollment": inv.program_enrollment,
        "posting_date": inv.posting_date,
        "due_date": inv.due_date,
        "total_amount": flt(inv.total_amount),
        "outstanding_amount": flt(inv.outstanding_amount),
        "status": inv.status,
        "items": [{"item_name": it.item_name, "amount": flt(it.amount)} for it in inv.items],
        "payments": pays,
    }


@frappe.whitelist()
def get_reports_overview(month=None, year=None):
    """Báo cáo tháng: doanh thu, công nợ, chuyên cần, doanh thu 6 tháng."""
    today = getdate(nowdate())
    payments = frappe.get_list(
        "Fee Payment", filters={"docstatus": 1}, fields=["amount", "payment_date"],
    )
    # doanh thu 6 tháng gần nhất
    buckets = []
    for k in range(5, -1, -1):
        d = getdate(frappe.utils.add_months(today, -k))
        buckets.append({"key": (d.year, d.month), "label": f"T{d.month}", "value": 0.0})
    bmap = {b["key"]: b for b in buckets}
    for p in payments:
        if not p.payment_date:
            continue
        pd = getdate(p.payment_date)
        b = bmap.get((pd.year, pd.month))
        if b:
            b["value"] += flt(p.amount)
    revenue_month = buckets[-1]["value"]

    invoices = frappe.get_list(
        "Fee Invoice", filters={"docstatus": 1}, fields=["outstanding_amount", "due_date"],
    )
    outstanding = sum(flt(i.outstanding_amount) for i in invoices)
    overdue_count = sum(
        1 for i in invoices
        if flt(i.outstanding_amount) > 0 and i.due_date and getdate(i.due_date) < today
    )

    # chuyên cần theo lớp = TB attendance_rate của HV active trong lớp
    att_by_class = []
    all_att = []
    for c in frappe.get_list("Class", filters={"status": ["in", ["Ongoing", "Upcoming"]]},
                             fields=["name", "class_name"]):
        enr = frappe.get_list(
            "Program Enrollment",
            filters={"class_id": c.name, "docstatus": 1, "enrollment_status": "Active"},
            fields=["student"],
        )
        rates = [
            flt(frappe.db.get_value("Student", e.student, "attendance_rate")) for e in enr
        ]
        if rates:
            avg = round(sum(rates) / len(rates))
            att_by_class.append({"name": c.class_name or c.name, "pct": avg})
            all_att.extend(rates)
    avg_attendance = round(sum(all_att) / len(all_att)) if all_att else 0

    return {
        "revenue_month": revenue_month,
        "outstanding": outstanding,
        "overdue_count": overdue_count,
        "avg_attendance": avg_attendance,
        "attendance_by_class": att_by_class,
        "revenue_6m": [{"label": b["label"], "value": b["value"]} for b in buckets],
    }
