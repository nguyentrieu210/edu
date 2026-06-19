<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Đăng Ký Lớp Học</h3>
        <p class="text-xs text-muted mt-1">Gán học viên vào lớp, chốt học phí và tự sinh onboarding + lịch thu + hóa đơn.</p>
      </div>
      <button @click="openCreateModal" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Đăng Ký Lớp Mới
      </button>
    </div>

    <!-- Stats -->
    <div v-if="!enrollments.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-3 animate-fade-in">
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng đăng ký</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.total }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-brand-tint text-brand rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đang học (Active)</p>
          <h4 class="text-lg font-bold text-brand">{{ stats.active }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng học phí (net)</p>
          <h4 class="text-lg font-bold text-blue-600">{{ formatCurrency(stats.totalFee) }}</h4>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-white p-4 rounded-xl border border-border shadow-sm flex-wrap">
      <div class="relative flex-1">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-faint">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        </span>
        <input v-model="searchQuery" placeholder="Tìm theo mã đăng ký, học viên, lớp..."
          class="w-full pl-10 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="statusFilter" class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
          <option value="">Tất cả trạng thái</option>
          <option v-for="s in statusValues" :key="s" :value="s">{{ statusLabel(s) }}</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="enrollments.loading" class="flex justify-center py-8"><LoadingIndicator /></div>

    <!-- Empty -->
    <div v-else-if="filteredEnrollments.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Chưa có đăng ký nào</h3>
      <p class="mt-1 text-sm text-muted">Hãy đăng ký học viên vào lớp để bắt đầu.</p>
      <div class="mt-6">
        <button @click="openCreateModal" class="flex items-center gap-2 mx-auto px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">Đăng Ký Lớp Mới</button>
      </div>
    </div>

    <!-- Table -->
    <div v-else class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-border">
          <thead class="bg-hover/40">
            <tr>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-12">STT</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Đăng Ký</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Học Viên</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Lớp</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Loại</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng Thái</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Học Phí (net)</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Ngày ĐK</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Thao Tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="(e, idx) in filteredEnrollments" :key="e.name" class="hover:bg-hover/40 transition-colors">
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-brand">
                <a :href="`/app/program-enrollment/${e.name}`" target="_blank" class="hover:underline">{{ e.name }}</a>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-ink">{{ e.student }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ e.class_id }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ e.enrollment_type === 'Trial' ? 'Học thử' : 'Chính thức' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="statusClass(e.enrollment_status)">
                  {{ statusLabel(e.enrollment_status) }}
                </span>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-sm font-bold text-ink-2 tabular-nums">{{ formatCurrency(e.net_fee) }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ e.enrollment_date || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-right">
                <button v-if="e.docstatus === 1 && ['Active', 'Deferred'].includes(e.enrollment_status)" @click="openAction(e)"
                  class="px-3 py-1.5 text-xs font-medium text-ink-2 border border-border rounded-lg hover:bg-hover/40 transition-colors">
                  Thao tác
                </button>
                <span v-else class="text-xs text-faint">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" @click.self="showCreateModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 my-8 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Đăng Ký Học Viên Vào Lớp</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="space-y-4">
          <FormControl type="select" label="Học viên *" v-model="newEnr.student" :options="studentOptions" :required="true" />

          <FormControl type="select" label="Lớp học *" v-model="newEnr.class_id" :options="classOptions" @change="onClassChange" :required="true" placeholder="Chọn lớp" />
          <p v-if="loadingClassInfo" class="text-xs text-faint">Đang tải thông tin lớp...</p>

          <!-- Class info box -->
          <div v-if="classInfo" class="rounded-lg bg-hover p-3 text-sm border border-border space-y-1.5">
            <div class="flex justify-between"><span class="text-muted">Giá niêm yết:</span><span class="font-semibold text-ink-2 tabular-nums">{{ formatCurrency(classInfo.list_price) }}</span></div>
            <div class="flex justify-between">
              <span class="text-muted">Sĩ số:</span>
              <span class="font-semibold tabular-nums" :class="capacityFull ? 'text-red-600' : 'text-ink-2'">
                {{ classInfo.active_count }}{{ classInfo.max_capacity ? ' / ' + classInfo.max_capacity : '' }}
                <span v-if="capacityFull" class="text-xs">(đã đầy)</span>
              </span>
            </div>
          </div>

          <FormControl type="select" label="Loại đăng ký" v-model="newEnr.enrollment_type"
            :options="[{ label: 'Chính thức', value: 'Official' }, { label: 'Học thử', value: 'Trial' }]" />

          <div class="grid grid-cols-2 gap-4">
            <FormControl type="select" label="Loại ưu đãi" v-model="newEnr.discount_type"
              :options="[{ label: 'Không', value: '' }, { label: 'Phần trăm (%)', value: 'Percent' }, { label: 'Số tiền', value: 'Amount' }]" />
            <FormControl v-if="newEnr.discount_type" type="text" :label="newEnr.discount_type === 'Percent' ? 'Giá trị (%)' : 'Giá trị (₫)'" v-model="newEnr.discount_value" placeholder="0" />
          </div>

          <FormControl v-if="newEnr.discount_type" type="text" label="Lý do / người duyệt ưu đãi" v-model="newEnr.discount_reason" placeholder="VD: Ưu đãi khai giảng - duyệt bởi ..." />

          <!-- Net fee preview -->
          <div class="rounded-lg bg-brand-tint/40 p-3 text-sm flex justify-between border border-brand/20">
            <span class="text-muted font-medium">Học phí cuối (net):</span>
            <span class="font-bold text-brand tabular-nums">{{ formatCurrency(feePreview) }}</span>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveEnrollment" :disabled="saving || capacityFull" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang xử lý...' : 'Đăng Ký & Chốt Học Phí' }}</button>
        </div>
      </div>
    </div>

    <!-- Lifecycle Action Modal -->
    <div v-if="showActionModal" @click.self="showActionModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 my-8 cursor-default">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-lg font-bold text-ink-2">Thao tác đăng ký</h2>
          <button @click="showActionModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <p class="text-xs text-muted mb-4">{{ actionEnr?.name }} · {{ actionEnr?.student }} · lớp {{ actionEnr?.class_id }}</p>

        <div class="space-y-4">
          <FormControl type="select" label="Hành động *" v-model="actionType" :options="actionOptions" @change="onActionTypeChange" />

          <!-- Defer -->
          <template v-if="actionType === 'defer'">
            <div class="grid grid-cols-2 gap-4">
              <FormControl type="date" label="Bảo lưu từ *" v-model="actionForm.leave_from_date" />
              <FormControl type="date" label="Đến ngày *" v-model="actionForm.leave_to_date" />
            </div>
            <FormControl type="textarea" label="Lý do" v-model="actionForm.reason" />
          </template>

          <!-- Transfer -->
          <template v-else-if="actionType === 'transfer'">
            <FormControl type="select" label="Chuyển sang lớp *" v-model="actionForm.to_class" :options="transferClassOptions" />
            <FormControl type="date" label="Ngày chuyển" v-model="actionForm.transfer_date" />
            <FormControl type="textarea" label="Lý do" v-model="actionForm.reason" />
            <p class="text-xs text-amber-600">Lưu ý: đăng ký mới sẽ chốt học phí chuẩn của lớp đích. Chênh lệch/credit do bộ phận tài chính xử lý riêng.</p>
          </template>

          <!-- Drop -->
          <template v-else-if="actionType === 'drop'">
            <FormControl type="textarea" label="Lý do nghỉ học" v-model="actionForm.reason" />
            <label class="flex items-center gap-2 text-sm text-ink-2">
              <input type="checkbox" v-model="actionForm.makeRefund" class="w-4 h-4 rounded border-border text-brand focus:ring-brand" />
              Tạo phiếu hoàn phí (Draft) để tài chính duyệt
            </label>
            <template v-if="actionForm.makeRefund">
              <FormControl type="select" label="Hóa đơn gốc *" v-model="actionForm.refund_invoice" :options="studentInvoiceOptions" />
              <FormControl type="text" label="Số tiền hoàn *" v-model="actionForm.refund_amount" placeholder="0" />
            </template>
          </template>

          <!-- Resume -->
          <p v-else-if="actionType === 'resume'" class="text-sm text-muted">Kích hoạt lại đăng ký này về trạng thái Đang học (Active).</p>
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showActionModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="submitAction" :disabled="actionSaving || !actionType" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ actionSaving ? 'Đang xử lý...' : 'Xác nhận' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, call, db } from '../api'

const showCreateModal = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const studentsList = ref([])
const classesList = ref([])
const classInfo = ref(null)
const loadingClassInfo = ref(false)

const statusValues = ['Pending', 'Active', 'Deferred', 'Transferred', 'Completed', 'Dropped', 'Rejected']

const newEnr = ref({
  student: '',
  class_id: '',
  enrollment_type: 'Official',
  discount_type: '',
  discount_value: '',
  discount_reason: '',
})

const enrollments = apiResource('get_enrollments', { auto: true })

const filteredEnrollments = computed(() => {
  if (!enrollments.data) return []
  const q = searchQuery.value.toLowerCase()
  return enrollments.data.filter((e) => {
    const searchMatch = !q ||
      e.name.toLowerCase().includes(q) ||
      (e.student || '').toLowerCase().includes(q) ||
      (e.class_id || '').toLowerCase().includes(q)
    const statusMatch = !statusFilter.value || e.enrollment_status === statusFilter.value
    return searchMatch && statusMatch
  })
})

const stats = computed(() => {
  const data = enrollments.data || []
  return {
    total: data.length,
    active: data.filter((e) => e.enrollment_status === 'Active').length,
    totalFee: data.reduce((s, e) => s + (Number(e.net_fee) || 0), 0),
  }
})

const studentOptions = computed(() => [
  { label: 'Chọn học viên...', value: '' },
  ...studentsList.value.map((s) => ({ label: `${s.name} - ${s.full_name}`, value: s.name })),
])

const classOptions = computed(() => [
  { label: 'Chọn lớp...', value: '' },
  ...classesList.value.map((c) => ({ label: `${c.name} - ${c.class_name}`, value: c.name })),
])

const capacityFull = computed(() =>
  !!classInfo.value && classInfo.value.max_capacity > 0 && classInfo.value.active_count >= classInfo.value.max_capacity
)

const feePreview = computed(() => {
  const lp = Number(classInfo.value?.list_price || 0)
  const dv = Number(newEnr.value.discount_value || 0)
  if (newEnr.value.discount_type === 'Percent') return Math.max(0, lp - (lp * dv) / 100)
  if (newEnr.value.discount_type === 'Amount') return Math.max(0, lp - dv)
  return lp
})

const openCreateModal = async () => {
  showCreateModal.value = true
  classInfo.value = null
  newEnr.value = { student: '', class_id: '', enrollment_type: 'Official', discount_type: '', discount_value: '', discount_reason: '' }
  try {
    const [students, classes] = await Promise.all([call('get_students'), call('get_classes')])
    studentsList.value = students || []
    classesList.value = classes || []
  } catch (err) {
    console.error('Error loading options:', err)
  }
}

const onClassChange = async () => {
  classInfo.value = null
  if (!newEnr.value.class_id) return
  loadingClassInfo.value = true
  try {
    classInfo.value = await call('get_class_enrollment_info', { class_id: newEnr.value.class_id })
  } catch (err) {
    console.error('Error loading class info:', err)
  } finally {
    loadingClassInfo.value = false
  }
}

const saveEnrollment = async () => {
  if (!newEnr.value.student) { alert('Vui lòng chọn học viên.'); return }
  if (!newEnr.value.class_id) { alert('Vui lòng chọn lớp học.'); return }
  if (capacityFull.value) { alert('Lớp đã đủ sĩ số.'); return }

  saving.value = true
  try {
    const res = await call('create_enrollment', {
      student: newEnr.value.student,
      class_id: newEnr.value.class_id,
      enrollment_type: newEnr.value.enrollment_type,
      discount_type: newEnr.value.discount_type || undefined,
      discount_value: Number(newEnr.value.discount_value || 0),
      discount_reason: newEnr.value.discount_reason || undefined,
      submit: 1,
    })
    showCreateModal.value = false
    enrollments.fetch()
    alert(`Đã đăng ký ${res.name} — học phí ${formatCurrency(res.net_fee)}. Onboarding, lịch thu và hóa đơn đã được tạo.`)
  } catch (err) {
    console.error(err)
    alert('Lỗi khi đăng ký: ' + (err.messages?.join('\n') || err.message || 'Vui lòng kiểm tra lại.'))
  } finally {
    saving.value = false
  }
}

// --- Lifecycle actions ---
const showActionModal = ref(false)
const actionSaving = ref(false)
const actionEnr = ref(null)
const actionType = ref('')
const studentInvoices = ref([])
const actionForm = ref({})

const actionOptions = computed(() => {
  const base = [{ label: 'Chọn hành động...', value: '' }]
  if (actionEnr.value?.enrollment_status === 'Active') {
    base.push({ label: 'Bảo lưu', value: 'defer' }, { label: 'Chuyển lớp', value: 'transfer' }, { label: 'Nghỉ học', value: 'drop' })
  } else if (actionEnr.value?.enrollment_status === 'Deferred') {
    base.push({ label: 'Tiếp tục học', value: 'resume' }, { label: 'Nghỉ học', value: 'drop' })
  }
  return base
})

const transferClassOptions = computed(() => [
  { label: 'Chọn lớp đích...', value: '' },
  ...classesList.value.filter(c => c.name !== actionEnr.value?.class_id).map(c => ({ label: `${c.name} - ${c.class_name}`, value: c.name })),
])

const studentInvoiceOptions = computed(() => [
  { label: 'Chọn hóa đơn...', value: '' },
  ...studentInvoices.value.map(i => ({ label: `${i.name} (${formatCurrency(i.total_amount)})`, value: i.name })),
])

const openAction = async (e) => {
  actionEnr.value = e
  actionType.value = ''
  actionForm.value = { transfer_date: new Date().toISOString().substring(0, 10), makeRefund: false }
  showActionModal.value = true
  if (!classesList.value.length) {
    try { classesList.value = await call('get_classes') || [] } catch (err) { console.error(err) }
  }
}

const onActionTypeChange = async () => {
  if (actionType.value === 'drop' && actionEnr.value) {
    try {
      studentInvoices.value = await db.getList('Fee Invoice', {
        filters: { student: actionEnr.value.student, docstatus: 1 },
        fields: ['name', 'total_amount'], order_by: 'creation desc',
      }) || []
    } catch (err) { console.error(err) }
  }
}

const submitAction = async () => {
  const enr = actionEnr.value
  const f = actionForm.value
  actionSaving.value = true
  try {
    if (actionType.value === 'defer') {
      if (!f.leave_from_date || !f.leave_to_date) { alert('Vui lòng nhập ngày bảo lưu.'); actionSaving.value = false; return }
      await call('defer_enrollment', { program_enrollment: enr.name, leave_from_date: f.leave_from_date, leave_to_date: f.leave_to_date, reason: f.reason || undefined })
    } else if (actionType.value === 'resume') {
      await call('resume_enrollment', { program_enrollment: enr.name })
    } else if (actionType.value === 'transfer') {
      if (!f.to_class) { alert('Vui lòng chọn lớp đích.'); actionSaving.value = false; return }
      await call('transfer_enrollment', { program_enrollment: enr.name, to_class: f.to_class, transfer_date: f.transfer_date || undefined, reason: f.reason || undefined })
    } else if (actionType.value === 'drop') {
      const params = { program_enrollment: enr.name, reason: f.reason || undefined }
      if (f.makeRefund) {
        if (!f.refund_invoice || !(Number(f.refund_amount) > 0)) { alert('Vui lòng chọn hóa đơn và nhập số tiền hoàn.'); actionSaving.value = false; return }
        params.refund_invoice = f.refund_invoice
        params.refund_amount = Number(f.refund_amount)
      }
      await call('drop_enrollment', params)
    } else {
      alert('Vui lòng chọn hành động.'); actionSaving.value = false; return
    }
    showActionModal.value = false
    enrollments.fetch()
    alert('Đã cập nhật trạng thái đăng ký.')
  } catch (err) {
    console.error(err)
    alert('Lỗi: ' + (err.messages?.join('\n') || err.message || ''))
  } finally {
    actionSaving.value = false
  }
}

const statusLabel = (s) => ({
  Pending: 'Chờ duyệt', Active: 'Đang học', Deferred: 'Bảo lưu', Transferred: 'Đã chuyển lớp',
  Completed: 'Hoàn thành', Dropped: 'Nghỉ học', Rejected: 'Từ chối',
}[s] || s || '—')

const statusClass = (s) => ({
  Active: 'bg-emerald-50 text-emerald-700',
  Pending: 'bg-amber-50 text-amber-700',
  Deferred: 'bg-blue-50 text-blue-700',
  Transferred: 'bg-indigo-50 text-indigo-700',
  Completed: 'bg-slate-100 text-slate-600',
  Dropped: 'bg-red-50 text-red-700',
  Rejected: 'bg-red-50 text-red-700',
}[s] || 'bg-slate-100 text-slate-600')

const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
</script>
