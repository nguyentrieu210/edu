// Lọc theo kỳ thời gian (client-side) dùng chung cho Tuyển sinh / Học viên / Lịch hẹn.
// Mốc: Tất cả · Hôm nay · Tuần này · Tháng này · Quý này · Năm nay.

export const PERIODS = [
  { value: 'all', label: '📅 Toàn thời gian' },
  { value: 'today', label: '📅 Hôm nay' },
  { value: 'week', label: '📅 Tuần này' },
  { value: 'month', label: '📅 Tháng này' },
  { value: 'quarter', label: '📅 Quý này' },
  { value: 'year', label: '📅 Năm nay' },
]

// Trả [start, end) của kỳ tính từ thời điểm now (đầu ngày).
function rangeOf(period, now = new Date()) {
  const start = new Date(now)
  start.setHours(0, 0, 0, 0)
  const end = new Date(start)
  if (period === 'today') {
    end.setDate(end.getDate() + 1)
  } else if (period === 'week') {
    const off = (start.getDay() + 6) % 7 // thứ 2 đầu tuần
    start.setDate(start.getDate() - off)
    end.setTime(start.getTime())
    end.setDate(end.getDate() + 7)
  } else if (period === 'month') {
    start.setDate(1)
    end.setTime(start.getTime())
    end.setMonth(end.getMonth() + 1)
  } else if (period === 'quarter') {
    start.setMonth(Math.floor(start.getMonth() / 3) * 3, 1)
    end.setTime(start.getTime())
    end.setMonth(end.getMonth() + 3)
  } else if (period === 'year') {
    start.setMonth(0, 1)
    end.setTime(start.getTime())
    end.setFullYear(end.getFullYear() + 1)
  } else {
    return null
  }
  return [start, end]
}

// dateStr: 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:mm:ss'.
export function inPeriod(dateStr, period, now = new Date()) {
  if (!period || period === 'all') return true
  if (!dateStr) return false
  const range = rangeOf(period, now)
  if (!range) return true
  const d = new Date(String(dateStr).trim().replace(' ', 'T'))
  if (isNaN(d.getTime())) return false
  return d >= range[0] && d < range[1]
}
