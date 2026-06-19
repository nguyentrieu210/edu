import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

ACTIVE_STATUS = "Active"


class ProgramEnrollment(Document):
    # Type Annotations for v15+
    student: str
    class_id: str
    enrollment_type: str
    enrollment_status: str
    enrollment_date: str
    list_price: float
    discount_type: str | None
    discount_value: float
    discount_reason: str | None
    net_fee: float
    installment_count: int

    def validate(self) -> None:
        if not self.enrollment_status:
            self.enrollment_status = "Pending"
        self._compute_fee_snapshot()

    def before_submit(self) -> None:
        # Snapshot học phí được chốt tại thời điểm submit và không đọc lại giá hiện tại sau đó.
        self._compute_fee_snapshot()
        if self.class_id:
            frappe.db.sql("select name from `tabClass` where name=%s for update", self.class_id)
        self._guard_duplicate_active()
        self._guard_capacity()
        self.enrollment_status = ACTIVE_STATUS

    def on_submit(self) -> None:
        # Toàn bộ chạy trong transaction của request submit; lỗi bất kỳ bước nào -> rollback.
        self.generate_onboarding_tasks()
        self.create_fee_schedule()

    # ----- Helpers -------------------------------------------------------

    def _compute_fee_snapshot(self) -> None:
        """Áp dụng thứ tự ưu tiên giá: list_price nhập tay > Class.standard_fee > Course.base_fee."""
        if not flt(self.list_price):
            list_price = 0.0
            if self.class_id:
                cls = frappe.db.get_value(
                    "Class", self.class_id, ["standard_fee", "course"], as_dict=True
                )
                if cls:
                    list_price = flt(cls.standard_fee)
                    if not list_price and cls.course:
                        list_price = flt(frappe.db.get_value("Course", cls.course, "base_fee"))
            self.list_price = list_price

        discount = 0.0
        if self.discount_type == "Percent":
            discount = flt(self.list_price) * flt(self.discount_value) / 100.0
        elif self.discount_type == "Amount":
            discount = flt(self.discount_value)

        self.net_fee = max(0.0, flt(self.list_price) - discount)
        if not self.installment_count or int(self.installment_count) < 1:
            self.installment_count = 1

    def _guard_duplicate_active(self) -> None:
        existing = frappe.db.exists(
            "Program Enrollment",
            {
                "student": self.student,
                "class_id": self.class_id,
                "docstatus": 1,
                "enrollment_status": ACTIVE_STATUS,
                "name": ["!=", self.name or ""],
            },
        )
        if existing:
            frappe.throw(
                f"Học viên {self.student} đã có đăng ký đang hoạt động ({existing}) trong lớp {self.class_id}.",
                title="Trùng đăng ký",
            )

    def _guard_capacity(self) -> None:
        max_capacity = frappe.db.get_value("Class", self.class_id, "max_capacity")
        if not max_capacity:
            return
        active_count = frappe.db.count(
            "Program Enrollment",
            {"class_id": self.class_id, "docstatus": 1, "enrollment_status": ACTIVE_STATUS},
        )
        if active_count >= int(max_capacity):
            frappe.throw(
                f"Lớp {self.class_id} đã đủ sĩ số ({active_count}/{int(max_capacity)}).",
                title="Vượt sĩ số",
            )

    def generate_onboarding_tasks(self) -> None:
        tasks = [
            "Phát bộ tài liệu & giáo trình",
            "Cấp phát thẻ học viên",
            "Thêm vào Group Zalo lớp",
            "Phổ biến nội quy trung tâm",
        ]
        for t in tasks:
            frappe.get_doc(
                {
                    "doctype": "Onboarding Task",
                    "student": self.student,
                    "program_enrollment": self.name,
                    "task_name": t,
                    "is_completed": 0,
                }
            ).insert()

    def create_fee_schedule(self) -> str | None:
        """Sinh lịch thu từ snapshot net_fee và submit để tạo hóa đơn (Invoice docstatus=1)."""
        if flt(self.net_fee) <= 0:
            return None
        if frappe.db.exists(
            "Fee Schedule", {"program_enrollment": self.name, "docstatus": ["<", 2]}
        ):
            return None
        sched = frappe.get_doc(
            {
                "doctype": "Fee Schedule",
                "student": self.student,
                "program_enrollment": self.name,
                "total_amount": flt(self.net_fee),
                "due_date": nowdate(),
                "status": "Draft",
            }
        )
        sched.insert()
        sched.submit()  # on_submit -> make_invoice() tạo & submit Fee Invoice
        return sched.name
