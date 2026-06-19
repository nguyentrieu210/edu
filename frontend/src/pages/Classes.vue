<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Quản lý Lớp Học</h3>
        <p class="text-xs text-muted mt-1">Quản lý danh sách lớp học, giáo viên chủ nhiệm và lịch học.</p>
      </div>
      <button @click="showCreateModal = true" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Mở Lớp Học
      </button>
    </div>

    <!-- Stats Card Grid -->
    <div v-if="!classes.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-4">
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-medium">Tổng số lớp</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.total }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-brand-tint text-brand rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-medium">Đang giảng dạy</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.ongoing }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-medium">Sắp khai giảng</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.upcoming }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-medium">Đã hoàn thành</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.completed }}</h4>
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
        <input v-model="searchQuery" placeholder="Tìm kiếm lớp học, mã lớp, hoặc khóa học..."
          class="w-full pl-10 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="statusFilter"
          class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
          <option value="">Tất cả trạng thái</option>
          <option value="Upcoming">Sắp khai giảng (Upcoming)</option>
          <option value="Ongoing">Đang học (Ongoing)</option>
          <option value="Completed">Hoàn thành (Completed)</option>
          <option value="Closed">Đã đóng (Closed)</option>
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

    <div v-if="classes.loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="filteredClasses.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không tìm thấy lớp học nào</h3>
      <p class="mt-1 text-sm text-muted">Thử thay đổi bộ lọc hoặc tạo một lớp học mới.</p>
      <div class="mt-6">
        <button @click="showCreateModal = true" class="flex items-center gap-2 mx-auto px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">Mở Lớp Học</button>
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
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Lớp</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Tên Lớp Học</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Khóa Học</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Giáo Viên</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Khai Giảng</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng Thái</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Hành Động</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="(cls, idx) in filteredClasses" :key="cls.name"
              class="hover:bg-hover/40 transition-colors"
              :class="selected.includes(cls.name) ? 'bg-brand-tint/30' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="cls.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-brand">
                <a :href="`/app/class/${cls.name}`" target="_blank" class="hover:underline">{{ cls.name }}</a>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-ink">{{ cls.class_name }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ cls.course }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ cls.teacher || 'Chưa xếp' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ cls.start_date || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="cls.status === 'Ongoing' ? 'bg-brand-soft text-brand' : cls.status === 'Upcoming' ? 'bg-blue-100 text-blue-700' : 'bg-hover text-muted'">
                  {{ cls.status }}
                </span>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-sm">
                <button :disabled="generating === cls.name" @click="generateSchedule(cls.name)" class="text-xs px-2.5 py-1 text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors disabled:opacity-50">
                  {{ generating === cls.name ? 'Đang sinh...' : 'Sinh Lịch' }}
                </button>
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
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> lớp học. Hành động này không thể hoàn tác.</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>

    <!-- Custom Modal -->
    <div v-if="showCreateModal" @click.self="showCreateModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Mở Lớp Học Mới</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <FormControl label="Tên lớp học *" v-model="newClass.class_name" :required="true" placeholder="VD: N5 Cấp tốc K1" />
          <FormControl label="Mã Khóa học *" v-model="newClass.course" :required="true" placeholder="VD: Khóa N5..." />
          <FormControl label="Giáo viên chủ nhiệm" v-model="newClass.teacher" placeholder="Nhập mã GV" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Ngày khai giảng" type="date" v-model="newClass.start_date" />
            <FormControl type="select" label="Mẫu lịch học" v-model="newClass.schedule_template" :options="['', '2-4-6', '3-5-7', 'T7-CN']" />
          </div>
          <div class="grid grid-cols-3 gap-4">
            <FormControl label="Giờ bắt đầu" type="time" v-model="newClass.start_time" />
            <FormControl label="Giờ kết thúc" type="time" v-model="newClass.end_time" />
            <FormControl label="Tổng số buổi" type="number" v-model="newClass.total_sessions" />
          </div>
          <FormControl 
            type="select" 
            label="Trạng thái" 
            v-model="newClass.status" 
            :options="[
              { label: 'Upcoming', value: 'Upcoming' },
              { label: 'Ongoing', value: 'Ongoing' },
              { label: 'Completed', value: 'Completed' },
              { label: 'Closed', value: 'Closed' }
            ]" 
          />
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveClass" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, db, call } from '../api'

const showCreateModal = ref(false)
const saving = ref(false)
const generating = ref(null)
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

const defaultClass = {
  class_name: '',
  course: '',
  teacher: '',
  start_date: '',
  schedule_template: '',
  start_time: '',
  end_time: '',
  total_sessions: 24,
  status: 'Upcoming'
}

const newClass = ref({ ...defaultClass })

const classes = apiResource('get_classes', { auto: true })

// Search & filter logic
const filteredClasses = computed(() => {
  if (!classes.data) return []
  const start = getDateRange(periodFilter.value)
  return classes.data.filter(cls => {
    const nameMatch = !searchQuery.value || 
      cls.class_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      cls.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      cls.course.toLowerCase().includes(searchQuery.value.toLowerCase())
    const statusMatch = !statusFilter.value || cls.status === statusFilter.value
    const periodMatch = !start || !cls.start_date || new Date(cls.start_date) >= start
    return nameMatch && statusMatch && periodMatch
  })
})

const allSelected = computed(() =>
  filteredClasses.value.length > 0 && filteredClasses.value.every(c => selected.value.includes(c.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredClasses.value.map(c => c.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Class', name)
    }
    selected.value = []; showDeleteConfirm.value = false; classes.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

// Stats calculations
const stats = computed(() => {
  const data = classes.data || []
  return {
    total: data.length,
    ongoing: data.filter(c => c.status === 'Ongoing').length,
    upcoming: data.filter(c => c.status === 'Upcoming').length,
    completed: data.filter(c => c.status === 'Completed').length
  }
})

const saveClass = async () => {
  if (!newClass.value.class_name || !newClass.value.course) {
    alert('Vui lòng nhập tên lớp và mã khóa học.')
    return
  }
  
  saving.value = true
  try {
    await db.insert({
      doctype: 'Class',
      class_name: newClass.value.class_name,
      course: newClass.value.course,
      teacher: newClass.value.teacher,
      start_date: newClass.value.start_date,
      schedule_template: newClass.value.schedule_template,
      start_time: newClass.value.start_time,
      end_time: newClass.value.end_time,
      total_sessions: newClass.value.total_sessions,
      status: newClass.value.status
    })
    showCreateModal.value = false
    classes.fetch()
    newClass.value = { ...defaultClass }
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra, vui lòng kiểm tra mã Khóa học và Giáo viên có tồn tại hay không.')
  } finally {
    saving.value = false
  }
}

const generateSchedule = async (className) => {
  if (!confirm(`Hệ thống sẽ xóa các ca học hiện tại của lớp ${className} và tự động sinh lại từ đầu. Bạn có chắc chắn?`)) return
  generating.value = className
  try {
    const res = await call('generate_class_sessions', { class_id: className })
    alert(res || 'Thành công')
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra: ' + (err.messages ? err.messages[0] : err.message || 'Vui lòng kiểm tra lại cấu hình mẫu lịch học của lớp'))
  } finally {
    generating.value = null
  }
}
</script>
