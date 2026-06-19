# TRACKLOG — Education ERP (Quản lý Học phí & Học viên)

Nhật ký tiến độ phát triển phân hệ Quản lý Đào tạo & Học phí (Education ERP). Múi giờ: +07.

---

## 2026-06-19 (lần 2) — **Trang Thẻ Học Viên, Lịch Hẹn & Tái sắp xếp Menu** ✅

**Nội dung thực hiện:**
- **[ADD] `StudentCard.vue`:** Trang Thẻ học viên nội bộ (không còn link external sang Desk):
  - Cấp thẻ mới, gia hạn thẻ, in thẻ
  - Hiển thị dạng Card trực quan với màu gradient theo trạng thái (Hoạt động / Hết hạn / Tạm dừng)
  - Stats: Tổng thẻ, Đang hoạt động, Hết hạn, Sắp hết hạn (trong 30 ngày)
- **[ADD] `Appointments.vue`:** Trang Lịch hẹn tư vấn nội bộ:
  - Danh sách lịch hẹn dạng bảng + chuyển đổi Calendar View
  - Banner "Hôm nay" hiển thị các lịch hẹn trong ngày
  - Thống kê: Sắp tới, Hoàn thành, Đã hủy
  - Hành động nhanh: Hoàn thành (✓) / Hủy (✗)
- **[UPDATE] `App.vue` + `router.js`:** Sắp xếp menu đúng thứ tự theo ảnh thiết kế:
  - `Dashboard` → `Sale & Lead` (Lead, Lịch hẹn, Pipeline, Học thử, Dashboard)
  - → `Học viên & Thẻ` (Học viên, Thẻ, Onboarding)
  - → `Lớp & Đào tạo` (Hiệu suất, Lịch lớp, Chấm công, Giáo viên, Khóa học)
  - → `Tài chính` (Hóa đơn, Phiếu thu)
  - → `Nhân sự & Lương` (placeholder)
  - → `Vận hành` (Thuê phòng)
  - → `Build & Lean` (Viral Lab, Task Board)
- **[FIX]** Route `/appointments` và `/student-card` chuyển sang nội bộ SPA

---

## 2026-06-19 — **Sắp xếp Sidebar Nhóm Menu & Cải thiện Trải nghiệm Người dùng** ✅

**Nội dung thực hiện:**
- **Tái cấu trúc Sidebar (`App.vue`):** Chuyển đổi giao diện Sidebar từ dạng phẳng (Flat List) nền tối sang giao diện **phân nhóm có thể đóng/mở (Grouped Expandable Sidebar)** nền sáng (`bg-white`), chuẩn hóa theo hình mẫu thực tế:
  - **Thuê Phòng:** `Phòng học / Đặt phòng` (`/room-booking`).
  - **Tài chính:** `Hóa đơn` (`/invoices`), `Phiếu thu` (`/payments`).
  - **Lớp & Đào tạo:** `Hiệu suất (Bảng điểm)` (`/assessments`), `Lịch lớp (Lớp học)` (`/classes`), `Chấm công & Điểm danh` (`/attendance`), `Giáo viên` (`/teachers`), `Khóa học` (`/courses`).
  - **Học viên & Thẻ:** `Học viên` (`/students`), `Thẻ học viên` (Link tới Desk), `Onboarding` (`/onboarding`).
  - **Sale & Lead:** `Lead tiềm năng` (`/crm`), `Lịch hẹn` (Link tới Desk), `Pipeline` (`/crm`), `Dashboard` (`/`).
  - **Vận hành:** `Task Board (Giao việc)` (`/task-board`).
- **Tích hợp liên kết Desk:** Thiết lập các mục chưa có giao diện SPA (`Thẻ học viên`, `Lịch hẹn`) tự động mở liên kết trực tiếp sang danh sách DocType trong Frappe Desk để giáo vụ thao tác liền mạch.

---

## 2026-06-19 — **Sửa lỗi routing F5 (404) & Nâng cấp Giao diện 3 Cột Học Viên** ✅

**Nội dung thực hiện:**
- **Sửa lỗi F5 (Page not found):** Bổ sung cấu trúc `website_route_rules` vào `hooks.py` để định tuyến tất cả các sub-paths của SPA về đúng file Jinja `education_app.html`. Thực hiện xóa cache và khởi động lại container Frappe để áp dụng cấu hình.
- **Sửa lỗi thêm Lead:** Cải tiến hàm `saveLead` trong `CRMBoard.vue`, hiển thị chính xác lỗi backend trả về (trùng tên, thiếu trường, phân quyền...) thay vì chỉ báo `"Lỗi"` chung chung.
- **Giao diện 3 Cột Học viên:** Tái thiết kế toàn bộ `Students.vue` sang Grid 3 cột chuẩn Base/Lark:
  - **Cột 1 (Trái):** Danh sách học viên rút gọn, thanh tìm kiếm thời gian thực.
  - **Cột 2 (Giữa):** Chi tiết hồ sơ học viên hiển thị đầy đủ thông tin cá nhân.
  - **Cột 3 (Phải):** Biểu đồ phễu SVG biểu diễn 5 nấc sức khỏe điểm danh (`Đang học đều`, `Cần theo dõi`, `Cảnh báo`, `Khẩn cấp`, `Ngừng học`).
- **Cập nhật Database:** Bổ sung các trường thông tin cá nhân mới vào DocType `Student`: Ngày sinh (`date_of_birth`), Giới tính (`gender`), Email, Số điện thoại (`phone`), Nguồn (`source`), Ngành nghề (`occupation`), Đánh giá (`rating`), Phản hồi tin nhắn (`message_response`).

---

## 2026-06-18 — **Phát triển Mở rộng All-in-One & Tự động hóa Backend** ✅

**Nội dung thực hiện:**
- **CRM Kanban (`CRMBoard.vue`):** Bảng Kanban kéo thả trạng thái của Lead tiềm năng.
- **Quy trình Nhập học (`Onboarding.vue`):** Tự động sinh `Onboarding Task` (Checklist nhận tài liệu, add Zalo...) ngay khi học viên đăng ký lớp.
- **Đặt phòng học (`RoomBooking.vue`):** Hệ thống đặt phòng học và kiểm tra trùng lặp thời gian thực.
- **Bảng việc nội bộ (`TaskBoard.vue`):** Quản lý và giao việc cho Giáo viên/Nhân viên.
- **Cảnh báo Sức khỏe Học viên:** Viết logic Python đếm số ngày vắng mặt liên tiếp để tự động cập nhật trạng thái sức khỏe học viên (`health_status`).

---

## 2026-06-15 — **Xây dựng Giao diện Học vụ & Tài chính Cơ bản (Phase 3 & 4)** ✅

**Nội dung thực hiện:**
- **Quản lý Đào tạo:** Tạo các trang Quản lý Giáo viên (`Teachers.vue`), Khóa học (`Courses.vue`), Lớp học (`Classes.vue`), Điểm danh (`Attendance.vue`), Bảng điểm (`Assessments.vue`).
- **Tự động sinh Lịch học:** Thuật toán tự sinh lịch học dựa trên các thứ trong tuần (2-4-6, 3-5-7) và ca học.
- **Tài chính học phí:** Trang hóa đơn học phí (`Invoices.vue`) hỗ trợ chi tiết các khoản thu, thuế VAT, chiết khấu và lịch sử phiếu thu (`Payments.vue`).
- **Biên dịch hệ thống:** Thiết lập build pipeline Vue 3, copy asset tự động và liên kết sang Frappe site.

---

## 2026-06-10 — **Kiến trúc Pure Frappe & Việt hóa Toàn diện (Phase 1 & 2)** ✅

**Bối cảnh:** Chuyển đổi từ mô hình phụ thuộc ERPNext sang kiến trúc Pure Frappe nhẹ nhàng, tự định nghĩa DocType và Controller để tránh gánh nặng dữ liệu.

**Nội dung thực hiện:**
- **Database Schema:** Thiết kế và chạy script tạo các DocType tùy biến: `Guardian`, `Student`, `Fee Schedule`, `Fee Invoice`, `Fee Payment`, `Student Attendance`, `Student Assessment`...
- **Python Controllers:** Viết logic phân bổ học phí khi tạo phiếu thu, cập nhật công nợ học viên thời gian thực khi đóng tiền hoặc hủy phiếu thu.
- **Việt hóa hệ thống:** Tạo từ điển `vi.csv` dịch toàn bộ tên DocType, giá trị lựa chọn (Draft, Paid, Bank Transfer...). Dịch toàn bộ nhãn hiển thị trong script cài đặt.
- **Kiểm thử tự động:** Hoàn thành script kiểm thử `test_flow.py` chạy qua toàn bộ chu trình nhập học -> thu tiền -> hủy thu tiền thành công 100%.
