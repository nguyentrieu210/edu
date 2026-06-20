// Toast store dùng chung (Sakura). Gọi: toast.success('...'), toast.error('...').
import { reactive } from 'vue'

let _id = 0
export const toasts = reactive([])

function push(type, title, detail = '', timeout = 3200) {
  const id = ++_id
  toasts.push({ id, type, title, detail })
  if (timeout) setTimeout(() => dismiss(id), timeout)
  return id
}

export function dismiss(id) {
  const i = toasts.findIndex((t) => t.id === id)
  if (i !== -1) toasts.splice(i, 1)
}

export const toast = {
  success: (title, detail) => push('success', title, detail),
  error: (title, detail) => push('error', title, detail, 5000),
  info: (title, detail) => push('info', title, detail),
}
