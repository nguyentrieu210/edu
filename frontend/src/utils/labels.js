// Ánh xạ enum trạng thái (DB) → { nhãn tiếng Việt, variant badge } — spec §23–24.
// DB lẫn lộn EN/VN; UI luôn hiển thị nhãn VN. variant ∈ success|info|warning|danger|neutral.

const S = (label, variant) => ({ label, variant })

export const STATUS_MAP = {
  // Student.student_status (DB tiếng Việt)
  'Student.student_status': {
    'Mới nhập học': S('Mới nhập học', 'info'),
    'Đang học': S('Đang học', 'success'),
    'Bảo lưu': S('Bảo lưu', 'warning'),
    'Đã tốt nghiệp': S('Đã tốt nghiệp', 'neutral'),
    'Nghỉ học': S('Nghỉ học', 'danger'),
  },
  // Student.health_status (tình trạng học tập)
  'Student.health_status': {
    'Đang học đều': S('Đang học đều', 'success'),
    'Cần theo dõi': S('Cần theo dõi', 'info'),
    'Cảnh báo': S('Cảnh báo', 'warning'),
    'Khẩn cấp': S('Khẩn cấp', 'danger'),
    'Ngừng học': S('Ngừng học', 'neutral'),
  },
  // Student Lead.status (DB tiếng Anh)
  'Student Lead.status': {
    New: S('Mới', 'neutral'),
    Consulting: S('Tư vấn', 'info'),
    Testing: S('Đang test đầu vào', 'info'),
    Trial: S('Học thử', 'warning'),
    Enrolled: S('Đã nhập học', 'success'),
    Lost: S('Thất bại', 'danger'),
  },
  // Student Appointment.status
  'Student Appointment.status': {
    Scheduled: S('Đã lên lịch', 'info'),
    Completed: S('Hoàn thành', 'success'),
    Cancelled: S('Đã hủy', 'danger'),
    Rescheduled: S('Dời lịch', 'warning'),
  },
  // Class.status
  'Class.status': {
    Upcoming: S('Sắp khai giảng', 'info'),
    Ongoing: S('Đang học', 'success'),
    Completed: S('Đã hoàn thành', 'neutral'),
    Closed: S('Đã đóng', 'neutral'),
  },
  // Class Session.session_status
  'Class Session.session_status': {
    Scheduled: S('Đã lên lịch', 'info'),
    'In Progress': S('Đang diễn ra', 'success'),
    Completed: S('Đã hoàn thành', 'neutral'),
    Cancelled: S('Đã hủy', 'danger'),
    Locked: S('Đã khóa', 'neutral'),
  },
  // Fee Invoice.status
  'Fee Invoice.status': {
    Unpaid: S('Chưa thu', 'warning'),
    'Partially Paid': S('Thu một phần', 'info'),
    Paid: S('Đã thu', 'success'),
    Overdue: S('Quá hạn', 'danger'),
    Cancelled: S('Đã hủy', 'neutral'),
  },
  // Student Attendance.status
  'Student Attendance.status': {
    Present: S('Có mặt', 'success'),
    'Absent with Permission': S('Vắng có phép', 'info'),
    'Absent without Permission': S('Vắng không phép', 'danger'),
    Late: S('Đi muộn', 'warning'),
  },
}

// statusMeta('Student', 'student_status', 'Đang học') → { label, variant }
export function statusMeta(doctype, field, value) {
  const table = STATUS_MAP[`${doctype}.${field}`]
  return (table && table[value]) || { label: value || '—', variant: 'neutral' }
}

// docstatus chứng từ submittable (§23.2)
export function docstatusMeta(docstatus) {
  if (Number(docstatus) === 1) return S('Đã chốt', 'success')
  if (Number(docstatus) === 2) return S('Đã hủy', 'neutral')
  return S('Nháp', 'warning')
}
