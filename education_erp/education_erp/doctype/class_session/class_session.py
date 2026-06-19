from datetime import time as _time, timedelta as _timedelta

import frappe
from frappe.model.document import Document


def _seconds(value):
    """Chuẩn hóa giá trị Time (str / datetime.time / timedelta) về số giây trong ngày."""
    if value is None or value == "":
        return None
    if isinstance(value, _timedelta):
        return int(value.total_seconds())
    if isinstance(value, _time):
        return value.hour * 3600 + value.minute * 60 + value.second
    parts = str(value).split(":")
    try:
        nums = [int(float(p)) for p in parts]
    except (ValueError, TypeError):
        return None
    nums += [0, 0, 0]
    return nums[0] * 3600 + nums[1] * 60 + nums[2]


def _overlaps(a_start, a_end, b_start, b_end):
    # Trùng khi: new_start < existing_end AND new_end > existing_start
    return a_start < b_end and a_end > b_start


def find_session_conflicts(
    session_date,
    start_time,
    end_time,
    teacher=None,
    classroom=None,
    exclude_name=None,
    exclude_class=None,
):
    """Trả về danh sách buổi học bị giao thời gian theo giáo viên hoặc phòng trong cùng ngày."""
    conflicts = []
    s_start, s_end = _seconds(start_time), _seconds(end_time)
    if s_start is None or s_end is None or not session_date:
        return conflicts

    targets = []
    if teacher:
        targets.append(("teacher", teacher, "giáo viên"))
    if classroom:
        targets.append(("classroom", classroom, "phòng học"))

    for field, value, label in targets:
        filters = {
            field: value,
            "session_date": session_date,
            "session_status": ["!=", "Cancelled"],
        }
        if exclude_name:
            filters["name"] = ["!=", exclude_name]
        if exclude_class:
            filters["class_id"] = ["!=", exclude_class]
        rows = frappe.get_all(
            "Class Session",
            filters=filters,
            fields=["name", "start_time", "end_time", "class_id"],
        )
        for r in rows:
            r_start, r_end = _seconds(r.start_time), _seconds(r.end_time)
            if r_start is None or r_end is None:
                continue
            if _overlaps(s_start, s_end, r_start, r_end):
                conflicts.append({"session": r.name, "class_id": r.class_id, "type": label})
    return conflicts


class ClassSession(Document):
    def validate(self):
        if not self.session_status:
            self.session_status = "Scheduled"
        if not self.session_type:
            self.session_type = "Regular"
        self._guard_duplicate()
        self._check_conflicts()

    def _guard_duplicate(self):
        # Bất biến §8.1: unique (class_id, session_date, start_time)
        if not (self.class_id and self.session_date and self.start_time):
            return
        dup = frappe.db.exists(
            "Class Session",
            {
                "class_id": self.class_id,
                "session_date": self.session_date,
                "start_time": self.start_time,
                "name": ["!=", self.name or ""],
            },
        )
        if dup:
            frappe.throw(
                f"Lớp {self.class_id} đã có buổi học ({dup}) cùng ngày và giờ bắt đầu.",
                title="Trùng buổi học",
            )

    def _check_conflicts(self):
        if self.session_status == "Cancelled":
            return
        conflicts = find_session_conflicts(
            self.session_date,
            self.start_time,
            self.end_time,
            teacher=self.teacher,
            classroom=self.classroom,
            exclude_name=self.name,
        )
        if conflicts:
            c = conflicts[0]
            frappe.throw(
                f"Trùng lịch {c['type']}: buổi {c['session']} (lớp {c['class_id']}) cùng ngày bị giao thời gian.",
                title="Xung đột lịch",
            )
