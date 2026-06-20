// Cấu hình pipeline tuyển sinh dùng chung cho Kanban, List và ngăn chi tiết.
import { statusMeta } from '../../utils/labels'

// 5 cột pipeline chính (Lost xử lý riêng — xem Admissions.vue).
export const STAGES = [
  { status: 'New', dot: '#9b6fc4' },
  { status: 'Consulting', dot: '#4a6fb5' },
  { status: 'Testing', dot: '#c98a2e' },
  { status: 'Trial', dot: '#e07a8f' },
  { status: 'Enrolled', dot: '#3f9b6e' },
]

export const STAGE_ORDER = STAGES.map((s) => s.status)

export function stageMeta(status) {
  return statusMeta('Student Lead', 'status', status)
}

export function stageLabel(status) {
  return stageMeta(status).label
}

// Trạng thái kế tiếp trong pipeline (null nếu đã ở cuối hoặc đã Enrolled/Lost).
export function nextStage(status) {
  const i = STAGE_ORDER.indexOf(status)
  if (i === -1 || i >= STAGE_ORDER.length - 1) return null
  return STAGE_ORDER[i + 1]
}

export function todayStr() {
  return new Date().toISOString().slice(0, 10)
}
