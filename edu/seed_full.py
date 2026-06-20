"""
Seed script TOÀN BỘ - Tạo dữ liệu mẫu đầy đủ 1 năm cho education_erp.

Tạo: Courses, Classrooms, Teachers, 800 Students, Classes (đủ buổi 1 năm),
Class Sessions, Program Enrollments, Student Attendance, Fee Schedule/Invoice/Payment,
Student Leads.

Chạy:
    bench --site erp.localhost execute edu.seed_full.run

Tuỳ chọn: đặt số học viên qua biến môi trường SEED_STUDENTS (mặc định 800),
và năm học gốc qua SEED_YEAR (mặc định năm hiện tại - 1).

Script idempotent: chạy lại sẽ bỏ qua dữ liệu đã có (đánh dấu qua tên/seed marker).
Để xoá sạch dữ liệu seed: bench ... execute edu.seed_full.wipe
"""

import os
import random

import frappe
from frappe.utils import add_days, getdate, today, flt

random.seed(42)  # deterministic

# ---------------------------------------------------------------------------
# Dữ liệu tham chiếu (tiếng Việt)
# ---------------------------------------------------------------------------
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
      "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh",
      "Cao", "Mai", "Tô", "Vương", "Trương", "Lưu", "Đào"]
DEM_NAM = ["Văn", "Hữu", "Đức", "Minh", "Quang", "Công", "Thành", "Bá", "Trung", "Xuân"]
DEM_NU = ["Thị", "Thu", "Ngọc", "Kiều", "Phương", "Mỹ", "Hồng", "Bích", "Diệu", "Thanh"]
TEN_NAM = ["An", "Bảo", "Cường", "Dũng", "Đạt", "Hải", "Hùng", "Khoa", "Lâm",
           "Long", "Mạnh", "Nam", "Nghĩa", "Phúc", "Quân", "Sơn", "Tài", "Thắng",
           "Tuấn", "Vinh", "Khang", "Huy", "Kiên", "Lộc", "Phát"]
TEN_NU = ["Anh", "Bình", "Châu", "Dung", "Hà", "Hân", "Hương", "Lan", "Linh",
          "Mai", "Như", "Oanh", "Phương", "Quỳnh", "Thảo", "Trang", "Trinh",
          "Vân", "Yến", "Nhi", "Ngân", "Hằng", "Diệp", "Trâm", "Uyên"]

OCCUPATIONS = ["Sinh viên", "Học sinh", "Nhân viên văn phòng", "Kế toán",
               "Lập trình viên", "Giáo viên", "Marketing", "Y tá", "Kỹ sư",
               "Nhân viên ngân hàng", "Thiết kế đồ họa", "Buôn bán", "Lái xe",
               "Nhân viên bán hàng"]
SOURCES = ["Website", "Facebook", "Google", "Khác"]
RATINGS = ["3 Sao", "3 Sao", "4 Sao", "4 Sao", "4 Sao", "5 Sao", "5 Sao", "2 Sao"]
MSG_RESP = ["Tốt", "Tốt", "Tốt", "Bình thường", "Bình thường", "Chậm", "Không trả lời"]
HEALTH = ["Đang học đều", "Đang học đều", "Đang học đều", "Cần theo dõi",
          "Cảnh báo", "Khẩn cấp", "Ngừng học"]
STU_STATUS = ["Đang học", "Đang học", "Đang học", "Mới nhập học", "Bảo lưu",
              "Đã tốt nghiệp", "Nghỉ học"]

# Courses: (name, base_fee, total_sessions)
COURSES = [
    ("Tiếng Anh Giao Tiếp Cơ Bản", 4500000, 30),
    ("Tiếng Anh Giao Tiếp Nâng Cao", 5500000, 30),
    ("Luyện Thi IELTS 5.5+", 8000000, 40),
    ("Luyện Thi IELTS 6.5+", 9500000, 40),
    ("Tiếng Anh Thiếu Nhi Starter", 4000000, 24),
    ("Tiếng Anh Doanh Nghiệp", 7000000, 30),
    ("Tiếng Nhật Sơ Cấp N5", 5000000, 36),
    ("Tiếng Hàn Sơ Cấp", 4800000, 36),
]

CLASSROOMS = [
    ("Phòng A101", 20), ("Phòng A102", 20), ("Phòng A103", 18),
    ("Phòng B201", 25), ("Phòng B202", 25), ("Phòng C301", 15),
    ("Phòng C302", 15), ("Phòng VIP", 10),
]

TEACHERS = [
    "Nguyễn Hoàng Anh", "Trần Thị Mỹ Dung", "Lê Quốc Khánh", "Phạm Thu Trang",
    "Hoàng Minh Tuấn", "Đỗ Thị Hồng Nhung", "Vũ Đình Nam", "Bùi Thị Lan Phương",
    "Ngô Văn Thành", "Mai Thị Kim Chi", "Sarah Johnson", "David Williams",
    "Phan Thanh Hải", "Đặng Thị Thu Hương", "Lý Quốc Bảo", "Trương Mỹ Linh",
    "Hồ Văn Đức", "Dương Thị Ngọc Mai", "Cao Minh Quân", "Võ Thị Kim Oanh",
    "Emily Brown", "Michael Davis", "Tô Thanh Tùng", "Lưu Thị Bích Ngọc",
    "Đinh Công Hậu", "Nguyễn Thị Hồng Vân", "James Wilson", "Trần Quốc Việt",
]

SCHEDULE_TEMPLATES = [
    ("2-4-6", [0, 2, 4]),   # Mon Wed Fri
    ("3-5-7", [1, 3, 5]),   # Tue Thu Sat
    ("T7-CN", [5, 6]),      # Sat Sun
]
TIME_SLOTS = [("18:00:00", "20:00:00"), ("19:30:00", "21:30:00"),
              ("09:00:00", "11:00:00"), ("14:00:00", "16:00:00")]

SEED_TAG = "[SEED]"  # đánh dấu vào occupation/description không, dùng marker riêng


# ---------------------------------------------------------------------------
def _quiet_mode():
    """Tắt các cơ chế đẩy background job / realtime / notification trong lúc
    seed để tránh 'Too many queued background jobs'."""
    frappe.flags.in_import = True
    frappe.flags.in_install = True          # bỏ qua nhiều hook không cần thiết
    frappe.flags.mute_emails = True
    frappe.flags.mute_messages = True
    # No-op hoá enqueue & realtime
    frappe.enqueue = lambda *a, **k: None
    frappe.enqueue_doc = lambda *a, **k: None
    try:
        frappe.publish_realtime = lambda *a, **k: None
    except Exception:
        pass

    # Tắt kiểm tra trùng lịch của Class Session trong lúc seed. Đây là dữ liệu
    # demo dày đặc, ta chấp nhận một số buổi có thể trùng phòng/GV trên lý
    # thuyết; validate này dành cho thao tác nhập liệu thủ công, không phù hợp
    # khi nạp hàng loạt. Nhờ vậy mọi lớp/buổi đều tạo được, không vỡ giữa chừng.
    try:
        from edu.education_erp.doctype.class_session import class_session as _cs
        _cs.ClassSession._check_conflicts = lambda self: None
    except Exception as e:
        print(f"  [WARN] không tắt được _check_conflicts: {e}")


def _exists(doctype, filters):
    return frappe.db.exists(doctype, filters)


# ---------------------------------------------------------------------------
# Raw bulk-insert: nạp thẳng vào DB cho các bảng KHỐI LƯỢNG LỚN, KHÔNG có hook
# nghiệp vụ (Student Attendance, Class Session). Nhanh hơn doc.insert nhiều lần
# vì bỏ vòng validate/ORM, nhưng vẫn điền đủ metadata hệ thống nên app đọc bình
# thường. Dùng frappe.db.bulk_insert nếu có, fallback INSERT đa dòng.
# ---------------------------------------------------------------------------
import time as _time
import hashlib as _hashlib


def _gen_name(prefix, n):
    """Sinh name kiểu hash 10 ký tự (giống Frappe khi autoname=hash)."""
    raw = f"{prefix}{n}{_time.time()}{random.random()}"
    return _hashlib.sha1(raw.encode()).hexdigest()[:10]


def _bulk_insert(doctype, fields, rows):
    """rows: list[dict] chỉ chứa field nghiệp vụ. Tự thêm metadata + name.

    Trả về list name đã tạo (để tham chiếu, ví dụ attendance -> session)."""
    if not rows:
        return []
    now = frappe.utils.now()
    user = "Administrator"
    meta_cols = ["name", "creation", "modified", "modified_by", "owner",
                 "docstatus", "idx"]
    all_cols = meta_cols + fields
    values = []
    names = []
    for i, r in enumerate(rows):
        nm = r.get("__name__") or _gen_name(doctype, i)
        names.append(nm)
        row = [nm, now, now, user, user, 0, i + 1]
        for f in fields:
            v = r.get(f)
            row.append(v)
        values.append(row)
    try:
        frappe.db.bulk_insert(doctype, all_cols, values)
    except (AttributeError, TypeError):
        # Fallback: INSERT đa dòng thủ công
        col_sql = ", ".join(f"`{c}`" for c in all_cols)
        ph = "(" + ", ".join(["%s"] * len(all_cols)) + ")"
        CHUNK = 500
        for s in range(0, len(values), CHUNK):
            batch = values[s:s + CHUNK]
            sql = (f"INSERT INTO `tab{doctype}` ({col_sql}) VALUES "
                   + ", ".join([ph] * len(batch)))
            flat = [x for row in batch for x in row]
            frappe.db.sql(sql, flat)
    return names


def _vn_name(gender):
    ho = random.choice(HO)
    if gender == "Nam":
        return f"{ho} {random.choice(DEM_NAM)} {random.choice(TEN_NAM)}"
    return f"{ho} {random.choice(DEM_NU)} {random.choice(TEN_NU)}"


def _slug_email(full_name, i):
    parts = full_name.lower().split()
    # bỏ dấu đơn giản
    table = str.maketrans(
        "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd",
    )
    base = "".join(p.translate(table) for p in parts[::-1])
    return f"{base}{i}@example.com"


# ---------------------------------------------------------------------------
def _ensure_courses():
    out = {}
    for name, fee, sessions in COURSES:
        ex = _exists("Course", {"course_name": name})
        if ex:
            out[name] = ex
            continue
        d = frappe.new_doc("Course")
        d.course_name = name
        d.base_fee = fee
        d.description = f"Khoá học {name} - {sessions} buổi."
        d.insert(ignore_permissions=True)
        out[name] = d.name
    return out


def _ensure_classrooms():
    out = []
    for name, cap in CLASSROOMS:
        ex = _exists("Classroom", {"room_name": name})
        if ex:
            out.append(ex)
            continue
        d = frappe.new_doc("Classroom")
        d.room_name = name
        d.capacity = cap
        d.insert(ignore_permissions=True)
        out.append(d.name)
    return out


def _ensure_teachers():
    out = []
    for i, name in enumerate(TEACHERS):
        ex = _exists("Teacher", {"teacher_name": name})
        if ex:
            out.append(ex)
            continue
        d = frappe.new_doc("Teacher")
        d.teacher_name = name
        d.phone = f"0908{i:06d}"[:10]
        d.email = _slug_email(name, i).replace("example.com", "edu.vn")
        d.status = "Active"
        d.insert(ignore_permissions=True)
        out.append(d.name)
    return out


def _ensure_students(n, year):
    """Tạo n học viên. Trả về list student names."""
    names = []
    base = getdate(f"{year-22}-01-01")
    for i in range(1, n + 1):
        gender = random.choice(["Nam", "Nữ"])
        full = _vn_name(gender)
        email = _slug_email(full, i)
        phone = f"09{random.randint(10000000, 99999999)}"

        if _exists("Student", {"email": email}):
            names.append(frappe.db.get_value("Student", {"email": email}, "name"))
            continue

        dob = add_days(base, random.randint(0, 365 * 12))  # tuổi 10-22
        status = random.choice(STU_STATUS)
        d = frappe.new_doc("Student")
        d.full_name = full
        d.date_of_birth = dob
        d.gender = gender
        d.email = email
        d.phone = phone
        d.source = random.choice(SOURCES)
        d.occupation = random.choice(OCCUPATIONS)
        d.rating = random.choice(RATINGS)
        d.message_response = random.choice(MSG_RESP)
        d.health_status = random.choice(HEALTH)
        d.student_status = status
        d.average_score = round(random.uniform(5.0, 9.8), 1)
        d.insert(ignore_permissions=True)
        names.append(d.name)

        if i % 100 == 0:
            frappe.db.commit()
            print(f"  ...đã tạo {i}/{n} học viên")
    frappe.db.commit()
    return names


def _overlaps(a_start, a_end, b_start, b_end):
    return a_start <= b_end and b_start <= a_end


def _create_classes(courses, classrooms, teachers, year, target_classes):
    """Tạo `target_classes` lớp trải đều 1 năm, KHÔNG trùng lịch.

    Ràng buộc (Class Session.validate): trùng khi cùng ngày + giao giờ và
    cùng classroom HOẶC cùng teacher.

    Mô hình: mỗi "lane" = (classroom, time_slot, template). Trong một lane,
    các lớp được xếp NỐI TIẾP theo thời gian (lớp sau bắt đầu sau khi lớp
    trước trong lane đã kết thúc) -> không bao giờ trùng phòng. Teacher được
    cấp phát theo bản đồ bận (interval) trên từng (time_slot, template) để
    không trùng GV. Nhờ xếp nối tiếp trong năm, ta tạo được nhiều lớp dù số
    phòng/khe có hạn.
    """
    classes = []
    course_items = list(courses.items())
    course_sessions = {name: s for name, _, s in COURSES}
    year_start = getdate(f"{year}-01-05")
    year_end = getdate(f"{year}-12-31")

    # Lane = (phòng, khung giờ). MỖI lane có MỘT con trỏ thời gian duy nhất và
    # các lớp trong lane được xếp NỐI TIẾP theo ngày -> không bao giờ trùng
    # phòng dù khác template (vì 3-5-7 và T7-CN có chung thứ Bảy, nếu cùng
    # phòng+giờ mà chạy song song sẽ đụng nhau). Template được chọn theo lượt.
    lanes = []
    for room in classrooms:
        for (start_t, end_t) in TIME_SLOTS:
            lanes.append({
                "room": room, "start_t": start_t, "end_t": end_t,
                "free_from": year_start,  # con trỏ thời gian rảnh kế tiếp
            })
    random.shuffle(lanes)

    # teacher_busy[teacher] = list of (start_date, end_date, weekdays_set,
    #   start_t, end_t). Hai lớp của cùng GV chỉ TRÙNG khi: có chung thứ trong
    #   tuần AND khoảng ngày giao nhau AND khung giờ giao nhau (đúng theo
    #   validate của Class Session). Nhờ nới lỏng theo thứ/giờ, mỗi GV có thể
    #   dạy song song nhiều lớp khác lịch -> đủ lớp cho toàn bộ học viên.
    teacher_busy = {t: [] for t in teachers}

    def _sec(t):
        h, m, s = (t.split(":") + ["0", "0"])[:3]
        return int(h) * 3600 + int(m) * 60 + int(s)

    def _pick_teacher(s, e, weekdays, start_t, end_t):
        wd = set(weekdays)
        ss, se = _sec(start_t), _sec(end_t)
        cand = teachers[:]
        random.shuffle(cand)
        for t in cand:
            ok = True
            for (bs, be, bwd, bst, bet) in teacher_busy[t]:
                if (wd & bwd) and _overlaps(s, e, bs, be) \
                        and _overlaps(ss, se, _sec(bst), _sec(bet)):
                    ok = False
                    break
            if ok:
                teacher_busy[t].append((s, e, wd, start_t, end_t))
                return t
        return None

    idx = 0
    safety = 0
    # Lặp vòng qua các lane, mỗi lượt đẩy thêm 1 lớp vào lane còn chỗ trong năm
    while idx < target_classes and safety < target_classes * 50:
        safety += 1
        progressed = False
        for lane in lanes:
            if idx >= target_classes:
                break
            cname, course_id = course_items[idx % len(course_items)]
            total = course_sessions[cname]
            tmpl_name, weekdays = SCHEDULE_TEMPLATES[idx % len(SCHEDULE_TEMPLATES)]
            start = lane["free_from"]
            dates = _session_dates(start, weekdays, total)
            if not dates or dates[-1] > year_end:
                continue  # lane này đã hết chỗ trong năm
            s_date, e_date = dates[0], dates[-1]
            teacher = _pick_teacher(s_date, e_date, weekdays,
                                    lane["start_t"], lane["end_t"])
            if teacher is None:
                continue  # không có GV rảnh cho khoảng này
            cap = random.choice([15, 18, 20, 25])

            d = frappe.new_doc("Class")
            label = cname.split()[0] + " " + cname.split()[-1]
            d.class_name = f"{label} - {s_date.strftime('%y%m%d')}-{idx+1:04d}"
            d.course = course_id
            d.teacher = teacher
            d.start_date = s_date
            d.schedule_template = tmpl_name
            d.start_time = lane["start_t"]
            d.end_time = lane["end_t"]
            d.total_sessions = total
            d.classroom = lane["room"]
            d.max_capacity = cap
            d.standard_fee = frappe.db.get_value("Course", course_id, "base_fee")
            d.status = "Ongoing" if e_date >= getdate(today()) else "Completed"
            d.insert(ignore_permissions=True)

            classes.append({
                "name": d.name, "course": course_id, "teacher": teacher,
                "classroom": lane["room"], "start": s_date,
                "weekdays": weekdays, "start_t": lane["start_t"],
                "end_t": lane["end_t"], "total": total,
                "fee": flt(d.standard_fee), "cap": cap, "dates": dates,
            })
            # đẩy con trỏ lane sang sau khi lớp này kết thúc (+ nghỉ 1 tuần)
            lane["free_from"] = add_days(e_date, 7)
            idx += 1
            progressed = True
        frappe.db.commit()
        if not progressed:
            break  # không còn lane nào nhận thêm lớp -> dừng
    print(f"  ...đã tạo {len(classes)} lớp học (mục tiêu {target_classes})")
    return classes


def _session_dates(start, weekdays, total):
    """Sinh đúng `total` ngày học theo lịch weekly template."""
    dates = []
    cur = getdate(start)
    # tiến tới ngày đầu tiên khớp weekday
    guard = 0
    while len(dates) < total and guard < total * 4 + 30:
        if cur.weekday() in weekdays:
            dates.append(cur)
        cur = add_days(cur, 1)
        guard += 1
    return dates


def _create_sessions_and_enroll(classes, students, year):
    """Tạo enrollment (SUBMIT), session, attendance, thanh toán cho từng lớp.

    Enrollment được submit -> hệ thống tự sinh Onboarding Task + Fee Schedule +
    Fee Invoice. Ta chỉ tạo thêm Fee Payment (submit) để chuyển trạng thái hóa
    đơn sang Paid/Partially Paid. Trả về list bản ghi enrollment để các bước
    seed sau (assessment/homework/refund...) dùng lại.
    """
    today_d = getdate(today())
    n_att = n_pay = n_enr = n_sess = 0
    enrollments = []  # [{enr, student, class, invoice, date}]
    student_pool = list(students)
    random.shuffle(student_pool)
    cursor = 0

    for ci, cls in enumerate(classes):
        # ---- chọn học viên cho lớp (đảm bảo <= max_capacity) ----
        cap = cls["cap"]
        n_enroll = random.randint(int(cap * 0.6), cap)
        enrolled = []
        seen = set()
        while len(enrolled) < n_enroll:
            if cursor >= len(student_pool):
                cursor = 0
                random.shuffle(student_pool)
            stu = student_pool[cursor]
            cursor += 1
            if stu not in seen:
                seen.add(stu)
                enrolled.append(stu)

        fee = cls["fee"] or 5000000
        class_enrolled = []  # student thực sự enroll thành công trong lớp này
        for stu in enrolled:
            if _exists("Program Enrollment",
                       {"student": stu, "class_id": cls["name"], "docstatus": 1}):
                continue
            discount_pct = random.choice([0, 0, 0, 5, 10, 15])
            enr = frappe.new_doc("Program Enrollment")
            enr.student = stu
            enr.class_id = cls["name"]
            enr.enrollment_date = cls["start"]
            enr.enrollment_type = "Official"
            enr.list_price = fee
            if discount_pct:
                enr.discount_type = "Percent"
                enr.discount_value = discount_pct
                enr.discount_reason = "Ưu đãi khai giảng"
            enr.installment_count = 1
            try:
                enr.insert(ignore_permissions=True)
                enr.submit()  # -> Onboarding Task + Fee Schedule + Fee Invoice
            except Exception as e:
                # Vượt sĩ số / trùng active -> bỏ qua học viên này
                print(f"    [WARN] enroll {stu} @ {cls['name']}: {e}")
                continue
            n_enr += 1
            class_enrolled.append(stu)
            net = flt(enr.net_fee)

            # ---- Hóa đơn tự sinh từ enrollment ----
            inv_name = frappe.db.get_value(
                "Fee Invoice", {"program_enrollment": enr.name, "docstatus": 1}, "name")
            invoice_rec = {"name": inv_name, "net": net, "status": "Unpaid"}
            if inv_name and net > 0:
                outstanding = flt(frappe.db.get_value(
                    "Fee Invoice", inv_name, "outstanding_amount"))
                roll = random.random()
                if roll < 0.75:
                    pay_amt = outstanding              # trả đủ -> Paid
                elif roll < 0.90:
                    pay_amt = round(outstanding / 2)   # trả 1 phần -> Partially Paid
                else:
                    pay_amt = 0                        # chưa trả
                if pay_amt > 0:
                    pay = frappe.new_doc("Fee Payment")
                    pay.student = stu
                    pay.posting_date = add_days(cls["start"], 7)
                    pay.payment_date = add_days(cls["start"], 7)
                    pay.payment_method = random.choice(["Cash", "Bank Transfer", "Card"])
                    pay.amount = pay_amt
                    pay.reference_no = f"TT{ci:03d}{n_pay:05d}"
                    pay.append("references",
                               {"invoice": inv_name, "allocated_amount": pay_amt})
                    try:
                        pay.insert(ignore_permissions=True)
                        pay.submit()  # -> cập nhật invoice Paid/Partially Paid
                        n_pay += 1
                    except Exception as e:
                        print(f"    [WARN] payment {stu}: {e}")
                else:
                    # Chưa trả: đánh dấu Overdue nếu đã quá hạn
                    due = getdate(frappe.db.get_value("Fee Invoice", inv_name, "due_date"))
                    if due and due < today_d:
                        frappe.db.set_value("Fee Invoice", inv_name, "status", "Overdue")
                invoice_rec["status"] = frappe.db.get_value(
                    "Fee Invoice", inv_name, "status")

            enrollments.append({
                "enr": enr.name, "student": stu, "class": cls["name"],
                "invoice": inv_name, "net": net, "date": cls["start"],
            })

        cls["enrolled"] = class_enrolled
        enrolled = class_enrolled
        frappe.db.commit()

        # ---- Sessions + attendance (RAW BULK INSERT) ----
        dates = cls.get("dates") or _session_dates(
            cls["start"], cls["weekdays"], cls["total"])
        sess_rows = []
        sess_meta = []  # (name, sdate, past) song song với sess_rows
        for si, sdate in enumerate(dates, start=1):
            past = sdate <= today_d
            nm = _gen_name("CS", n_sess + si)
            sess_rows.append({
                "__name__": nm,
                "class_id": cls["name"], "classroom": cls["classroom"],
                "session_date": sdate, "start_time": cls["start_t"],
                "end_time": cls["end_t"], "teacher": cls["teacher"],
                "lesson_topic": f"Buổi {si}: Unit {si}",
                "session_type": "Regular",
                "teacher_attendance_status": "Present" if past else "",
                "session_status": "Completed" if past else "Scheduled",
            })
            sess_meta.append((nm, sdate, past))
        _bulk_insert(
            "Class Session",
            ["class_id", "classroom", "session_date", "start_time", "end_time",
             "teacher", "lesson_topic", "session_type",
             "teacher_attendance_status", "session_status"],
            sess_rows)
        n_sess += len(sess_rows)

        att_rows = []
        for nm, sdate, past in sess_meta:
            if not past:
                continue
            for stu in enrolled:
                r = random.random()
                if r < 0.85:
                    status = "Present"
                elif r < 0.92:
                    status = "Late"
                elif r < 0.97:
                    status = "Absent with Permission"
                else:
                    status = "Absent without Permission"
                att_rows.append({
                    "class_id": cls["name"], "class_session": nm,
                    "student": stu, "attendance_date": sdate, "status": status,
                    "attendance_type": "Regular",
                    "minutes_late": random.randint(5, 25) if status == "Late" else 0,
                })
        _bulk_insert(
            "Student Attendance",
            ["class_id", "class_session", "student", "attendance_date", "status",
             "attendance_type", "minutes_late"],
            att_rows)
        n_att += len(att_rows)
        frappe.db.commit()
        print(f"  ...lớp {ci+1}/{len(classes)} ({cls['name']}): "
              f"{len(enrolled)} HV, {len(dates)} buổi")

    print(f"\n  Tổng: enroll={n_enr} session={n_sess} attendance={n_att} "
          f"payment={n_pay}")
    return enrollments


def _create_leads(year, n=120):
    statuses = ["New", "New", "Consulting", "Consulting", "Testing", "Trial",
                "Enrolled", "Lost"]
    src = ["Website", "Facebook", "Hotline", "Word of Mouth", "Other"]
    leads = []  # [(name, status)]
    for i in range(n):
        gender = random.choice(["Nam", "Nữ"])
        name = _vn_name(gender)
        phone = f"08{random.randint(10000000, 99999999)}"
        if _exists("Student Lead", {"phone": phone}):
            continue
        d = frappe.new_doc("Student Lead")
        d.lead_name = name
        d.phone = phone
        d.email = _slug_email(name, 9000 + i)
        d.source = random.choice(src)
        d.status = random.choice(statuses)
        d.gender = gender
        d.occupation = random.choice(OCCUPATIONS)
        if d.status == "Lost":
            d.lost_reason = random.choice(
                ["Học phí cao", "Chọn trung tâm khác", "Không sắp xếp được lịch",
                 "Không phản hồi"])
        d.insert(ignore_permissions=True)
        leads.append((d.name, d.status))
    frappe.db.commit()
    print(f"  ...đã tạo {len(leads)} lead tư vấn")
    return leads


# ===========================================================================
# NHÓM HỌC TẬP & TIẾN ĐỘ
# ===========================================================================
def _seed_curriculum(courses):
    """Mỗi Course -> 3-5 Curriculum Module -> mỗi module 4-8 Lesson Template."""
    n_mod = n_les = 0
    templates_by_course = {}
    for cname, course_id in courses.items():
        if _exists("Curriculum Module", {"course": course_id}):
            templates_by_course[course_id] = frappe.get_all(
                "Lesson Template",
                filters={"course": course_id}, pluck="name")
            continue
        n_modules = random.randint(3, 5)
        course_templates = []
        for m in range(1, n_modules + 1):
            mod = frappe.new_doc("Curriculum Module")
            mod.course = course_id
            mod.module_name = f"Học phần {m}: {cname.split()[-1]} cấp {m}"
            mod.sequence = m
            mod.description = f"Nội dung học phần {m} của khoá {cname}."
            mod.insert(ignore_permissions=True)
            n_mod += 1
            for l in range(1, random.randint(4, 8) + 1):
                les = frappe.new_doc("Lesson Template")
                les.curriculum_module = mod.name
                les.lesson_no = l
                les.title = f"Bài {l}: Chủ đề {m}.{l}"
                les.duration_minutes = random.choice([90, 120])
                les.vocabulary = f"Từ vựng bài {l}"
                les.grammar = f"Ngữ pháp bài {l}"
                les.homework = f"Bài tập về nhà bài {l}"
                les.insert(ignore_permissions=True)
                course_templates.append(les.name)
                n_les += 1
        templates_by_course[course_id] = course_templates
        frappe.db.commit()
    print(f"  ...đã tạo {n_mod} học phần, {n_les} giáo án (lesson template)")
    return templates_by_course


def _seed_learning_materials(courses, classes):
    types = ["Document", "Link", "Video", "Other"]
    n = 0
    class_by_course = {}
    for c in classes:
        class_by_course.setdefault(c["course"], []).append(c["name"])
    for cname, course_id in courses.items():
        for i in range(random.randint(3, 6)):
            d = frappe.new_doc("Learning Material")
            d.title = f"Tài liệu {i+1} - {cname}"
            d.material_type = random.choice(types)
            d.course = course_id
            if random.random() < 0.5 and class_by_course.get(course_id):
                d.class_id = random.choice(class_by_course[course_id])
            d.url = f"https://lms.example.com/{course_id}/tai-lieu-{i+1}"
            d.is_public = random.choice([0, 1])
            d.description = f"Tài liệu học tập cho {cname}."
            d.insert(ignore_permissions=True)
            n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} tài liệu học tập")


def _seed_assessments(enrollments):
    """Mỗi enrollment 1-3 bài kiểm tra (Student Assessment)."""
    types = ["Vocabulary", "Grammar", "Reading", "Listening", "Kaiwa",
             "JLPT Mini Test", "Homework"]
    n = 0
    for i, e in enumerate(enrollments):
        for k in range(random.randint(1, 3)):
            a = frappe.new_doc("Student Assessment")
            a.student = e["student"]
            a.class_id = e["class"]
            a.program_enrollment = e["enr"]
            a.assessment_name = f"Bài KT {k+1}"
            a.assessment_type = random.choice(types)
            a.max_score = 100
            a.score = round(random.uniform(45, 98), 1)
            a.weight = random.choice([1, 1, 2, 3])
            a.insert(ignore_permissions=True)
            n += 1
        if i % 200 == 0:
            frappe.db.commit()
    frappe.db.commit()
    print(f"  ...đã tạo {n} bài kiểm tra (assessment)")


def _seed_homework(classes, enrollments):
    """Mỗi lớp 2-4 bài tập (Whole Class) + bài nộp của ~70% HV trong lớp."""
    today_d = getdate(today())
    enr_by_class = {}
    for e in enrollments:
        enr_by_class.setdefault(e["class"], []).append(e)
    n_hw = n_sub = 0
    for cls in classes:
        cls_enr = enr_by_class.get(cls["name"], [])
        sessions = frappe.get_all(
            "Class Session",
            filters={"class_id": cls["name"], "session_status": "Completed"},
            fields=["name", "session_date"], order_by="session_date")
        if not sessions:
            continue
        for h in range(random.randint(2, 4)):
            sess = random.choice(sessions)
            assigned = getdate(sess["session_date"])
            hw = frappe.new_doc("Homework")
            hw.title = f"Bài tập {h+1} - {cls['name']}"
            hw.class_id = cls["name"]
            hw.class_session = sess["name"]
            hw.target = "Whole Class"
            hw.assigned_date = assigned
            hw.due_date = add_days(assigned, 7)
            hw.status = "Published"
            hw.description = f"Hoàn thành bài tập {h+1}."
            hw.insert(ignore_permissions=True)
            n_hw += 1
            for e in cls_enr:
                if random.random() > 0.70:
                    continue
                sub = frappe.new_doc("Homework Submission")
                sub.homework = hw.name
                sub.program_enrollment = e["enr"]
                sub.student = e["student"]
                sub.submission_date = add_days(assigned, random.randint(1, 7))
                graded = random.random() < 0.7
                sub.status = "Graded" if graded else "Submitted"
                sub.content = "Bài làm của học viên."
                if graded:
                    sub.grade = round(random.uniform(5, 10), 1)
                    sub.feedback = random.choice(
                        ["Tốt", "Cần cố gắng thêm", "Khá", "Xuất sắc"])
                try:
                    sub.insert(ignore_permissions=True)
                    n_sub += 1
                except Exception:
                    pass  # trùng (homework, enrollment) -> bỏ qua
        frappe.db.commit()
    print(f"  ...đã tạo {n_hw} bài tập, {n_sub} bài nộp")


# ===========================================================================
# NHÓM TƯ VẤN & HẸN (theo Student Lead)
# ===========================================================================
def _seed_consultations(leads, year):
    results = ["Tiềm năng cao", "Tiềm năng trung bình", "Cần theo dõi thêm",
               "Tiềm năng thấp", "Không quan tâm"]
    base = getdate(f"{year}-01-10")
    n = 0
    for lead_name, status in leads:
        for _ in range(random.randint(1, 4)):
            c = frappe.new_doc("Consultation Log")
            c.lead = lead_name
            cdate = add_days(base, random.randint(0, 330))
            c.contact_date = cdate
            c.result = random.choice(results)
            c.notes = "Đã trao đổi với khách về khoá học và học phí."
            c.next_follow_up = add_days(cdate, random.randint(3, 14))
            c.insert(ignore_permissions=True)
            n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} lịch sử tư vấn")


def _seed_appointments(leads, year):
    statuses = ["Scheduled", "Completed", "Completed", "Cancelled", "Rescheduled"]
    purposes = ["Tư vấn trực tiếp", "Test đầu vào", "Tham quan trung tâm",
                "Ký hợp đồng"]
    base = getdate(f"{year}-01-10")
    n = 0
    for lead_name, status in leads:
        if random.random() > 0.4:
            continue
        for _ in range(random.randint(1, 2)):
            a = frappe.new_doc("Student Appointment")
            a.lead = lead_name
            a.appointment_date = add_days(base, random.randint(0, 330))
            a.appointment_time = random.choice(
                ["09:00:00", "10:30:00", "14:00:00", "16:00:00", "18:30:00"])
            a.purpose = random.choice(purposes)
            a.status = random.choice(statuses)
            a.insert(ignore_permissions=True)
            n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} lịch hẹn")


def _seed_placement_tests(leads, courses, year):
    levels = ["Mất gốc", "N5", "N4", "N3", "N2", "N1"]
    base = getdate(f"{year}-01-10")
    course_ids = list(courses.values())
    n = 0
    for lead_name, status in leads:
        if status in ("New", "Lost") or random.random() > 0.5:
            continue
        t = frappe.new_doc("Placement Test")
        t.lead = lead_name
        t.test_date = add_days(base, random.randint(0, 330))
        t.score = round(random.uniform(20, 95), 1)
        t.level = random.choice(levels)
        t.recommended_course = random.choice(course_ids)
        t.status = "Enrolled" if status == "Enrolled" else random.choice(
            ["Pending", "Evaluated"])
        t.notes = "Kết quả test xếp lớp đầu vào."
        t.insert(ignore_permissions=True)
        n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} bài test xếp lớp")


# ===========================================================================
# NHÓM TÀI CHÍNH MỞ RỘNG
# ===========================================================================
def _seed_refunds(enrollments):
    """~3% hóa đơn đã trả -> tạo Fee Refund (submit)."""
    n = 0
    paid = [e for e in enrollments
            if e["invoice"] and frappe.db.get_value(
                "Fee Invoice", e["invoice"], "status") == "Paid"]
    sample = random.sample(paid, k=max(1, int(len(paid) * 0.03))) if paid else []
    for e in sample:
        r = frappe.new_doc("Fee Refund")
        r.student = e["student"]
        r.invoice_reference = e["invoice"]
        r.refund_amount = round(flt(e["net"]) * random.choice([0.1, 0.2, 0.3]))
        r.refund_date = add_days(e["date"], random.randint(30, 120))
        r.reason = random.choice(
            ["Học viên chuyển công tác", "Lý do sức khoẻ", "Không sắp xếp được lịch"])
        r.status = "Completed"
        try:
            r.insert(ignore_permissions=True)
            r.submit()
            n += 1
        except Exception as ex:
            print(f"    [WARN] refund: {ex}")
    frappe.db.commit()
    print(f"  ...đã tạo {n} phiếu hoàn tiền")


def _seed_salary_slips(teachers, year):
    """Mỗi GV vài tháng -> Teacher Salary Slip (submit), số buổi từ Class Session."""
    n = 0
    for t in teachers:
        for month in random.sample(range(1, 13), k=random.randint(3, 6)):
            cnt = frappe.db.sql(
                """select count(*) from `tabClass Session`
                   where teacher=%s and extract(month from session_date)=%s
                   and extract(year from session_date)=%s
                   and session_status='Completed'""",
                (t, month, year))[0][0]
            slip = frappe.new_doc("Teacher Salary Slip")
            slip.teacher = t
            slip.month = str(month)
            slip.year = year
            slip.total_sessions_taught = int(cnt)
            slip.rate_per_session = random.choice([250000, 300000, 350000, 400000])
            slip.status = random.choice(["Paid", "Paid", "Unpaid"])
            try:
                slip.insert(ignore_permissions=True)
                slip.submit()
                n += 1
            except Exception as ex:
                print(f"    [WARN] salary {t} m{month}: {ex}")
    frappe.db.commit()
    print(f"  ...đã tạo {n} bảng lương giáo viên")


# ===========================================================================
# NHÓM VẬN HÀNH
# ===========================================================================
def _ensure_education_settings():
    try:
        s = frappe.get_single("Education Settings")
        if not s.default_due_days:
            s.default_due_days = 7
            s.save(ignore_permissions=True)
    except Exception as ex:
        print(f"    [WARN] settings: {ex}")
    print("  ...đã cấu hình Education Settings")


def _seed_guardians_and_cards(students, year):
    """~30% HV có Guardian (link), ~60% có Student Card."""
    n_g = n_c = 0
    base = getdate(f"{year}-01-05")
    for i, stu in enumerate(students):
        if random.random() < 0.30:
            g = frappe.new_doc("Guardian")
            g.guardian_name = "Phụ huynh " + _vn_name(random.choice(["Nam", "Nữ"]))
            g.phone = f"09{random.randint(10000000, 99999999)}"
            g.insert(ignore_permissions=True)
            frappe.db.set_value("Student", stu, "guardian", g.name)
            n_g += 1
        if random.random() < 0.60:
            card = frappe.new_doc("Student Card")
            card.student = stu
            card.card_number = f"THE{year}{i+1:05d}"
            card.issue_date = add_days(base, random.randint(0, 200))
            card.status = random.choice(["Active", "Active", "Active", "Lost"])
            card.insert(ignore_permissions=True)
            n_c += 1
        if i % 200 == 0:
            frappe.db.commit()
    frappe.db.commit()
    print(f"  ...đã tạo {n_g} người giám hộ, {n_c} thẻ học viên")


def _seed_deferments_transfers(enrollments, classes):
    """~3% bảo lưu, ~2% chuyển lớp (submit)."""
    n_def = n_tr = 0
    sample_def = random.sample(enrollments, k=max(1, int(len(enrollments) * 0.03)))
    for e in sample_def:
        d = frappe.new_doc("Student Deferment")
        d.student = e["student"]
        d.class_id = e["class"]
        frm = add_days(e["date"], random.randint(20, 90))
        d.leave_from_date = frm
        d.leave_to_date = add_days(frm, random.randint(30, 90))
        d.reason = random.choice(["Lý do sức khoẻ", "Đi công tác", "Bận việc gia đình"])
        d.status = random.choice(["Approved", "Approved", "Pending"])
        try:
            d.insert(ignore_permissions=True)
            d.submit()
            n_def += 1
        except Exception:
            pass
    class_names = [c["name"] for c in classes]
    sample_tr = random.sample(enrollments, k=max(1, int(len(enrollments) * 0.02)))
    for e in sample_tr:
        others = [c for c in class_names if c != e["class"]]
        if not others:
            continue
        t = frappe.new_doc("Class Transfer")
        t.student = e["student"]
        t.from_class = e["class"]
        t.to_class = random.choice(others)
        t.transfer_date = add_days(e["date"], random.randint(20, 100))
        t.reason = random.choice(["Lệch trình độ", "Đổi lịch học", "Theo nguyện vọng"])
        t.status = random.choice(["Approved", "Approved", "Pending"])
        try:
            t.insert(ignore_permissions=True)
            t.submit()
            n_tr += 1
        except Exception:
            pass
    frappe.db.commit()
    print(f"  ...đã tạo {n_def} bảo lưu, {n_tr} chuyển lớp")


def _seed_room_bookings(classrooms, year):
    purposes = ["Họp giáo viên", "Sự kiện CLB tiếng Nhật", "Thi xếp lớp",
                "Buổi hội thảo", "Đào tạo nội bộ"]
    base = getdate(f"{year}-01-05")
    n = 0
    for _ in range(30):
        b = frappe.new_doc("Room Booking")
        b.classroom = random.choice(classrooms)
        b.booking_date = add_days(base, random.randint(0, 350))
        slot = random.choice([("08:00:00", "10:00:00"), ("13:00:00", "15:00:00"),
                              ("16:00:00", "18:00:00")])
        b.start_time, b.end_time = slot
        b.purpose = random.choice(purposes)
        b.booked_by = "Phòng Đào tạo"
        b.status = random.choice(["Booked", "Completed", "Completed"])
        b.insert(ignore_permissions=True)
        n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} đặt phòng")


def _seed_internal_tasks(year):
    titles = ["Chuẩn bị tài liệu khai giảng", "Liên hệ phụ huynh nhắc học phí",
              "Cập nhật website khoá mới", "Tổ chức sự kiện cuối kỳ",
              "Kiểm kê trang thiết bị phòng học", "Lên lịch thi xếp lớp",
              "Đào tạo giáo viên mới", "Rà soát hợp đồng giáo viên",
              "Chuẩn bị báo cáo doanh thu", "Bảo trì máy chiếu"]
    base = getdate(f"{year}-01-05")
    n = 0
    for i in range(15):
        d = frappe.new_doc("Internal Task")
        d.title = random.choice(titles) + f" #{i+1}"
        d.description = "Công việc nội bộ trung tâm."
        d.assigned_to = "Phòng Đào tạo"
        d.due_date = add_days(base, random.randint(0, 350))
        d.priority = random.choice(["Low", "Medium", "High"])
        d.status = random.choice(["To Do", "In Progress", "Done", "Done"])
        d.insert(ignore_permissions=True)
        n += 1
    frappe.db.commit()
    print(f"  ...đã tạo {n} công việc nội bộ")


# ---------------------------------------------------------------------------
def run():
    _quiet_mode()
    n_students = int(os.environ.get("SEED_STUDENTS", "800"))
    year = int(os.environ.get("SEED_YEAR", str(getdate(today()).year - 1)))

    print(f"\n=== SEED education_erp: {n_students} học viên, năm {year} ===\n")

    print("1) Courses...")
    courses = _ensure_courses()
    print("2) Classrooms...")
    classrooms = _ensure_classrooms()
    print("3) Teachers...")
    teachers = _ensure_teachers()
    print(f"4) Students ({n_students})...")
    students = _ensure_students(n_students, year)
    print("5) Education Settings + Curriculum + Learning Materials...")
    _ensure_education_settings()
    _seed_curriculum(courses)
    print("6) Classes (1 năm)...")
    # Đủ lớp để phủ hết học viên (~18 HV/lớp), thêm hệ số để vài HV học >1 lớp.
    target_classes = int(os.environ.get(
        "SEED_CLASSES", str(max(8, round(n_students / 18 * 1.25)))))
    classes = _create_classes(courses, classrooms, teachers, year,
                              target_classes)
    _seed_learning_materials(courses, classes)
    print("7) Enrollments (submit) + Sessions + Attendance + Fees...")
    enrollments = _create_sessions_and_enroll(classes, students, year)
    print("8) Học tập: Assessment + Homework...")
    _seed_assessments(enrollments)
    _seed_homework(classes, enrollments)
    print("9) Tài chính mở rộng: Refund + Salary Slip...")
    _seed_refunds(enrollments)
    _seed_salary_slips(teachers, year)
    print("10) Vận hành: Guardian/Card + Deferment/Transfer + Booking + Task...")
    _seed_guardians_and_cards(students, year)
    _seed_deferments_transfers(enrollments, classes)
    _seed_room_bookings(classrooms, year)
    _seed_internal_tasks(year)
    print("11) Leads + Tư vấn + Hẹn + Test xếp lớp...")
    leads = _create_leads(year)
    _seed_consultations(leads, year)
    _seed_appointments(leads, year)
    _seed_placement_tests(leads, courses, year)
    print("12) Tính lại toàn bộ tiến độ/chuyên cần/điểm TB...")
    from edu.education_erp import metrics
    metrics.recompute_all_metrics()

    frappe.db.commit()
    print("\n✅ HOÀN TẤT seed dữ liệu 1 năm cho education_erp.")
    print(f"   Students: {len(students)} | Classes: {len(classes)} | "
          f"Enrollments: {len(enrollments)} | Teachers: {len(teachers)} | "
          f"Courses: {len(courses)} | Leads: {len(leads)}")


# ---------------------------------------------------------------------------
def wipe():
    """Xoá nhanh toàn bộ dữ liệu giao dịch seed bằng SQL trực tiếp
    (giữ Course/Classroom/Teacher). Xoá cả child table liên quan."""
    _quiet_mode()
    # Thứ tự xoá: phụ thuộc/ con trước, cha sau.
    # parent doctype -> các child doctype cần xoá theo (parentfield table)
    targets = [
        # --- Tư vấn & hẹn (phụ thuộc Student Lead) ---
        ("Consultation Log", []),
        ("Student Appointment", []),
        ("Placement Test", []),
        # --- Học tập (phụ thuộc Homework/Enrollment/Class/Session) ---
        ("Homework Submission", []),
        ("Homework", []),
        ("Student Assessment", []),
        ("Learning Material", []),
        ("Lesson Template", []),
        ("Curriculum Module", []),
        # --- Tài chính (phụ thuộc Invoice/Enrollment/Teacher) ---
        ("Fee Refund", []),
        ("Teacher Salary Slip", []),
        ("Fee Payment", ["Fee Payment Reference"]),
        ("Fee Invoice", ["Fee Invoice Item"]),
        ("Fee Schedule", []),
        # --- Vận hành (phụ thuộc Student/Class) ---
        ("Onboarding Task", []),
        ("Student Card", []),
        ("Student Deferment", []),
        ("Class Transfer", []),
        ("Room Booking", []),
        ("Internal Task", []),
        # --- Học tập theo buổi/lớp ---
        ("Student Attendance", []),
        ("Class Session", []),
        ("Program Enrollment", []),
        ("Class", []),
        # --- Lead & Student & Guardian ---
        ("Student Lead", []),
        ("Student", ["Student Sibling"]),
        ("Guardian", []),
    ]
    for parent, children in targets:
        n = frappe.db.count(parent)
        for child in children:
            frappe.db.sql(f"DELETE FROM `tab{child}` WHERE parenttype=%s", parent)
        frappe.db.delete(parent)
        frappe.db.commit()
        print(f"  Đã xoá {n} {parent}")
    print("\n🗑️  Đã xoá dữ liệu seed.")
