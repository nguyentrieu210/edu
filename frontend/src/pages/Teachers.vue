<template>
  <div class="h-full flex flex-col">
    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-5 flex-shrink-0">
      <div class="flex items-center gap-3 flex-wrap">
        <div class="relative">
          <input v-model="search" type="text" placeholder="Tìm giáo viên..."
            class="pl-9 pr-4 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 w-64" />
          <svg class="absolute left-3 top-2.5 h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select v-model="filterStatus" class="text-sm border border-border rounded-lg px-3 py-2 bg-white text-muted focus:outline-none focus:ring-2 focus:ring-brand/30">
          <option value="">Tất cả</option>
          <option value="Active">Đang dạy</option>
          <option value="Inactive">Nghỉ</option>
        </select>
        <!-- Date Period Filter -->
        <div class="flex items-center gap-1 bg-white border border-border rounded-lg p-1">
          <button v-for="p in periods" :key="p.value" @click="periodFilter = p.value"
            class="px-3 py-1 text-xs font-medium rounded-md transition-all"
            :class="periodFilter === p.value ? 'bg-brand text-white shadow-sm' : 'text-muted hover:bg-hover/60'">
            {{ p.label }}
          </button>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <!-- Bulk delete bar -->
        <transition name="fade">
          <div v-if="selected.length > 0" class="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
            <span class="text-xs text-red-700 font-medium">Đã chọn {{ selected.length }}</span>
            <button @click="bulkDelete" class="flex items-center gap-1 px-2.5 py-1 bg-red-600 text-white text-xs font-medium rounded-md hover:bg-red-700 transition-colors">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Xóa
            </button>
            <button @click="selected = []" class="text-xs text-red-500 hover:text-red-700 font-medium">Bỏ chọn</button>
          </div>
        </transition>
        <button @click="showAddModal = true"
          class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Thêm giáo viên
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-5 flex-shrink-0">
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-muted font-medium uppercase tracking-wider">Tổng giáo viên</p>
        <p class="text-2xl font-bold text-ink-2 mt-1">{{ teachers.data?.length || 0 }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-brand font-medium uppercase tracking-wider">Đang dạy</p>
        <p class="text-2xl font-bold text-brand mt-1">{{ activeCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-faint font-medium uppercase tracking-wider">Nghỉ</p>
        <p class="text-2xl font-bold text-faint mt-1">{{ inactiveCount }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="teachers.loading" class="flex items-center justify-center h-48">
      <div class="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!filteredTeachers.length" class="flex flex-col items-center justify-center h-48 text-faint">
      <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <p class="text-sm font-medium">Chưa có giáo viên nào</p>
    </div>

    <!-- Table -->
    <div v-else class="flex-1 overflow-y-auto">
      <div class="bg-white rounded-xl border border-border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-divider bg-hover/40">
              <th class="px-4 py-3 w-10">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </th>
              <th class="text-left px-3 py-3 text-xs font-semibold text-muted uppercase tracking-wider w-12">STT</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Giáo viên</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Liên hệ</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Môn dạy</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Trạng thái</th>
              <th class="text-right px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, idx) in filteredTeachers" :key="t.name"
              class="border-b border-slate-50 hover:bg-hover/40 transition-colors"
              :class="selected.includes(t.name) ? 'bg-brand-tint/30' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="t.name" v-model="selected"
                  class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-3.5 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xs">
                    {{ t.teacher_name?.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium text-ink-2">{{ t.teacher_name }}</p>
                    <p class="text-xs text-faint font-mono">{{ t.name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-3.5">
                <p class="text-ink-2">{{ t.phone || '—' }}</p>
                <p class="text-xs text-faint">{{ t.email || '—' }}</p>
              </td>
              <td class="px-5 py-3.5 text-muted">{{ t.subject || '—' }}</td>
              <td class="px-5 py-3.5">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="t.status === 'Active' ? 'bg-brand-soft text-brand' : 'bg-hover text-muted'">
                  {{ t.status === 'Active' ? 'Đang dạy' : 'Nghỉ' }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <a :href="`/app/teacher/${t.name}`" target="_blank"
                  class="text-xs text-muted hover:text-ink-2 border border-border rounded-lg px-2.5 py-1 hover:bg-hover/40 transition-colors">
                  Xem ↗
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" @click.self="showAddModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Thêm giáo viên mới</h2>
          <button @click="showAddModal = false" class="text-faint hover:text-muted">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Tên giáo viên *</label>
            <input v-model="newTeacher.teacher_name" placeholder="Nhập họ và tên..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Số điện thoại</label>
              <input v-model="newTeacher.phone" placeholder="0901234567"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Email</label>
              <input v-model="newTeacher.email" type="email" placeholder="email@..."
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Trạng thái</label>
            <select v-model="newTeacher.status"
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
              <option value="Active">Đang dạy</option>
              <option value="Inactive">Nghỉ</option>
            </select>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showAddModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveTeacher" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : '✓ Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Delete Confirm Modal -->
    <div v-if="showDeleteConfirm" @click.self="showDeleteConfirm = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6 cursor-default">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
            <svg class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-ink-2">Xác nhận xóa</h3>
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> giáo viên. Hành động này không thể hoàn tác.</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
            {{ deleting ? 'Đang xóa...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { apiResource, db } from '../api'

const search = ref('')
const filterStatus = ref('')
const periodFilter = ref('')
const showAddModal = ref(false)
const saving = ref(false)
const selected = ref([])
const showDeleteConfirm = ref(false)
const deleting = ref(false)
const newTeacher = ref({ teacher_name: '', phone: '', email: '', status: 'Active' })

const periods = [
  { label: 'Tất cả', value: '' },
  { label: 'Tuần', value: 'week' },
  { label: 'Tháng', value: 'month' },
  { label: 'Quý', value: 'quarter' },
  { label: 'Năm', value: 'year' },
]

const teachers = apiResource('get_teachers', { auto: true })

const activeCount = computed(() => teachers.data?.filter(t => t.status === 'Active').length || 0)
const inactiveCount = computed(() => teachers.data?.filter(t => t.status !== 'Active').length || 0)

function getDateRange(period) {
  const now = new Date()
  let start = null
  if (period === 'week') {
    start = new Date(now); start.setDate(now.getDate() - 7)
  } else if (period === 'month') {
    start = new Date(now.getFullYear(), now.getMonth(), 1)
  } else if (period === 'quarter') {
    const q = Math.floor(now.getMonth() / 3)
    start = new Date(now.getFullYear(), q * 3, 1)
  } else if (period === 'year') {
    start = new Date(now.getFullYear(), 0, 1)
  }
  return start
}

const filteredTeachers = computed(() => {
  const start = getDateRange(periodFilter.value)
  return (teachers.data || []).filter(t => {
    const matchSearch = !search.value || t.teacher_name?.toLowerCase().includes(search.value.toLowerCase())
    const matchStatus = !filterStatus.value || t.status === filterStatus.value
    const matchPeriod = !start || !t.creation || new Date(t.creation) >= start
    return matchSearch && matchStatus && matchPeriod
  })
})

const allSelected = computed(() =>
  filteredTeachers.value.length > 0 && filteredTeachers.value.every(t => selected.value.includes(t.name))
)
function toggleSelectAll() {
  if (allSelected.value) {
    selected.value = []
  } else {
    selected.value = filteredTeachers.value.map(t => t.name)
  }
}

function bulkDelete() {
  if (!selected.value.length) return
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Teacher', name)
    }
    selected.value = []
    showDeleteConfirm.value = false
    teachers.fetch()
  } catch (err) {
    alert('Lỗi khi xóa: ' + (err.message || 'Vui lòng thử lại'))
  } finally {
    deleting.value = false
  }
}

const saveTeacher = async () => {
  if (!newTeacher.value.teacher_name) return
  saving.value = true
  try {
    await db.insert({ doctype: 'Teacher', ...newTeacher.value })
    showAddModal.value = false
    teachers.fetch()
    newTeacher.value = { teacher_name: '', phone: '', email: '', status: 'Active' }
  } catch (err) {
    alert('Lỗi: ' + (err.message || 'Không thể lưu giáo viên'))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateX(8px); }
</style>
