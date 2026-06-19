<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Quản lý Hóa Đơn</h3>
        <p class="text-xs text-muted mt-1">Theo dõi các khoản thu học phí, hóa đơn học viên và trạng thái thanh toán.</p>
      </div>
      <button @click="showCreateModal = true" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo Hóa Đơn
      </button>
    </div>

    <!-- Stats Card Grid -->
    <div v-if="!invoices.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-4 animate-fade-in">
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng hóa đơn</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.total }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-brand-tint text-brand rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đã thu</p>
          <h4 class="text-lg font-bold text-brand">{{ formatCurrency(stats.paidAmount) }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-amber-50 text-amber-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Còn nợ (Chưa thu)</p>
          <h4 class="text-lg font-bold text-amber-600">{{ formatCurrency(stats.outstandingAmount) }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-thaco-red-soft text-thaco-red rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Số hóa đơn nợ</p>
          <h4 class="text-lg font-bold text-thaco-red">{{ stats.unpaidCount }}</h4>
        </div>
      </div>
    </div>

    <!-- Toolbar: Search & Filter -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-white p-4 rounded-xl border border-border shadow-sm flex-wrap">
      <div class="relative flex-1">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-faint">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input v-model="searchQuery" placeholder="Tìm kiếm theo mã hóa đơn, học viên..."
          class="w-full pl-10 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="statusFilter"
          class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
          <option value="">Tất cả trạng thái</option>
          <option value="Paid">Đã đóng (Paid)</option>
          <option value="Unpaid">Chưa đóng (Unpaid)</option>
          <option value="Partially Paid">Đóng một phần</option>
          <option value="Overdue">Quá hạn (Overdue)</option>
        </select>
      </div>
      <!-- Period Filter -->
      <div class="flex items-center gap-1 bg-hover/40 border border-border rounded-lg p-1">
        <button v-for="p in periods" :key="p.value" @click="periodFilter = p.value"
          class="px-3 py-1 text-xs font-medium rounded-md transition-all"
          :class="periodFilter === p.value ? 'bg-brand text-white shadow-sm' : 'text-muted hover:bg-white'">
          {{ p.label }}
        </button>
      </div>
      <!-- Bulk delete bar -->
      <transition name="fade">
        <div v-if="selected.length > 0" class="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
          <span class="text-xs text-red-700 font-medium">Đã chọn {{ selected.length }}</span>
          <button @click="showDeleteConfirm = true" class="flex items-center gap-1 px-2.5 py-1 bg-red-600 text-white text-xs font-medium rounded-md hover:bg-red-700">
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            Xóa
          </button>
          <button @click="selected = []" class="text-xs text-red-500 hover:text-red-700">Bỏ chọn</button>
        </div>
      </transition>
    </div>

    <div v-if="invoices.loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="filteredInvoices.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không tìm thấy hóa đơn nào</h3>
      <p class="mt-1 text-sm text-muted">Thử thay đổi bộ lọc hoặc tạo một hóa đơn mới.</p>
      <div class="mt-6">
        <button @click="showCreateModal = true" class="flex items-center gap-2 mx-auto px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">Tạo Hóa Đơn</button>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-border">
          <thead class="bg-hover/40">
            <tr>
              <th class="px-4 py-3 w-10">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-12">STT</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Hóa Đơn</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Học Viên</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Tổng Tiền</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Còn Nợ</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Hạn Nộp</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng Thái</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="(inv, idx) in filteredInvoices" :key="inv.name"
              class="hover:bg-hover/40 transition-colors"
              :class="selected.includes(inv.name) ? 'bg-brand-tint/30' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="inv.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-brand">
                <a :href="`/app/fee-invoice/${inv.name}`" target="_blank" class="hover:underline">{{ inv.name }}</a>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-ink">{{ inv.student }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ formatCurrency(inv.total_amount) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-thaco-red font-semibold">{{ formatCurrency(inv.outstanding_amount) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ inv.due_date || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="inv.status === 'Paid' ? 'bg-brand-soft text-brand' : inv.status === 'Unpaid' ? 'bg-thaco-red-soft text-thaco-red' : inv.status === 'Partially Paid' ? 'bg-amber-100 text-amber-700' : 'bg-hover text-muted'">
                  {{ translateStatus(inv.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bulk Delete Confirm Modal -->
    <div v-if="showDeleteConfirm" @click.self="showDeleteConfirm = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6 cursor-default">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
            <svg class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-ink-2">Xác nhận xóa</h3>
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> hóa đơn. Hành động này không thể hoàn tác.</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>

    <!-- Custom Modal -->
    <div v-if="showCreateModal" @click.self="showCreateModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 my-8 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Tạo Hóa Đơn Học Phí</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Học viên *" v-model="newInvoice.student" :required="true" placeholder="VD: STU-..." />
            <FormControl label="Lịch đăng ký (Tùy chọn)" v-model="newInvoice.program_enrollment" placeholder="VD: ENR-..." />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Ngày lập" type="date" v-model="newInvoice.posting_date" />
            <FormControl label="Hạn nộp" type="date" v-model="newInvoice.due_date" />
          </div>

          <div class="border-t border-border pt-4">
            <div class="flex justify-between items-center mb-3">
              <label class="block text-sm font-semibold text-ink-2">Chi tiết khoản thu</label>
              <button @click="addItem" class="text-xs px-2.5 py-1 text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Thêm dòng</button>
            </div>
            
            <div class="space-y-2">
              <div v-for="(item, index) in newInvoice.items" :key="index" class="flex space-x-2 items-center">
                <div class="flex-1">
                  <FormControl placeholder="Tên khoản thu (Học phí, Sách...)" v-model="item.item_name" />
                </div>
                <div class="w-48">
                  <FormControl type="number" placeholder="Số tiền" v-model="item.amount" />
                </div>
                <button @click="removeItem(index)" class="p-2 text-faint hover:text-thaco-red hover:bg-thaco-red-soft rounded-lg transition-colors" title="Xóa">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="border-t border-border pt-4 grid grid-cols-2 gap-4">
            <FormControl label="Thuế VAT (VND)" type="number" v-model="newInvoice.tax_amount" />
            <div class="space-y-2">
              <FormControl label="Giảm giá (VND)" type="number" v-model="newInvoice.discount_amount" />
              <FormControl label="Lý do giảm giá" v-model="newInvoice.discount_reason" />
            </div>
          </div>
          
          <div class="bg-hover/40 p-4 rounded-lg flex justify-between items-center border border-border">
            <span class="font-medium text-ink-2">Tổng Tiền Thanh Toán:</span>
            <span class="text-xl font-bold text-brand">{{ formatCurrency(computedTotal) }}</span>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2.5 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveInvoice" :disabled="saving" class="flex-1 py-2.5 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Tạo & Lưu Nháp' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { listResource, db } from '../api'

const showCreateModal = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const periodFilter = ref('')
const selected = ref([])
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const periods = [
  { label: 'Tất cả', value: '' },
  { label: 'Tuần', value: 'week' },
  { label: 'Tháng', value: 'month' },
  { label: 'Quý', value: 'quarter' },
  { label: 'Năm', value: 'year' },
]

function getDateRange(period) {
  const now = new Date()
  if (period === 'week') { const d = new Date(now); d.setDate(now.getDate() - 7); return d }
  if (period === 'month') return new Date(now.getFullYear(), now.getMonth(), 1)
  if (period === 'quarter') return new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1)
  if (period === 'year') return new Date(now.getFullYear(), 0, 1)
  return null
}

const getTodayDate = () => new Date().toISOString().split('T')[0]

const defaultInvoice = {
  student: '',
  program_enrollment: '',
  posting_date: getTodayDate(),
  due_date: getTodayDate(),
  tax_amount: 0,
  discount_amount: 0,
  discount_reason: '',
  items: [
    { item_name: 'Học phí', amount: 0 }
  ]
}

const newInvoice = ref(JSON.parse(JSON.stringify(defaultInvoice)))

const computedTotal = computed(() => {
  const itemTotal = newInvoice.value.items.reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0)
  const tax = Number(newInvoice.value.tax_amount) || 0
  const discount = Number(newInvoice.value.discount_amount) || 0
  return Math.max(0, itemTotal + tax - discount)
})

const invoices = listResource('Fee Invoice', {
  fields: ['name', 'student', 'total_amount', 'outstanding_amount', 'due_date', 'status'],
  order_by: 'creation desc',
  limit_page_length: 50,
  auto: true
})

// Search & filter logic
const filteredInvoices = computed(() => {
  if (!invoices.data) return []
  const start = getDateRange(periodFilter.value)
  return invoices.data.filter(inv => {
    const nameMatch = !searchQuery.value || 
      inv.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      inv.student.toLowerCase().includes(searchQuery.value.toLowerCase())
    const statusMatch = !statusFilter.value || inv.status === statusFilter.value
    const periodMatch = !start || !inv.due_date || new Date(inv.due_date) >= start
    return nameMatch && statusMatch && periodMatch
  })
})

const allSelected = computed(() =>
  filteredInvoices.value.length > 0 && filteredInvoices.value.every(i => selected.value.includes(i.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredInvoices.value.map(i => i.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Fee Invoice', name)
    }
    selected.value = []; showDeleteConfirm.value = false; invoices.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

// Stats calculations
const stats = computed(() => {
  const data = invoices.data || []
  const unpaid = data.filter(i => i.status === 'Unpaid' || i.status === 'Partially Paid' || i.status === 'Overdue')
  const totalOutstanding = unpaid.reduce((sum, curr) => sum + (Number(curr.outstanding_amount) || 0), 0)
  const total = data.reduce((sum, curr) => sum + (Number(curr.total_amount) || 0), 0)
  
  return {
    total: data.length,
    paidAmount: Math.max(0, total - totalOutstanding),
    outstandingAmount: totalOutstanding,
    unpaidCount: unpaid.length
  }
})

const addItem = () => {
  newInvoice.value.items.push({ item_name: '', amount: 0 })
}

const removeItem = (idx) => {
  newInvoice.value.items.splice(idx, 1)
}

const saveInvoice = async () => {
  if (!newInvoice.value.student) {
    alert('Vui lòng nhập mã Học viên.')
    return
  }
  
  saving.value = true
  try {
    const docData = {
      doctype: 'Fee Invoice',
      student: newInvoice.value.student,
      program_enrollment: newInvoice.value.program_enrollment,
      posting_date: newInvoice.value.posting_date,
      due_date: newInvoice.value.due_date,
      tax_amount: newInvoice.value.tax_amount,
      discount_amount: newInvoice.value.discount_amount,
      discount_reason: newInvoice.value.discount_reason,
      total_amount: computedTotal.value,
      items: newInvoice.value.items.map(i => ({
        item_name: i.item_name,
        amount: Number(i.amount)
      }))
    }

    await db.insert(docData)
    
    showCreateModal.value = false
    invoices.fetch()
    newInvoice.value = JSON.parse(JSON.stringify(defaultInvoice))
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra: ' + (err.messages ? err.messages[0] : 'Vui lòng kiểm tra lại thông tin.'))
  } finally {
    saving.value = false
  }
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
}

const translateStatus = (status) => {
  if (status === 'Paid') return 'Đã thanh toán'
  if (status === 'Unpaid') return 'Chưa thanh toán'
  if (status === 'Partially Paid') return 'Thanh toán một phần'
  if (status === 'Overdue') return 'Quá hạn'
  return status
}
</script>
