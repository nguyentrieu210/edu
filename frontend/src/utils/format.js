// Định dạng vi-VN tập trung (spec §24). Không format thủ công rải rác trong page.

const vnNumber = new Intl.NumberFormat('vi-VN')

// Chuyển 'YYYY-MM-DD' / 'YYYY-MM-DD HH:mm:ss' / Date → Date (an toàn).
function toDate(value) {
  if (!value) return null
  if (value instanceof Date) return value
  // Frappe trả chuỗi local, dùng dạng có 'T' để parser ổn định.
  const s = String(value).trim().replace(' ', 'T')
  const d = new Date(s)
  return isNaN(d.getTime()) ? null : d
}

function pad(n) {
  return String(n).padStart(2, '0')
}

// 4.500.000 ₫ — không phần thập phân, hậu tố ₫.
export function formatVND(value) {
  const n = Number(value)
  if (value == null || isNaN(n)) return '0 ₫'
  return `${vnNumber.format(Math.round(n))} ₫`
}

// 1.250
export function formatNumber(value) {
  const n = Number(value)
  if (value == null || isNaN(n)) return '0'
  return vnNumber.format(n)
}

// 87% / 92,5%
export function formatPercent(value, digits = 0) {
  const n = Number(value)
  if (value == null || isNaN(n)) return '0%'
  return `${n.toLocaleString('vi-VN', { maximumFractionDigits: digits })}%`
}

// 20/06/2026
export function formatDate(value) {
  const d = toDate(value)
  if (!d) return '—'
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`
}

// 18:30
export function formatTime(value) {
  if (!value) return '—'
  // Chấp nhận 'HH:mm:ss' thuần.
  if (typeof value === 'string' && /^\d{1,2}:\d{2}/.test(value)) {
    const [h, m] = value.split(':')
    return `${pad(h)}:${pad(m)}`
  }
  const d = toDate(value)
  if (!d) return '—'
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// 20/06/2026 18:30
export function formatDateTime(value) {
  const d = toDate(value)
  if (!d) return '—'
  return `${formatDate(d)} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// "2 phút trước", "Hôm qua", hoặc ngày tuyệt đối nếu > 7 ngày.
export function formatRelative(value, now = new Date()) {
  const d = toDate(value)
  if (!d) return '—'
  const diffMs = now.getTime() - d.getTime()
  const sec = Math.round(diffMs / 1000)
  const min = Math.round(sec / 60)
  const hour = Math.round(min / 60)
  const day = Math.round(hour / 24)
  if (sec < 60) return 'Vừa xong'
  if (min < 60) return `${min} phút trước`
  if (hour < 24) return `${hour} giờ trước`
  if (day === 1) return 'Hôm qua'
  if (day < 7) return `${day} ngày trước`
  return formatDate(d)
}

// Quá hạn = due_date < hôm nay và còn nợ (§24.1).
export function isOverdue(dueDate, outstanding = 1, now = new Date()) {
  const d = toDate(dueDate)
  if (!d) return false
  return Number(outstanding) > 0 && d.getTime() < now.setHours(0, 0, 0, 0)
}
