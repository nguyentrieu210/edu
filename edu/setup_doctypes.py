import frappe

def create_all():
    frappe.flags.in_import = True # To bypass some validations during creation

    create_doctype("Guardian", "Setup", "DocType for Guardian", [
        {"fieldname": "guardian_name", "fieldtype": "Data", "label": "Tên người giám hộ", "reqd": 1},
        {"fieldname": "phone", "fieldtype": "Data", "label": "Số điện thoại"}
    ])

    create_doctype("Education Settings", "Setup", "Global Settings for Education", [
        {"fieldname": "default_due_days", "fieldtype": "Int", "label": "Số ngày hạn nộp mặc định", "default": "15"}
    ], is_single=1)

    create_doctype("Student", "Setup", "Student Master", [
        {"fieldname": "full_name", "fieldtype": "Data", "label": "Họ và tên học viên", "reqd": 1},
        {"fieldname": "guardian", "fieldtype": "Link", "label": "Người giám hộ", "options": "Guardian"},
        {"fieldname": "progress", "fieldtype": "Data", "label": "Tiến độ học tập (Ví dụ: Buổi 8/30)"},
        {"fieldname": "attendance_status", "fieldtype": "Select", "label": "Trạng thái điểm danh", "options": "\nVắng có phép\nKhông phép"},
        {"fieldname": "average_score", "fieldtype": "Float", "label": "Điểm trung bình"},
        {"fieldname": "health_status", "fieldtype": "Select", "label": "Cảnh báo sức khỏe", "options": "Đang học đều\nCần theo dõi\nCảnh báo\nKhẩn cấp\nNgừng học", "default": "Đang học đều", "in_list_view": 1},
        {"fieldname": "date_of_birth", "fieldtype": "Date", "label": "Ngày sinh"},
        {"fieldname": "gender", "fieldtype": "Select", "label": "Giới tính", "options": "\nNam\nNữ\nKhác"},
        {"fieldname": "email", "fieldtype": "Data", "label": "Email"},
        {"fieldname": "phone", "fieldtype": "Data", "label": "Phone"},
        {"fieldname": "source", "fieldtype": "Select", "label": "Nguồn", "options": "\nWebsite\nFacebook\nGoogle\nKhác"},
        {"fieldname": "occupation", "fieldtype": "Data", "label": "Ngành nghề"},
        {"fieldname": "rating", "fieldtype": "Select", "label": "Đánh giá", "options": "\n1 Sao\n2 Sao\n3 Sao\n4 Sao\n5 Sao"},
        {"fieldname": "message_response", "fieldtype": "Select", "label": "Phản hồi tin nhắn", "options": "\nTốt\nBình thường\nChậm\nKhông trả lời"}
    ], naming_rule="Expression", autoname="STU-.YYYY.-.####")

    create_doctype("Student Sibling", "Setup", "Child table for siblings", [
        {"fieldname": "student_id", "fieldtype": "Link", "label": "Mã học viên", "options": "Student", "in_list_view": 1},
        {"fieldname": "same_institute", "fieldtype": "Check", "label": "Học cùng trung tâm", "in_list_view": 1}
    ], is_child=1)

    # Now add the siblings table to Student
    student = frappe.get_doc("DocType", "Student")
    student.append("fields", {
        "fieldname": "siblings",
        "fieldtype": "Table",
        "label": "Anh chị em ruột",
        "options": "Student Sibling"
    })
    student.save()

    create_doctype("Student Lead", "CRM", "Học viên tiềm năng", [
        {"fieldname": "lead_name", "fieldtype": "Data", "label": "Tên ứng viên", "reqd": 1, "in_list_view": 1},
        {"fieldname": "phone", "fieldtype": "Data", "label": "Số điện thoại", "in_list_view": 1},
        {"fieldname": "email", "fieldtype": "Data", "label": "Email"},
        {"fieldname": "source", "fieldtype": "Select", "label": "Nguồn đăng ký", "options": "Website\nFacebook\nHotline\nWord of Mouth\nOther", "default": "Website"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "New\nConsulting\nTesting\nTrial\nEnrolled\nLost", "default": "New", "in_list_view": 1},
        {"fieldname": "date_of_birth", "fieldtype": "Date", "label": "Ngày sinh"},
        {"fieldname": "gender", "fieldtype": "Select", "label": "Giới tính", "options": "\nNam\nNữ\nKhác"},
        {"fieldname": "occupation", "fieldtype": "Data", "label": "Ngành nghề"},
        {"fieldname": "guardian_name", "fieldtype": "Data", "label": "Tên người giám hộ"},
        {"fieldname": "guardian_phone", "fieldtype": "Data", "label": "Số điện thoại người giám hộ"},
        {"fieldname": "lost_reason", "fieldtype": "Text", "label": "Lý do thất bại"}
    ], naming_rule="Expression", autoname="LED-.YYYY.-.####")

    create_doctype("Consultation Log", "CRM", "Nhật ký tư vấn", [
        {"fieldname": "lead", "fieldtype": "Link", "label": "Ứng viên", "options": "Student Lead", "reqd": 1, "in_list_view": 1},
        {"fieldname": "contact_date", "fieldtype": "Date", "label": "Ngày liên hệ", "reqd": 1, "in_list_view": 1},
        {"fieldname": "notes", "fieldtype": "Text Editor", "label": "Nội dung trao đổi"},
        {"fieldname": "next_follow_up", "fieldtype": "Date", "label": "Hẹn ngày gọi lại", "in_list_view": 1}
    ])

    create_doctype("Placement Test", "CRM", "Bài thi xếp lớp", [
        {"fieldname": "lead", "fieldtype": "Link", "label": "Ứng viên", "options": "Student Lead", "reqd": 1, "in_list_view": 1},
        {"fieldname": "test_date", "fieldtype": "Date", "label": "Ngày thi", "reqd": 1, "in_list_view": 1},
        {"fieldname": "score", "fieldtype": "Float", "label": "Điểm số", "reqd": 1, "in_list_view": 1},
        {"fieldname": "recommended_course", "fieldtype": "Link", "label": "Khóa học đề xuất", "options": "Course"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Pending\nEvaluated\nEnrolled", "default": "Pending", "in_list_view": 1}
    ], naming_rule="Expression", autoname="PLT-.YYYY.-.####")

    create_doctype("Student Appointment", "CRM", "Lịch hẹn tư vấn", [
        {"fieldname": "lead", "fieldtype": "Link", "label": "Ứng viên", "options": "Student Lead", "reqd": 1, "in_list_view": 1},
        {"fieldname": "appointment_date", "fieldtype": "Date", "label": "Ngày hẹn", "reqd": 1, "in_list_view": 1},
        {"fieldname": "appointment_time", "fieldtype": "Time", "label": "Giờ hẹn"},
        {"fieldname": "purpose", "fieldtype": "Data", "label": "Mục đích", "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Scheduled\nCompleted\nCancelled\nRescheduled", "default": "Scheduled", "in_list_view": 1}
    ], naming_rule="Expression", autoname="APT-.YYYY.-.####")

    create_doctype("Teacher", "Core", "Hồ sơ giáo viên", [
        {"fieldname": "teacher_name", "fieldtype": "Data", "label": "Tên giáo viên", "reqd": 1, "in_list_view": 1},
        {"fieldname": "phone", "fieldtype": "Data", "label": "Số điện thoại", "in_list_view": 1},
        {"fieldname": "email", "fieldtype": "Data", "label": "Email"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Active\nInactive", "default": "Active", "in_list_view": 1}
    ], naming_rule="Expression", autoname="TCH-.####")

    create_doctype("Course", "Core", "Khóa học", [
        {"fieldname": "course_name", "fieldtype": "Data", "label": "Tên khóa học", "reqd": 1, "in_list_view": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Mô tả khóa học"},
        {"fieldname": "base_fee", "fieldtype": "Currency", "label": "Học phí cơ bản", "in_list_view": 1}
    ])

    create_doctype("Classroom", "Core", "Phòng học", [
        {"fieldname": "room_name", "fieldtype": "Data", "label": "Tên phòng học", "reqd": 1, "in_list_view": 1},
        {"fieldname": "capacity", "fieldtype": "Int", "label": "Sức chứa tối đa", "in_list_view": 1}
    ])

    create_doctype("Class", "Core", "Lớp học", [
        {"fieldname": "class_name", "fieldtype": "Data", "label": "Tên lớp học", "reqd": 1, "in_list_view": 1},
        {"fieldname": "course", "fieldtype": "Link", "label": "Khóa học", "options": "Course", "reqd": 1, "in_list_view": 1},
        {"fieldname": "teacher", "fieldtype": "Link", "label": "Giáo viên chủ nhiệm", "options": "Teacher", "in_list_view": 1},
        {"fieldname": "start_date", "fieldtype": "Date", "label": "Ngày khai giảng"},
        {"fieldname": "schedule_template", "fieldtype": "Select", "label": "Mẫu lịch học", "options": "\n2-4-6\n3-5-7\nT7-CN\nCustom"},
        {"fieldname": "start_time", "fieldtype": "Time", "label": "Giờ bắt đầu"},
        {"fieldname": "end_time", "fieldtype": "Time", "label": "Giờ kết thúc"},
        {"fieldname": "total_sessions", "fieldtype": "Int", "label": "Tổng số buổi học"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Upcoming\nOngoing\nCompleted\nClosed", "default": "Upcoming", "in_list_view": 1}
    ], naming_rule="Expression", autoname="CLS-.YYYY.-.####")

    create_doctype("Class Session", "Core", "Lịch học theo ca", [
        {"fieldname": "class_id", "fieldtype": "Link", "label": "Lớp học", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "lesson_topic", "fieldtype": "Data", "label": "Nội dung bài học", "in_list_view": 1},
        {"fieldname": "classroom", "fieldtype": "Link", "label": "Phòng học", "options": "Classroom", "in_list_view": 1},
        {"fieldname": "session_date", "fieldtype": "Date", "label": "Ngày học", "reqd": 1, "in_list_view": 1},
        {"fieldname": "start_time", "fieldtype": "Time", "label": "Giờ bắt đầu", "reqd": 1, "in_list_view": 1},
        {"fieldname": "end_time", "fieldtype": "Time", "label": "Giờ kết thúc", "reqd": 1},
        {"fieldname": "teacher", "fieldtype": "Link", "label": "Giáo viên dạy", "options": "Teacher"},
        {"fieldname": "teacher_attendance_status", "fieldtype": "Select", "label": "Điểm danh GV", "options": "\nPresent\nAbsent", "default": ""}
    ])

    create_doctype("Program Enrollment", "Core", "Enroll student to a program", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "class_id", "fieldtype": "Link", "label": "Lớp học", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "enrollment_type", "fieldtype": "Select", "label": "Loại đăng ký", "options": "Official\nTrial", "default": "Official", "in_list_view": 1},
        {"fieldname": "enrollment_date", "fieldtype": "Date", "label": "Ngày nhập học", "reqd": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="ENR-.YYYY.-.####")

    create_doctype("Fee Schedule", "Core", "Schedule for Fee Collection", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "program_enrollment", "fieldtype": "Link", "label": "Lịch sử đăng ký học", "options": "Program Enrollment"},
        {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Tổng học phí", "reqd": 1, "in_list_view": 1},
        {"fieldname": "due_date", "fieldtype": "Date", "label": "Hạn thanh toán", "reqd": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Draft\nInvoice Pending\nInvoiced\nCancelled", "default": "Draft"}
    ], is_submittable=1, naming_rule="Expression", autoname="FEE-.YYYY.-.####")

    create_doctype("Fee Invoice Item", "Core", "Chi tiết hóa đơn học phí", [
        {"fieldname": "item_name", "fieldtype": "Data", "label": "Tên khoản thu", "reqd": 1, "in_list_view": 1},
        {"fieldname": "amount", "fieldtype": "Currency", "label": "Thành tiền", "reqd": 1, "in_list_view": 1}
    ], is_child=1)

    create_doctype("Fee Invoice", "Core", "Fee Invoice for student", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "program_enrollment", "fieldtype": "Link", "label": "Lịch sử đăng ký học", "options": "Program Enrollment"},
        {"fieldname": "fee_schedule", "fieldtype": "Link", "label": "Lịch thu phí", "options": "Fee Schedule", "read_only": 1},
        {"fieldname": "posting_date", "fieldtype": "Date", "label": "Ngày lập hóa đơn", "reqd": 1},
        {"fieldname": "due_date", "fieldtype": "Date", "label": "Hạn nộp học phí", "reqd": 1},
        {"fieldname": "items", "fieldtype": "Table", "label": "Chi tiết khoản thu", "options": "Fee Invoice Item"},
        {"fieldname": "discount_amount", "fieldtype": "Currency", "label": "Số tiền giảm giá", "default": "0"},
        {"fieldname": "discount_reason", "fieldtype": "Data", "label": "Lý do giảm giá"},
        {"fieldname": "tax_amount", "fieldtype": "Currency", "label": "Thuế VAT", "default": "0"},
        {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Tổng tiền", "reqd": 1, "in_list_view": 1},
        {"fieldname": "outstanding_amount", "fieldtype": "Currency", "label": "Số tiền còn nợ", "read_only": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Unpaid\nPartially Paid\nPaid\nOverdue\nCancelled", "default": "Unpaid", "in_list_view": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="INV-.YYYY.-.####")

    create_doctype("Fee Payment Reference", "Core", "Fee Payment Reference detail", [
        {"fieldname": "invoice", "fieldtype": "Link", "label": "Hóa đơn liên kết", "options": "Fee Invoice", "reqd": 1, "in_list_view": 1},
        {"fieldname": "allocated_amount", "fieldtype": "Currency", "label": "Số tiền thanh toán", "reqd": 1, "in_list_view": 1}
    ], is_child=1)

    create_doctype("Fee Payment", "Core", "Fee payment receipt", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "posting_date", "fieldtype": "Date", "label": "Ngày lập phiếu", "reqd": 1},
        {"fieldname": "payment_date", "fieldtype": "Date", "label": "Ngày đóng học phí", "reqd": 1},
        {"fieldname": "payment_method", "fieldtype": "Select", "label": "Phương thức đóng", "options": "Cash\nBank Transfer\nCard\nOther", "default": "Cash"},
        {"fieldname": "amount", "fieldtype": "Currency", "label": "Số tiền đóng", "reqd": 1, "in_list_view": 1},
        {"fieldname": "reference_no", "fieldtype": "Data", "label": "Mã giao dịch / Số tham chiếu"},
        {"fieldname": "reference_date", "fieldtype": "Date", "label": "Ngày giao dịch"},
        {"fieldname": "references", "fieldtype": "Table", "label": "Chi tiết hóa đơn thanh toán", "options": "Fee Payment Reference"}
    ], is_submittable=1, naming_rule="Expression", autoname="PAY-.YYYY.-.####")

    create_doctype("Student Attendance", "Operations", "Điểm danh học viên theo buổi", [
        {"fieldname": "class_id", "fieldtype": "Link", "label": "Lớp học", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "attendance_date", "fieldtype": "Date", "label": "Ngày điểm danh", "reqd": 1, "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Present\nAbsent with Permission\nAbsent without Permission", "default": "Present", "in_list_view": 1}
    ], naming_rule="Expression", autoname="ATT-.YYYY.-.####")

    create_doctype("Student Assessment", "Operations", "Kết quả học tập", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "class_id", "fieldtype": "Link", "label": "Lớp học", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "assessment_name", "fieldtype": "Data", "label": "Tên bài kiểm tra", "reqd": 1, "in_list_view": 1},
        {"fieldname": "score", "fieldtype": "Float", "label": "Điểm số", "reqd": 1, "in_list_view": 1},
        {"fieldname": "notes", "fieldtype": "Text", "label": "Nhận xét của giáo viên"}
    ], naming_rule="Expression", autoname="ASM-.YYYY.-.####")

    create_doctype("Student Deferment", "Operations", "Đơn xin bảo lưu", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "class_id", "fieldtype": "Link", "label": "Lớp học đang học", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "leave_from_date", "fieldtype": "Date", "label": "Bảo lưu từ ngày", "reqd": 1},
        {"fieldname": "leave_to_date", "fieldtype": "Date", "label": "Đến ngày", "reqd": 1},
        {"fieldname": "reason", "fieldtype": "Text", "label": "Lý do bảo lưu"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Pending\nApproved\nRejected", "default": "Pending", "in_list_view": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="DEF-.YYYY.-.####")

    create_doctype("Class Transfer", "Operations", "Đơn xin chuyển lớp", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "from_class", "fieldtype": "Link", "label": "Từ lớp", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "to_class", "fieldtype": "Link", "label": "Sang lớp", "options": "Class", "reqd": 1, "in_list_view": 1},
        {"fieldname": "transfer_date", "fieldtype": "Date", "label": "Ngày chuyển", "reqd": 1},
        {"fieldname": "reason", "fieldtype": "Text", "label": "Lý do chuyển"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Pending\nApproved\nRejected", "default": "Pending", "in_list_view": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="TRF-.YYYY.-.####")

    create_doctype("Fee Refund", "Core", "Phiếu hoàn phí", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "invoice_reference", "fieldtype": "Link", "label": "Hóa đơn gốc", "options": "Fee Invoice", "reqd": 1},
        {"fieldname": "refund_amount", "fieldtype": "Currency", "label": "Số tiền hoàn", "reqd": 1, "in_list_view": 1},
        {"fieldname": "refund_date", "fieldtype": "Date", "label": "Ngày hoàn tiền", "reqd": 1},
        {"fieldname": "reason", "fieldtype": "Text", "label": "Lý do hoàn phí"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Draft\nCompleted\nCancelled", "default": "Draft", "in_list_view": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="REF-.YYYY.-.####")

    create_doctype("Teacher Salary Slip", "HR", "Phiếu lương Giáo viên", [
        {"fieldname": "teacher", "fieldtype": "Link", "label": "Giáo viên", "options": "Teacher", "reqd": 1, "in_list_view": 1},
        {"fieldname": "month", "fieldtype": "Select", "label": "Tháng", "options": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12", "reqd": 1, "in_list_view": 1},
        {"fieldname": "year", "fieldtype": "Int", "label": "Năm", "reqd": 1, "in_list_view": 1},
        {"fieldname": "total_sessions_taught", "fieldtype": "Int", "label": "Tổng ca dạy", "read_only": 1, "in_list_view": 1},
        {"fieldname": "rate_per_session", "fieldtype": "Currency", "label": "Lương 1 ca", "reqd": 1},
        {"fieldname": "total_salary", "fieldtype": "Currency", "label": "Tổng lương", "read_only": 1, "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Draft\nUnpaid\nPaid\nCancelled", "default": "Draft", "in_list_view": 1}
    ], is_submittable=1, naming_rule="Expression", autoname="SAL-.YYYY.-.####")

    create_doctype("Student Card", "Operations", "Thẻ học viên", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "card_number", "fieldtype": "Data", "label": "Mã thẻ / Barcode", "reqd": 1, "in_list_view": 1},
        {"fieldname": "issue_date", "fieldtype": "Date", "label": "Ngày cấp", "reqd": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Active\nLost\nRevoked", "default": "Active", "in_list_view": 1}
    ])

    create_doctype("Onboarding Task", "Operations", "Công việc nhập học", [
        {"fieldname": "student", "fieldtype": "Link", "label": "Học viên", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "program_enrollment", "fieldtype": "Link", "label": "Đăng ký học", "options": "Program Enrollment"},
        {"fieldname": "task_name", "fieldtype": "Data", "label": "Tên công việc (Phát sách, Zalo...)", "reqd": 1, "in_list_view": 1},
        {"fieldname": "is_completed", "fieldtype": "Check", "label": "Đã hoàn thành", "in_list_view": 1}
    ])

    create_doctype("Room Booking", "Operations", "Quản lý thuê phòng", [
        {"fieldname": "classroom", "fieldtype": "Link", "label": "Phòng học", "options": "Classroom", "reqd": 1, "in_list_view": 1},
        {"fieldname": "booking_date", "fieldtype": "Date", "label": "Ngày đặt", "reqd": 1, "in_list_view": 1},
        {"fieldname": "start_time", "fieldtype": "Time", "label": "Giờ bắt đầu", "reqd": 1, "in_list_view": 1},
        {"fieldname": "end_time", "fieldtype": "Time", "label": "Giờ kết thúc", "reqd": 1},
        {"fieldname": "purpose", "fieldtype": "Data", "label": "Mục đích sử dụng"},
        {"fieldname": "booked_by", "fieldtype": "Data", "label": "Người đặt", "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "Booked\nCompleted\nCancelled", "default": "Booked", "in_list_view": 1}
    ], naming_rule="Expression", autoname="RBK-.YYYY.-.####")

    create_doctype("Internal Task", "Core", "Giao việc nội bộ", [
        {"fieldname": "title", "fieldtype": "Data", "label": "Tiêu đề công việc", "reqd": 1, "in_list_view": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Mô tả chi tiết"},
        {"fieldname": "assigned_to", "fieldtype": "Data", "label": "Người phụ trách (Email/Tên)", "in_list_view": 1},
        {"fieldname": "due_date", "fieldtype": "Date", "label": "Hạn chót", "in_list_view": 1},
        {"fieldname": "priority", "fieldtype": "Select", "label": "Độ ưu tiên", "options": "Low\nMedium\nHigh", "default": "Medium", "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Trạng thái", "options": "To Do\nIn Progress\nDone", "default": "To Do", "in_list_view": 1}
    ])

    frappe.db.commit()
    print("All DocTypes created successfully!")

def create_doctype(name, module, description, fields, is_single=0, is_child=0, is_submittable=0, naming_rule=None, autoname=None):
    if frappe.db.exists("DocType", name):
        # Set custom = 1 in DB first to prevent delete_doc from deleting physical files
        frappe.db.set_value("DocType", name, "custom", 1)
        frappe.db.commit()
        frappe.delete_doc("DocType", name, force=1)
    
    permissions = []
    if not is_child:
        perm = {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "report": 1,
            "share": 1
        }
        if is_submittable:
            perm.update({
                "submit": 1,
                "cancel": 1,
                "amend": 1
            })
        permissions.append(perm)

    doc = frappe.get_doc({
        "doctype": "DocType",
        "module": "Education ERP",
        "custom": 1,
        "name": name,
        "issingle": is_single,
        "istable": is_child,
        "is_submittable": is_submittable,
        "fields": fields,
        "permissions": permissions
    })
    if naming_rule:
        doc.naming_rule = naming_rule
    if autoname:
        doc.autoname = autoname
    doc.insert(ignore_permissions=True)
    print(f"Created DocType: {name}")
