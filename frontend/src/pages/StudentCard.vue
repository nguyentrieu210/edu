<template>
  <div class="h-full flex flex-col">
    <!-- Header Toolbar -->
    <div class="flex items-center justify-between mb-5 flex-shrink-0">
      <div class="flex items-center gap-3">
        <div class="relative">
          <input
            v-model="search"
            type="text"
            placeholder="Tìm thẻ học viên..."
            class="pl-9 pr-4 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 w-64"
          />
          <svg class="absolute left-3 top-2.5 h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select v-model="filterStatus" class="text-sm border border-border rounded-lg px-3 py-2 bg-white text-muted focus:outline-none focus:ring-2 focus:ring-brand/30">
          <option value="">Tất cả trạng thái</option>
          <option value="active">Đang hoạt động</option>
          <option value="expired">Hết hạn</option>
          <option value="suspended">Tạm dừng</option>
        </select>
      </div>
      <button
        @click="showAddModal = true"
        class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Cấp thẻ mới
      </button>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-4 gap-4 mb-5 flex-shrink-0">
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-muted font-medium uppercase tracking-wider">Tổng thẻ</p>
        <p class="text-2xl font-bold text-ink-2 mt-1">{{ cards.length }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-brand font-medium uppercase tracking-wider">Đang hoạt động</p>
        <p class="text-2xl font-bold text-brand mt-1">{{ activeCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-thaco-red font-medium uppercase tracking-wider">Hết hạn</p>
        <p class="text-2xl font-bold text-thaco-red mt-1">{{ expiredCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-amber-500 font-medium uppercase tracking-wider">Sắp hết hạn</p>
        <p class="text-2xl font-bold text-amber-500 mt-1">{{ soonExpiredCount }}</p>
      </div>
    </div>

    <!-- Card Grid -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center h-48">
        <div class="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div v-else-if="filteredCards.length === 0" class="flex flex-col items-center justify-center h-48 text-faint">
        <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
        <p class="text-sm font-medium">Chưa có thẻ học viên nào</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="card in filteredCards"
          :key="card.name"
          class="bg-white rounded-xl border border-border overflow-hidden hover:shadow-md transition-shadow group"
        >
          <!-- Card Visual -->
          <div class="relative h-32 overflow-hidden" :class="cardGradient(card.status)">
            <div class="absolute inset-0 opacity-10">
              <div class="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white"></div>
              <div class="absolute -bottom-6 -left-6 w-32 h-32 rounded-full bg-white"></div>
            </div>
            <div class="relative p-4 h-full flex flex-col justify-between">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-white/80 uppercase tracking-wider">IKE Ohashi</span>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="statusBadge(card.status)">
                  {{ statusLabel(card.status) }}
                </span>
              </div>
              <div>
                <p class="text-white font-bold text-lg leading-tight">{{ card.student_name }}</p>
                <p class="text-white/70 text-xs font-mono">{{ card.name }}</p>
              </div>
            </div>
          </div>

          <!-- Card Details -->
          <div class="p-4 space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted">Mã học viên</span>
              <span class="font-medium text-ink-2 font-mono">{{ card.student || '—' }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted">Ngày cấp</span>
              <span class="font-medium text-ink-2">{{ formatDate(card.issue_date) }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted">Hết hạn</span>
              <span class="font-medium" :class="card.status === 'expired' ? 'text-thaco-red' : 'text-ink-2'">
                {{ formatDate(card.expiry_date) }}
              </span>
            </div>
            <div v-if="card.notes" class="pt-1 border-t border-divider">
              <p class="text-xs text-faint italic truncate">{{ card.notes }}</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="px-4 pb-4 flex gap-2">
            <button @click="printCard(card)" class="flex-1 text-xs py-1.5 rounded-lg border border-border text-muted hover:bg-hover/40 transition-colors font-medium">
              🖨️ In thẻ
            </button>
            <button @click="renewCard(card)" class="flex-1 text-xs py-1.5 rounded-lg bg-brand-tint text-brand hover:bg-brand-soft transition-colors font-medium border border-emerald-200">
              🔄 Gia hạn
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" @click.self="showAddModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Cấp thẻ học viên mới</h2>
          <button @click="showAddModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Học viên *</label>
            <input
              v-model="newCard.student_name"
              placeholder="Nhập tên học viên..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Mã học viên</label>
            <input
              v-model="newCard.student"
              placeholder="VD: STU-2024-0001"
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 font-mono"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngày cấp</label>
              <input
                v-model="newCard.issue_date"
                type="date"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Hết hạn</label>
              <input
                v-model="newCard.expiry_date"
                type="date"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
              />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ghi chú</label>
            <textarea
              v-model="newCard.notes"
              rows="2"
              placeholder="Ghi chú thêm..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 resize-none"
            ></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showAddModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">
            Hủy
          </button>
          <button @click="addCard" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : '✓ Cấp thẻ' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const search = ref('')
const filterStatus = ref('')
const loading = ref(false)
const saving = ref(false)
const showAddModal = ref(false)

const cards = ref([
  { name: 'STC-2024-0001', student: 'STU-2024-0001', student_name: 'Nguyễn Văn An', issue_date: '2024-01-15', expiry_date: '2024-12-31', status: 'active', notes: 'Học viên xuất sắc' },
  { name: 'STC-2024-0002', student: 'STU-2024-0002', student_name: 'Trần Thị Bình', issue_date: '2024-02-01', expiry_date: '2024-07-31', status: 'expired', notes: '' },
  { name: 'STC-2024-0003', student: 'STU-2024-0003', student_name: 'Lê Minh Châu', issue_date: '2024-03-10', expiry_date: '2024-12-10', status: 'active', notes: '' },
  { name: 'STC-2024-0004', student: 'STU-2024-0004', student_name: 'Phạm Thu Dung', issue_date: '2024-04-01', expiry_date: '2024-06-30', status: 'suspended', notes: 'Tạm dừng theo yêu cầu' },
  { name: 'STC-2024-0005', student: 'STU-2024-0005', student_name: 'Hoàng Văn Đức', issue_date: '2024-05-15', expiry_date: '2024-12-15', status: 'active', notes: '' },
])

const newCard = ref({
  student_name: '',
  student: '',
  issue_date: new Date().toISOString().split('T')[0],
  expiry_date: '',
  notes: ''
})

const activeCount = computed(() => cards.value.filter(c => c.status === 'active').length)
const expiredCount = computed(() => cards.value.filter(c => c.status === 'expired').length)
const soonExpiredCount = computed(() => {
  const now = new Date()
  const soon = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  return cards.value.filter(c => {
    const exp = new Date(c.expiry_date)
    return c.status === 'active' && exp <= soon && exp > now
  }).length
})

const filteredCards = computed(() => {
  return cards.value.filter(c => {
    const matchSearch = !search.value || c.student_name.toLowerCase().includes(search.value.toLowerCase()) || c.name.toLowerCase().includes(search.value.toLowerCase())
    const matchStatus = !filterStatus.value || c.status === filterStatus.value
    return matchSearch && matchStatus
  })
})

const cardGradient = (status) => {
  if (status === 'active') return 'bg-gradient-to-br from-emerald-500 to-teal-600'
  if (status === 'expired') return 'bg-gradient-to-br from-slate-400 to-slate-600'
  if (status === 'suspended') return 'bg-gradient-to-br from-amber-400 to-orange-500'
  return 'bg-gradient-to-br from-slate-400 to-slate-600'
}

const statusBadge = (status) => {
  if (status === 'active') return 'bg-white/20 text-white'
  if (status === 'expired') return 'bg-black/20 text-white'
  if (status === 'suspended') return 'bg-white/20 text-white'
  return 'bg-white/20 text-white'
}

const statusLabel = (status) => {
  if (status === 'active') return 'Hoạt động'
  if (status === 'expired') return 'Hết hạn'
  if (status === 'suspended') return 'Tạm dừng'
  return status
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('vi-VN')
}

const addCard = async () => {
  if (!newCard.value.student_name) return
  saving.value = true
  await new Promise(r => setTimeout(r, 500))
  cards.value.unshift({
    name: `STC-2024-${String(cards.value.length + 1).padStart(4, '0')}`,
    student_name: newCard.value.student_name,
    student: newCard.value.student,
    issue_date: newCard.value.issue_date,
    expiry_date: newCard.value.expiry_date,
    status: 'active',
    notes: newCard.value.notes
  })
  newCard.value = { student_name: '', student: '', issue_date: new Date().toISOString().split('T')[0], expiry_date: '', notes: '' }
  saving.value = false
  showAddModal.value = false
}

const printCard = (card) => {
  alert(`In thẻ cho: ${card.student_name}`)
}

const renewCard = (card) => {
  const expiry = new Date(card.expiry_date)
  expiry.setFullYear(expiry.getFullYear() + 1)
  card.expiry_date = expiry.toISOString().split('T')[0]
  card.status = 'active'
}
</script>
