<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Phiếu Thu Học Phí</h3>
        <p class="text-xs text-muted mt-1">Lập và quản lý phiếu thu học phí, theo dõi doanh thu thực tế.</p>
      </div>
      <button @click="openCreateModal" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Lập Phiếu Thu
      </button>
    </div>

    <!-- Stats Card Grid -->
    <div v-if="!payments.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-4 animate-fade-in">
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng số phiếu thu</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.totalCount }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-brand-tint text-brand rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Doanh thu (Đã thu)</p>
          <h4 class="text-lg font-bold text-brand">{{ formatCurrency(stats.totalAmount) }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Kênh phổ biến</p>
          <h4 class="text-lg font-bold text-blue-600">{{ translatePaymentMethod(stats.topMethod) }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-amber-50 text-amber-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Giao dịch hôm nay</p>
          <h4 class="text-lg font-bold text-amber-600">{{ stats.todayCount }}</h4>
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
        <input v-model="searchQuery" placeholder="Tìm kiếm theo mã phiếu thu, học viên..."
          class="w-full pl-10 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="methodFilter"
          class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
          <option value="">Tất cả phương thức</option>
          <option value="Cash">Tiền mặt</option>
          <option value="Bank Transfer">Chuyển khoản</option>
          <option value="Card">Thẻ ngân hàng</option>
          <option value="Other">Khác</option>
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

    <!-- Loading State -->
    <div v-if="payments.loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredPayments.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không tìm thấy phiếu thu nào</h3>
      <p class="mt-1 text-sm text-muted">Hãy lập phiếu thu mới để bắt đầu thu học phí.</p>
      <div class="mt-6">
        <button @click="openCreateModal" class="flex items-center gap-2 mx-auto px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">Lập Phiếu Thu Mới</button>
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
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Phiếu Thu</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Học Viên</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Ngày Đóng</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Phương Thức</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Số Tiền Đóng</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Giao Dịch</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="(payment, idx) in filteredPayments" :key="payment.name"
              class="hover:bg-hover/40 transition-colors"
              :class="selected.includes(payment.name) ? 'bg-brand-tint/30' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="payment.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-brand">
                <a :href="`/app/fee-payment/${payment.name}`" target="_blank" class="hover:underline">{{ payment.name }}</a>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-ink">{{ payment.student }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ payment.payment_date || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ translatePaymentMethod(payment.payment_method) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-sm font-bold text-brand">{{ formatCurrency(payment.amount) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ payment.reference_no || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Custom Modal -->
    <div v-if="showCreateModal" @click.self="showCreateModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Lập Phiếu Thu Học Phí</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- Select Student -->
          <FormControl 
            type="select" 
            label="Học viên *" 
            v-model="newPayment.student" 
            :options="studentOptions"
            @change="onStudentChange"
            :required="true"
          />

          <!-- Select Invoice -->
          <FormControl 
            type="select" 
            label="Hóa đơn học phí *" 
            v-model="newPayment.invoice" 
            :options="invoiceOptions"
            @change="onInvoiceChange"
            :disabled="!newPayment.student || loadingInvoices"
            :required="true"
            placeholder="Chọn hóa đơn cần thu"
          />
          <p v-if="loadingInvoices" class="text-xs text-faint">Đang tải hóa đơn chưa đóng...</p>
          <p v-else-if="newPayment.student && invoiceOptions.length === 0" class="text-xs text-amber-600">Học viên này không có hóa đơn nào chưa đóng.</p>

          <!-- Display Outstanding -->
          <div v-if="selectedInvoice" class="rounded-lg bg-hover p-3 text-sm flex justify-between border border-border">
            <span class="text-muted">Số tiền nợ còn lại:</span>
            <span class="font-bold text-ink-2">{{ formatCurrency(selectedInvoice.outstanding_amount) }}</span>
          </div>

          <!-- Date -->
          <FormControl 
            type="date" 
            label="Ngày đóng học phí *" 
            v-model="newPayment.payment_date" 
            :required="true"
          />

          <!-- Method -->
          <FormControl 
            type="select" 
            label="Phương thức đóng *" 
            v-model="newPayment.payment_method" 
            :options="[
              { label: 'Tiền mặt', value: 'Cash' },
              { label: 'Chuyển khoản', value: 'Bank Transfer' },
              { label: 'Thẻ ngân hàng', value: 'Card' },
              { label: 'Khác', value: 'Other' }
            ]" 
            :required="true"
          />

          <!-- Amount -->
          <FormControl 
            type="text" 
            label="Số tiền đóng *" 
            v-model="newPayment.amount" 
            placeholder="0"
            :required="true"
          />

          <!-- Reference -->
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Mã giao dịch / Số tham chiếu" v-model="newPayment.reference_no" placeholder="TXN123456" />
            <FormControl type="date" label="Ngày giao dịch" v-model="newPayment.reference_date" />
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="savePayment" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu & Ghi Sổ' }}</button>
        </div>
      </div>
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
          <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> phiếu thu. Hành động này không thể hoàn tác.</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
        <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl } from 'frappe-ui'
import { apiResource, db, call } from '../api'

const showCreateModal = ref(false)
const saving = ref(false)
const loadingInvoices = ref(false)
const studentsList = ref([])
const unpaidInvoices = ref([])
const searchQuery = ref('')
const methodFilter = ref('')
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

const newPayment = ref({
  student: '',
  invoice: '',
  payment_date: new Date().toISOString().substring(0, 10),
  payment_method: 'Cash',
  amount: '',
  reference_no: '',
  reference_date: ''
})

// Load payments
const payments = apiResource('get_payments', { auto: true })

// Search & filter logic
const filteredPayments = computed(() => {
  if (!payments.data) return []
  const start = getDateRange(periodFilter.value)
  return payments.data.filter(p => {
    const searchMatch = !searchQuery.value || 
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.student.toLowerCase().includes(searchQuery.value.toLowerCase())
    const methodMatch = !methodFilter.value || p.payment_method === methodFilter.value
    const dateField = p.payment_date || p.creation
    const periodMatch = !start || !dateField || new Date(dateField) >= start
    return searchMatch && methodMatch && periodMatch
  })
})

const allSelected = computed(() =>
  filteredPayments.value.length > 0 && filteredPayments.value.every(p => selected.value.includes(p.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredPayments.value.map(p => p.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Fee Payment', name)
    }
    selected.value = []; showDeleteConfirm.value = false; payments.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

// Stats calculations
const stats = computed(() => {
  const data = payments.data || []
  const totalAmount = data.reduce((sum, curr) => sum + (Number(curr.amount) || 0), 0)
  
  // Count payment methods
  const methods = data.map(p => p.payment_method)
  const counts = {}
  methods.forEach(m => { counts[m] = (counts[m] || 0) + 1 })
  let topMethod = 'N/A'
  let maxCount = 0
  for (const [m, count] of Object.entries(counts)) {
    if (count > maxCount) {
      maxCount = count
      topMethod = m
    }
  }

  // Payments today
  const todayStr = new Date().toISOString().split('T')[0]
  const todayCount = data.filter(p => p.payment_date === todayStr).length

  return {
    totalCount: data.length,
    totalAmount,
    topMethod,
    todayCount
  }
})

// Load students list for options
const loadStudents = async () => {
  try {
    const res = await call('get_students')
    studentsList.value = res || []
  } catch (err) {
    console.error('Error loading students:', err)
  }
}

const studentOptions = computed(() => {
  return [
    { label: 'Chọn học viên...', value: '' },
    ...studentsList.value.map(s => ({
      label: `${s.name} - ${s.full_name}`,
      value: s.name
    }))
  ]
})

const invoiceOptions = computed(() => {
  if (unpaidInvoices.value.length === 0) return []
  return [
    { label: 'Chọn hóa đơn...', value: '' },
    ...unpaidInvoices.value.map(inv => ({
      label: `${inv.name} (Hạn: ${inv.due_date} - Nợ: ${formatCurrency(inv.outstanding_amount)})`,
      value: inv.name
    }))
  ]
})

const selectedInvoice = computed(() => {
  return unpaidInvoices.value.find(inv => inv.name === newPayment.value.invoice)
})

const openCreateModal = async () => {
  showCreateModal.value = true
  await loadStudents()
}

const onStudentChange = async () => {
  newPayment.value.invoice = ''
  unpaidInvoices.value = []
  if (!newPayment.value.student) return

  loadingInvoices.value = true
  try {
    const res = await call('get_unpaid_invoices', { student: newPayment.value.student })
    unpaidInvoices.value = res || []
  } catch (err) {
    console.error('Error loading unpaid invoices:', err)
  } finally {
    loadingInvoices.value = false
  }
}

const onInvoiceChange = () => {
  if (selectedInvoice.value) {
    newPayment.value.amount = String(selectedInvoice.value.outstanding_amount)
  } else {
    newPayment.value.amount = ''
  }
}

const savePayment = async () => {
  if (!newPayment.value.student) {
    alert('Vui lòng chọn học viên.')
    return
  }
  if (!newPayment.value.invoice) {
    alert('Vui lòng chọn hóa đơn để thanh toán.')
    return
  }
  const amt = parseFloat(newPayment.value.amount)
  if (isNaN(amt) || amt <= 0) {
    alert('Số tiền đóng phải lớn hơn 0.')
    return
  }
  if (selectedInvoice.value && amt > selectedInvoice.value.outstanding_amount + 0.01) {
    alert(`Số tiền đóng (${formatCurrency(amt)}) không được vượt quá số tiền nợ (${formatCurrency(selectedInvoice.value.outstanding_amount)}).`)
    return
  }

  saving.value = true
  try {
    await call('create_payment', {
      student: newPayment.value.student,
      payment_date: newPayment.value.payment_date,
      payment_method: newPayment.value.payment_method,
      amount: amt,
      invoice: newPayment.value.invoice,
      reference_no: newPayment.value.reference_no || undefined,
      reference_date: newPayment.value.reference_date || undefined
    })
    
    showCreateModal.value = false
    payments.fetch() // Refresh list
    
    // Reset form
    newPayment.value = {
      student: '',
      invoice: '',
      payment_date: new Date().toISOString().substring(0, 10),
      payment_method: 'Cash',
      amount: '',
      reference_no: '',
      reference_date: ''
    }
    unpaidInvoices.value = []
    
    alert('Phiếu thu đã được lập và ghi sổ thành công.')
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra khi tạo phiếu thu.')
  } finally {
    saving.value = false
  }
}

const translatePaymentMethod = (method) => {
  if (method === 'Cash') return 'Tiền mặt'
  if (method === 'Bank Transfer') return 'Chuyển khoản'
  if (method === 'Card') return 'Thẻ ngân hàng'
  if (method === 'Other') return 'Khác'
  return method
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
}
</script>
