<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="palette">
      <div v-if="isOpen" class="fixed inset-0 z-[999] flex items-start justify-center pt-[12vh]" @click.self="close">
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="close"></div>

        <!-- Panel -->
        <div class="relative w-full max-w-xl mx-4 bg-paper rounded-3xl shadow-[0_24px_64px_rgba(0,0,0,0.16),0_12px_32px_rgba(228,0,43,0.08)] border-2 border-brand/30 overflow-hidden z-10">

          <!-- Search Input -->
          <div class="flex items-center gap-3 px-5 py-4 border-b border-divider">
            <svg class="h-4.5 w-4.5 text-brand flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Tìm kiếm trang, học viên, tính năng..."
              class="flex-1 bg-transparent text-sm text-ink placeholder-muted outline-none font-medium"
              @keydown.down.prevent="moveDown"
              @keydown.up.prevent="moveUp"
              @keydown.enter.prevent="selectActive"
              @keydown.escape="close"
            />
            <kbd class="hidden sm:flex items-center gap-1 px-1.5 py-0.5 text-[10px] text-muted bg-hover border border-border rounded font-mono">
              ESC
            </kbd>
          </div>

          <!-- Results -->
          <div class="max-h-[420px] overflow-y-auto scrollbar-thin" ref="resultsRef">

            <!-- Empty State -->
            <div v-if="filteredGroups.length === 0" class="flex flex-col items-center justify-center py-12 text-muted">
              <svg class="h-10 w-10 mb-3 opacity-30 text-brand" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm font-medium text-ink">Không tìm thấy kết quả</p>
              <p class="text-xs mt-1 text-muted">Thử từ khóa khác</p>
            </div>

            <!-- Groups -->
            <div v-for="group in filteredGroups" :key="group.label">
              <div class="px-5 pt-4 pb-1.5">
                <span class="text-[10px] font-bold text-brand uppercase tracking-wider">{{ group.label }}</span>
              </div>
              <div class="px-3 pb-3 space-y-1">
                <button
                  v-for="(item, i) in group.items"
                  :key="item.id"
                  @click="selectItem(item)"
                  @mouseenter="activeIndex = item._globalIndex"
                  class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-left transition-all duration-150 group"
                  :class="activeIndex === item._globalIndex
                    ? 'bg-brand-soft text-brand'
                    : 'hover:bg-hover text-ink-2'"
                  :ref="el => { if (el) itemRefs[item._globalIndex] = el }"
                >
                  <!-- Icon -->
                  <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                    :class="activeIndex === item._globalIndex ? 'bg-brand/10' : 'bg-hover group-hover:bg-border/50'">
                    <span class="text-lg leading-none">{{ item.emoji }}</span>
                  </div>

                  <!-- Text -->
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold truncate" v-html="highlight(item.label)"></p>
                    <p v-if="item.subtitle" class="text-xs text-muted truncate mt-0.5"
                       :class="activeIndex === item._globalIndex ? 'text-brand-deep/70' : ''">{{ item.subtitle }}</p>
                  </div>

                  <!-- Shortcut / badge -->
                  <div class="flex items-center gap-2 flex-shrink-0">
                    <span v-if="item.badge" class="text-[10.5px] px-2.5 py-0.5 rounded-full font-semibold border"
                      :class="{
                        'bg-brand-soft text-brand border-brand/10': item.badge === 'Trang' && activeIndex !== item._globalIndex,
                        'bg-brand text-paper border-transparent': item.badge === 'Trang' && activeIndex === item._globalIndex,
                        'bg-blue-50 text-blue-600 border-blue-100': item.badge === 'Học viên' && activeIndex !== item._globalIndex,
                        'bg-blue-600 text-paper border-transparent': item.badge === 'Học viên' && activeIndex === item._globalIndex,
                        'bg-purple-50 text-purple-600 border-purple-100': item.badge === 'Lead' && activeIndex !== item._globalIndex,
                        'bg-purple-600 text-paper border-transparent': item.badge === 'Lead' && activeIndex === item._globalIndex,
                        'bg-amber-soft text-amber-700 border-amber-200': item.badge === 'Hành động' && activeIndex !== item._globalIndex,
                        'bg-amber-500 text-paper border-transparent': item.badge === 'Hành động' && activeIndex === item._globalIndex,
                      }">
                      {{ item.badge }}
                    </span>
                    <kbd v-if="activeIndex === item._globalIndex"
                      class="text-[10px] px-1.5 py-0.5 bg-brand/10 text-brand border border-brand/20 rounded font-mono">
                      ↵
                    </kbd>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 border-t border-divider flex items-center justify-between bg-hover/30">
            <div class="flex items-center gap-3 text-[11px] text-muted">
              <span class="flex items-center gap-1">
                <kbd class="px-1 py-0.5 bg-paper border border-border rounded font-mono">↑↓</kbd>
                Di chuyển
              </span>
              <span class="flex items-center gap-1">
                <kbd class="px-1 py-0.5 bg-paper border border-border rounded font-mono">↵</kbd>
                Chọn
              </span>
              <span class="flex items-center gap-1">
                <kbd class="px-1 py-0.5 bg-paper border border-border rounded font-mono">ESC</kbd>
                Đóng
              </span>
            </div>
            <div class="flex items-center gap-1 text-[11px] font-medium text-brand">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              IKE Search
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- State ---
const isOpen = ref(false)
const query = ref('')
const activeIndex = ref(0)
const inputRef = ref(null)
const resultsRef = ref(null)
const itemRefs = ref({})

// --- Static items (pages + actions) ---
const staticItems = [
  // Pages
  { id: 'p-dashboard',   label: 'Dashboard',               subtitle: 'Tổng quan hệ thống',          emoji: '🏠', badge: 'Trang',    action: () => router.push('/') },
  { id: 'p-students',    label: 'Học viên',                 subtitle: 'Quản lý danh sách học viên',  emoji: '👥', badge: 'Trang',    action: () => router.push('/students') },
  { id: 'p-student-card',label: 'Thẻ học viên',            subtitle: 'Cấp thẻ, gia hạn, in thẻ',   emoji: '🪪', badge: 'Trang',    action: () => router.push('/student-card') },
  { id: 'p-crm',         label: 'CRM Pipeline',            subtitle: 'Lead tiềm năng, Kanban',       emoji: '📊', badge: 'Trang',    action: () => router.push('/crm') },
  { id: 'p-appointments',label: 'Lịch hẹn',               subtitle: 'Lịch tư vấn, calendar view',  emoji: '📅', badge: 'Trang',    action: () => router.push('/appointments') },
  { id: 'p-onboarding',  label: 'Onboarding',              subtitle: 'Quy trình nhập học',          emoji: '✅', badge: 'Trang',    action: () => router.push('/onboarding') },
  { id: 'p-teachers',    label: 'Giáo viên',               subtitle: 'Quản lý đội ngũ giáo viên',  emoji: '👨‍🏫', badge: 'Trang', action: () => router.push('/teachers') },
  { id: 'p-courses',     label: 'Khóa học',                subtitle: 'Danh mục khóa học',           emoji: '📚', badge: 'Trang',    action: () => router.push('/courses') },
  { id: 'p-classes',     label: 'Lớp học',                 subtitle: 'Lịch lớp, sinh lịch học',     emoji: '🏫', badge: 'Trang',    action: () => router.push('/classes') },
  { id: 'p-enrollments', label: 'Đăng ký lớp',             subtitle: 'Gán học viên vào lớp, chốt học phí', emoji: '📝', badge: 'Trang', action: () => router.push('/enrollments') },
  { id: 'p-curriculum',  label: 'Chương trình & Giáo án',  subtitle: 'Học phần, giáo án theo kỹ năng', emoji: '📘', badge: 'Trang', action: () => router.push('/curriculum') },
  { id: 'p-homework',    label: 'Bài tập & Tài liệu',      subtitle: 'Giao bài, publish, tài liệu ôn tập', emoji: '📒', badge: 'Trang', action: () => router.push('/homework') },
  { id: 'p-attendance',  label: 'Điểm danh',               subtitle: 'Điểm danh học viên theo buổi',emoji: '📋', badge: 'Trang',    action: () => router.push('/attendance') },
  { id: 'p-assessments', label: 'Bảng điểm',              subtitle: 'Hiệu suất học tập',           emoji: '🎯', badge: 'Trang',    action: () => router.push('/assessments') },
  { id: 'p-room',        label: 'Thuê phòng',              subtitle: 'Đặt phòng học',               emoji: '🔑', badge: 'Trang',    action: () => router.push('/room-booking') },
  { id: 'p-tasks',       label: 'Task Board',              subtitle: 'Giao việc nội bộ Kanban',     emoji: '⚡', badge: 'Trang',    action: () => router.push('/task-board') },
  { id: 'p-invoices',    label: 'Hóa đơn',                subtitle: 'Quản lý hóa đơn học phí',     emoji: '🧾', badge: 'Trang',    action: () => router.push('/invoices') },
  { id: 'p-payments',    label: 'Phiếu thu',              subtitle: 'Lịch sử thu học phí',         emoji: '💰', badge: 'Trang',    action: () => router.push('/payments') },
  // Actions
  { id: 'a-desk',        label: 'Vào Frappe Desk',         subtitle: 'Mở trang quản trị Frappe',    emoji: '🖥️', badge: 'Hành động', action: () => { window.location.href = '/app' } },
  { id: 'a-new-student', label: 'Thêm học viên mới',       subtitle: 'Tạo hồ sơ học viên',          emoji: '➕', badge: 'Hành động', action: () => { router.push('/students'); close() } },
  { id: 'a-new-lead',    label: 'Thêm Lead mới',           subtitle: 'Tạo khách hàng tiềm năng',    emoji: '🎯', badge: 'Hành động', action: () => { router.push('/crm'); close() } },
  { id: 'a-new-apt',     label: 'Đặt lịch hẹn',           subtitle: 'Tạo lịch hẹn tư vấn',         emoji: '📆', badge: 'Hành động', action: () => { router.push('/appointments'); close() } },
]

// --- Computed filtered + grouped ---
const allFlatItems = computed(() => {
  const q = query.value.toLowerCase().trim()
  const filtered = q
    ? staticItems.filter(item =>
        item.label.toLowerCase().includes(q) ||
        item.subtitle?.toLowerCase().includes(q)
      )
    : staticItems

  // Assign global index for keyboard nav
  let idx = 0
  return filtered.map(item => ({ ...item, _globalIndex: idx++ }))
})

const filteredGroups = computed(() => {
  const items = allFlatItems.value
  const groups = []

  const pages = items.filter(i => i.badge === 'Trang')
  const actions = items.filter(i => i.badge === 'Hành động')
  const students = items.filter(i => i.badge === 'Học viên')
  const leads = items.filter(i => i.badge === 'Lead')

  if (pages.length) groups.push({ label: 'Điều hướng', items: pages })
  if (actions.length) groups.push({ label: 'Hành động nhanh', items: actions })
  if (students.length) groups.push({ label: 'Học viên', items: students })
  if (leads.length) groups.push({ label: 'Lead', items: leads })

  return groups
})

const totalItems = computed(() => allFlatItems.value.length)

// --- Keyboard nav ---
const moveDown = () => {
  activeIndex.value = (activeIndex.value + 1) % Math.max(totalItems.value, 1)
  scrollToActive()
}
const moveUp = () => {
  activeIndex.value = (activeIndex.value - 1 + Math.max(totalItems.value, 1)) % Math.max(totalItems.value, 1)
  scrollToActive()
}
const scrollToActive = () => {
  nextTick(() => {
    const el = itemRefs.value[activeIndex.value]
    el?.scrollIntoView({ block: 'nearest' })
  })
}

const selectActive = () => {
  const item = allFlatItems.value.find(i => i._globalIndex === activeIndex.value)
  if (item) selectItem(item)
}
const selectItem = (item) => {
  item.action?.()
  close()
}

// --- Highlight match ---
const highlight = (text) => {
  if (!query.value.trim()) return text
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${escaped})`, 'gi'),
    '<mark class="bg-brand-soft/80 text-brand rounded px-0.5 not-italic font-semibold">$1</mark>')
}

// --- Open / Close ---
const open = () => {
  isOpen.value = true
  query.value = ''
  activeIndex.value = 0
  nextTick(() => inputRef.value?.focus())
}
const close = () => {
  isOpen.value = false
  query.value = ''
}

// Reset activeIndex on query change
watch(query, () => { activeIndex.value = 0 })

// Global Ctrl+K listener
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value ? close() : open()
  }
}
onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

// Expose open for App.vue
defineExpose({ open, close })
</script>

<style scoped>
.palette-enter-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.palette-leave-active {
  transition: opacity 0.1s ease, transform 0.1s ease;
}
.palette-enter-from,
.palette-leave-to {
  opacity: 0;
  transform: scale(0.97) translateY(-8px);
}
</style>
