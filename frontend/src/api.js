// Tầng gọi API dùng chung cho toàn bộ SPA Education ERP.
// Mục tiêu: gom mọi lời gọi backend về một chỗ — tên phương thức whitelisted,
// thao tác frappe.client (get_list / insert / set_value / delete) và proxy AI.
// CSRF do frappe-ui (frappeRequest) tự xử lý qua window.csrf_token.
import { frappeRequest, createResource } from 'frappe-ui'

// Mọi phương thức whitelisted của app nằm dưới namespace này.
const API_NS = 'edu.education_erp.api'

// Cho phép truyền tên ngắn ('get_students') hoặc full path ('frappe.client.x').
function resolve(method) {
  return method.includes('.') ? method : `${API_NS}.${method}`
}

// Gọi một phương thức API của education_erp (POST). Trả về `message` của response.
export function call(method, params = {}) {
  return frappeRequest({ url: resolve(method), method: 'POST', params })
}

// Tạo một reactive resource (frappe-ui) gắn với phương thức API của education_erp.
// Giữ nguyên các option của createResource (auto, params, transform, onSuccess...).
export function apiResource(method, options = {}) {
  return createResource({ url: resolve(method), ...options })
}

// Tạo reactive resource liệt kê một DocType qua frappe.client.get_list.
// `filters` có thể là object tĩnh hoặc một hàm trả về object (để phản ứng theo state).
// Các option còn lại (auto, transform, onSuccess...) được truyền thẳng cho createResource.
export function listResource(doctype, { fields, filters, order_by, limit_page_length, ...rest } = {}) {
  return createResource({
    url: 'frappe.client.get_list',
    makeParams() {
      const p = { doctype }
      if (fields) p.fields = JSON.stringify(fields)
      if (filters) p.filters = JSON.stringify(typeof filters === 'function' ? filters() : filters)
      if (order_by) p.order_by = order_by
      if (limit_page_length != null) p.limit_page_length = limit_page_length
      return p
    },
    ...rest,
  })
}

// Các key cần serialize sang JSON khi gọi frappe.client.get_list.
const JSON_KEYS = ['fields', 'filters', 'or_filters']

// Helper thao tác Document chung qua frappe.client. Tôn trọng phân quyền của
// user đang đăng nhập (KHÔNG bỏ qua permission).
export const db = {
  // getList('Student', { fields: [...], filters: {...}, order_by, limit_page_length, parent })
  getList(doctype, opts = {}) {
    const params = { doctype }
    for (const [k, v] of Object.entries(opts)) {
      params[k] = JSON_KEYS.includes(k) && typeof v !== 'string' ? JSON.stringify(v) : v
    }
    return frappeRequest({ url: 'frappe.client.get_list', method: 'GET', params })
  },

  // insert({ doctype: 'Teacher', ... })
  insert(doc) {
    return call('create_document', { doc })
  },

  // setValue('Doctype', name, 'field', value)  hoặc  setValue('Doctype', name, { f1, f2 })
  setValue(doctype, name, fieldname, value) {
    const values = fieldname && typeof fieldname === 'object' ? fieldname : { [fieldname]: value }
    return call('update_document', { doctype, name, values })
  },

  // delete('Doctype', name)
  delete(doctype, name) {
    return call('delete_document', { doctype, name })
  },
}

// Tải file lên qua endpoint chuẩn của Frappe (/api/method/upload_file).
// Dùng fetch + FormData: PHẢI tự set CSRF header và KHÔNG set Content-Type
// (trình duyệt tự thêm boundary multipart). Trả về File doc { name, file_url, ... }.
export async function uploadFile(file, { isPrivate = false, folder = 'Home', doctype, docname, fieldname } = {}) {
  const form = new FormData()
  form.append('file', file, file.name)
  form.append('is_private', isPrivate ? '1' : '0')
  form.append('folder', folder)
  if (doctype) form.append('doctype', doctype)
  if (docname) form.append('docname', docname)
  if (fieldname) form.append('fieldname', fieldname)

  const res = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
    body: form,
    credentials: 'include',
  })
  let json = {}
  try {
    json = await res.json()
  } catch {
    json = {}
  }
  if (!res.ok) {
    let msg = json?.exception || `Tải lên thất bại (${res.status})`
    try {
      const sm = json?._server_messages && JSON.parse(json._server_messages)
      if (sm?.length) msg = JSON.parse(sm[0]).message || msg
    } catch { /* giữ msg mặc định */ }
    throw new Error(msg)
  }
  return json.message
}

// Các tác vụ CRM tuyển sinh — gom về một chỗ cho gọn component.
export const crm = {
  advanceStage(leadId, toStatus, payload = {}) {
    return call('advance_lead_stage', { lead_id: leadId, to_status: toStatus, payload })
  },
  timeline(leadId) {
    return call('get_lead_timeline', { lead_id: leadId })
  },
  appointments(leadId) {
    return call('get_appointments', { lead_id: leadId })
  },
  parseDocument(fileUrl) {
    return call('ai_parse_lead_document', { file_url: fileUrl })
  },
  attachFile(fileUrl, leadId) {
    return call('attach_file_to_lead', { file_url: fileUrl, lead_id: leadId })
  },
}
