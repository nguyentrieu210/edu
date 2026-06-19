"""
Seed script - Tạo dữ liệu mẫu học viên cho education_erp
Chạy: bench --site erp.localhost execute edu.seed_students.run
"""

import frappe
from frappe.utils import now_datetime
import random

STUDENTS = [
    # name, dob, gender, phone, email, source, occupation, rating, msg_response, health, progress, avg_score
    ("Nguyễn Thu Hà",       "2001-03-15", "Nữ",  "0901234567", "ha.nguyen@gmail.com",       "Facebook",  "Sinh viên",         "5 Sao", "Tốt",        "Đang học đều",  "Buổi 12/30", 8.5),
    ("Trần Minh Khoa",      "1999-07-22", "Nam", "0912345678", "khoa.tran@gmail.com",       "Google",    "Nhân viên văn phòng","4 Sao", "Bình thường","Đang học đều",  "Buổi 8/30",  7.8),
    ("Lê Thị Bảo Châu",    "2003-11-05", "Nữ",  "0923456789", "chau.le@gmail.com",         "Website",   "Học sinh",          "5 Sao", "Tốt",        "Đang học đều",  "Buổi 20/30", 9.2),
    ("Phạm Quốc Bảo",      "2000-01-30", "Nam", "0934567890", "bao.pham@gmail.com",        "Facebook",  "Sinh viên",         "3 Sao", "Chậm",       "Cần theo dõi",  "Buổi 5/30",  6.1),
    ("Hoàng Phương Anh",   "1998-09-12", "Nữ",  "0945678901", "anh.hoang@gmail.com",       "Khác",      "Giáo viên",         "4 Sao", "Tốt",        "Đang học đều",  "Buổi 15/30", 8.0),
    ("Vũ Đức Mạnh",        "2002-04-18", "Nam", "0956789012", "manh.vu@gmail.com",         "Google",    "Sinh viên",         "4 Sao", "Bình thường","Đang học đều",  "Buổi 10/30", 7.5),
    ("Đỗ Thị Lan Anh",     "1997-12-03", "Nữ",  "0967890123", "lananh.do@gmail.com",       "Website",   "Kế toán",           "5 Sao", "Tốt",        "Đang học đều",  "Buổi 25/30", 9.5),
    ("Bùi Văn Hưng",       "2001-06-27", "Nam", "0978901234", "hung.bui@gmail.com",        "Facebook",  "Sinh viên",         "2 Sao", "Không trả lời","Cảnh báo",   "Buổi 2/30",  5.0),
    ("Nguyễn Thị Mai",     "2004-08-14", "Nữ",  "0989012345", "mai.nguyen2@gmail.com",     "Facebook",  "Học sinh",          "5 Sao", "Tốt",        "Đang học đều",  "Buổi 18/30", 8.8),
    ("Trịnh Đình Phúc",    "1996-02-09", "Nam", "0990123456", "phuc.trinh@gmail.com",      "Google",    "Lập trình viên",    "4 Sao", "Tốt",        "Đang học đều",  "Buổi 22/30", 8.3),
    ("Ngô Thị Hương",      "2003-05-20", "Nữ",  "0901111222", "huong.ngo@gmail.com",       "Website",   "Sinh viên",         "3 Sao", "Bình thường","Cần theo dõi",  "Buổi 7/30",  6.5),
    ("Lý Minh Tuấn",       "2000-10-11", "Nam", "0912222333", "tuan.ly@gmail.com",         "Khác",      "Nhân viên bán hàng","4 Sao", "Tốt",        "Đang học đều",  "Buổi 13/30", 7.9),
    ("Phan Thị Quỳnh Như", "1999-04-25", "Nữ",  "0923333444", "nhu.phan@gmail.com",        "Facebook",  "Marketing",         "5 Sao", "Tốt",        "Đang học đều",  "Buổi 28/30", 9.1),
    ("Đinh Công Sơn",      "2002-07-07", "Nam", "0934444555", "son.dinh@gmail.com",        "Google",    "Sinh viên",         "3 Sao", "Chậm",       "Cảnh báo",      "Buổi 3/30",  5.5),
    ("Võ Thị Kiều Oanh",  "1998-01-16", "Nữ",  "0945555666", "oanh.vo@gmail.com",         "Website",   "Nhân viên hành chính","5 Sao","Tốt",       "Đang học đều",  "Buổi 24/30", 8.7),
    ("Cao Văn Nghĩa",      "2001-09-03", "Nam", "0956666777", "nghia.cao@gmail.com",       "Facebook",  "Sinh viên",         "4 Sao", "Bình thường","Đang học đều",  "Buổi 16/30", 7.6),
    ("Trương Thị Bích Ngọc","2003-03-28","Nữ", "0967777888", "ngoc.truong@gmail.com",     "Khác",      "Học sinh",          "4 Sao", "Tốt",        "Đang học đều",  "Buổi 11/30", 8.1),
    ("Huỳnh Thanh Tùng",   "1997-11-19", "Nam", "0978888999", "tung.huynh@gmail.com",      "Google",    "Thiết kế đồ họa",   "3 Sao", "Không trả lời","Khẩn cấp",   "Buổi 1/30",  4.0),
    ("Mai Thị Thu Thảo",   "2002-06-08", "Nữ",  "0989999000", "thao.mai@gmail.com",        "Facebook",  "Sinh viên",         "5 Sao", "Tốt",        "Đang học đều",  "Buổi 19/30", 9.0),
    ("Nguyễn Văn Đức",    "2000-12-22", "Nam", "0900000111", "duc.nguyen2@gmail.com",     "Website",   "Kỹ sư xây dựng",   "4 Sao", "Tốt",        "Đang học đều",  "Buổi 21/30", 8.2),
    ("Lê Ngọc Hân",       "2004-02-14", "Nữ",  "0911111222", "han.le@gmail.com",          "Facebook",  "Học sinh",          "5 Sao", "Tốt",        "Đang học đều",  "Buổi 14/30", 8.6),
    ("Phạm Trung Hiếu",   "1999-08-31", "Nam", "0922222333", "hieu.pham@gmail.com",       "Google",    "Sinh viên",         "2 Sao", "Chậm",       "Ngừng học",     "Buổi 0/30",  0.0),
    ("Đặng Thị Mỹ Linh",  "2001-05-17", "Nữ",  "0933333444", "linh.dang@gmail.com",       "Website",   "Nhân viên ngân hàng","5 Sao","Tốt",        "Đang học đều",  "Buổi 27/30", 9.3),
    ("Bùi Quang Trung",   "2003-10-06", "Nam", "0944444555", "trung.bui@gmail.com",       "Khác",      "Học sinh",          "3 Sao", "Bình thường","Cần theo dõi",  "Buổi 6/30",  6.3),
    ("Nguyễn Thị Yến Nhi","1998-07-23", "Nữ",  "0955555666", "nhi.nguyen@gmail.com",      "Facebook",  "Y tá",              "4 Sao", "Tốt",        "Đang học đều",  "Buổi 17/30", 8.4),
    ("Tô Văn Lộc",        "2000-03-10", "Nam", "0966666777", "loc.to@gmail.com",          "Google",    "Lái xe",            "3 Sao", "Bình thường","Đang học đều",  "Buổi 9/30",  7.0),
    ("Vương Thị Lan",     "2002-01-05", "Nữ",  "0977777888", "lan.vuong@gmail.com",       "Website",   "Sinh viên",         "4 Sao", "Tốt",        "Đang học đều",  "Buổi 23/30", 8.9),
    ("Trần Hữu Phát",     "1997-06-14", "Nam", "0988888999", "phat.tran@gmail.com",       "Facebook",  "Buôn bán",          "4 Sao", "Tốt",        "Đang học đều",  "Buổi 20/30", 8.0),
    ("Hồ Thị Ngọc Trinh", "2003-09-02", "Nữ",  "0999999000", "trinh.ho@gmail.com",        "Khác",      "Học sinh",          "5 Sao", "Tốt",        "Đang học đều",  "Buổi 26/30", 9.4),
    ("Lê Quang Vinh",     "2001-11-28", "Nam", "0900111222", "vinh.le@gmail.com",         "Google",    "Sinh viên",         "4 Sao", "Bình thường","Đang học đều",  "Buổi 12/30", 7.7),
]


def run():
    frappe.flags.in_import = True
    created = 0
    skipped = 0

    for row in STUDENTS:
        (full_name, dob, gender, phone, email,
         source, occupation, rating, msg_response,
         health_status, progress, average_score) = row

        # Skip nếu đã tồn tại (theo tên + phone)
        existing = frappe.db.exists("Student", {"full_name": full_name, "phone": phone})
        if existing:
            skipped += 1
            print(f"  [SKIP] {full_name} đã tồn tại ({existing})")
            continue

        doc = frappe.new_doc("Student")
        doc.full_name        = full_name
        doc.date_of_birth    = dob
        doc.gender           = gender
        doc.phone            = phone
        doc.email            = email
        doc.source           = source
        doc.occupation       = occupation
        doc.rating           = rating
        doc.message_response = msg_response
        doc.health_status    = health_status
        doc.progress         = progress
        doc.average_score    = average_score
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        created += 1
        print(f"  [OK] Đã tạo: {doc.name} — {full_name}")

    print(f"\n✅ Xong! Đã tạo: {created} học viên | Bỏ qua (trùng): {skipped}")
