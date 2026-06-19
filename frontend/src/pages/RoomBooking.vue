<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Quản lý Đặt Phòng Học</h3>
        <p class="text-xs text-muted mt-1">Đặt lịch, theo dõi sử dụng và quản lý trạng thái các phòng học.</p>
      </div>
      <button @click="showCreateModal = true" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Đặt Phòng Học
      </button>
    </div>

    <!-- Stats Card Grid -->
    <div v-if="!bookings.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-4 animate-fade-in">
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-hover text-muted rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng số lượt đặt</p>
          <h4 class="text-lg font-bold text-ink-2">{{ stats.total }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đang đặt (Booked)</p>
          <h4 class="text-lg font-bold text-blue-600">{{ stats.booked }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-brand-tint text-brand rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đã kết thúc</p>
          <h4 class="text-lg font-bold text-brand">{{ stats.completed }}</h4>
        </div>
      </div>
      <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
        <div class="p-3 bg-thaco-red-soft text-thaco-red rounded-lg">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đã hủy bỏ</p>
          <h4 class="text-lg font-bold text-thaco-red">{{ stats.cancelled }}</h4>
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
        <input v-model="searchQuery" placeholder="Tìm kiếm theo phòng, người đặt, mục đích..."
          class="w-full pl-10 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="statusFilter"
          class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
          <option value="">Tất cả trạng thái</option>
          <option value="Booked">Đã đặt (Booked)</option>
          <option value="Completed">Đã kết thúc (Completed)</option>
          <option value="Cancelled">Đã hủy (Cancelled)</option>
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

    <div v-if="bookings.loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="filteredBookings.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không tìm thấy lịch đặt nào</h3>
      <p class="mt-1 text-sm text-muted">Hãy đặt lịch phòng mới cho các lớp học.</p>
      <div class="mt-6">
        <button @click="showCreateModal = true" class="flex items-center gap-2 mx-auto px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">Đặt Phòng Học</button>
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
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Đặt</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Phòng</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Ngày</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Giờ</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mục đích</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Người đặt</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng thái</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="(b, idx) in filteredBookings" :key="b.name"
              class="hover:bg-hover/40 transition-colors"
              :class="selected.includes(b.name) ? 'bg-brand-tint/30' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="b.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-brand">
                <a :href="`/app/room-booking/${b.name}`" target="_blank" class="hover:underline">{{ b.name }}</a>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm font-medium text-ink">{{ b.classroom }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ b.booking_date }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ b.start_time }} - {{ b.end_time }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ b.purpose || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-muted">{{ b.booked_by || '—' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-sm">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="b.status === 'Completed' ? 'bg-brand-soft text-brand' : b.status === 'Cancelled' ? 'bg-thaco-red-soft text-thaco-red' : 'bg-blue-100 text-blue-700'">
                  {{ translateStatus(b.status) }}
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
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> lịch đặt phòng. Hành động này không thể hoàn tác.</p>
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
          <h2 class="text-lg font-bold text-ink-2">Đặt Lịch Phòng Học</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <FormControl label="Phòng học *" v-model="newBooking.classroom" :required="true" placeholder="Nhập tên phòng, VD: Room 101" />
          <FormControl label="Ngày đặt *" type="date" v-model="newBooking.booking_date" :required="true" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Giờ bắt đầu *" type="time" v-model="newBooking.start_time" :required="true" />
            <FormControl label="Giờ kết thúc *" type="time" v-model="newBooking.end_time" :required="true" />
          </div>
          <FormControl label="Mục đích" v-model="newBooking.purpose" placeholder="Ví dụ: Dạy lớp N5 K1..." />
          <FormControl label="Người đặt" v-model="newBooking.booked_by" placeholder="Tên cán bộ/Giáo viên đặt phòng" />
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveBooking" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu đặt phòng' }}</button>
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

const newBooking = ref({
  classroom: '',
  booking_date: getTodayDate(),
  start_time: '08:00',
  end_time: '10:00',
  purpose: '',
  booked_by: ''
})

const bookings = listResource('Room Booking', {
  fields: ['name', 'classroom', 'booking_date', 'start_time', 'end_time', 'purpose', 'booked_by', 'status'],
  order_by: 'booking_date desc',
  limit_page_length: 50,
  auto: true
})

// Filter logic
const filteredBookings = computed(() => {
  if (!bookings.data) return []
  const start = getDateRange(periodFilter.value)
  return bookings.data.filter(b => {
    const searchMatch = !searchQuery.value || 
      b.classroom.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (b.purpose && b.purpose.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (b.booked_by && b.booked_by.toLowerCase().includes(searchQuery.value.toLowerCase()))
    const statusMatch = !statusFilter.value || b.status === statusFilter.value
    const periodMatch = !start || !b.booking_date || new Date(b.booking_date) >= start
    return searchMatch && statusMatch && periodMatch
  })
})

const allSelected = computed(() =>
  filteredBookings.value.length > 0 && filteredBookings.value.every(b => selected.value.includes(b.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredBookings.value.map(b => b.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Room Booking', name)
    }
    selected.value = []; showDeleteConfirm.value = false; bookings.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

// Stats calculations
const stats = computed(() => {
  const data = bookings.data || []
  return {
    total: data.length,
    booked: data.filter(b => b.status === 'Booked').length,
    completed: data.filter(b => b.status === 'Completed').length,
    cancelled: data.filter(b => b.status === 'Cancelled').length
  }
})

const saveBooking = async () => {
  if (!newBooking.value.classroom || !newBooking.value.booking_date) {
    alert('Vui lòng nhập Phòng học và Ngày đặt.')
    return
  }
  
  saving.value = true
  try {
    await db.insert({
      doctype: 'Room Booking',
      status: 'Booked',
      ...newBooking.value
    })
    showCreateModal.value = false
    bookings.fetch()
    newBooking.value = {
      classroom: '', booking_date: getTodayDate(), start_time: '08:00', end_time: '10:00', purpose: '', booked_by: ''
    }
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra: ' + (err.messages ? err.messages[0] : 'Vui lòng kiểm tra lại thông tin.'))
  } finally {
    saving.value = false
  }
}

const translateStatus = (status) => {
  if (status === 'Booked') return 'Đang đặt'
  if (status === 'Completed') return 'Hoàn thành'
  if (status === 'Cancelled') return 'Đã hủy'
  return status
}
</script>
