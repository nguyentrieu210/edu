// Tầng gọi API dùng chung cho toàn bộ SPA Education ERP.
// Mục tiêu: gom mọi lời gọi backend về một chỗ — tên phương thức whitelisted,
// thao tác frappe.client (get_list / insert / set_value / delete) và proxy AI.
// CSRF do frappe-ui (frappeRequest) tự xử lý qua window.csrf_token.
import { frappeRequest, createResource } from 'frappe-ui'

// Mọi phương thức whitelisted của app nằm dưới namespace này.
const API_NS = 'education_erp.education_erp.api'

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
    return frappeRequest({ url: 'frappe.client.insert', method: 'POST', params: { doc } })
  },

  // setValue('Doctype', name, 'field', value)  hoặc  setValue('Doctype', name, { f1, f2 })
  setValue(doctype, name, fieldname, value) {
    const params = { doctype, name, fieldname }
    if (value !== undefined) params.value = value
    return frappeRequest({ url: 'frappe.client.set_value', method: 'POST', params })
  },

  // delete('Doctype', name)
  delete(doctype, name) {
    return frappeRequest({ url: 'frappe.client.delete', method: 'POST', params: { doctype, name } })
  },
}
