<template>
  <div class="h-full flex flex-col">
    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-5 flex-shrink-0">
      <div class="relative">
        <input v-model="search" type="text" placeholder="Tìm khóa học..."
          class="pl-9 pr-4 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 w-64" />
        <svg class="absolute left-3 top-2.5 h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <button @click="showAddModal = true"
        class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Thêm khóa học
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-5 flex-shrink-0">
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-muted font-medium uppercase tracking-wider">Tổng khóa học</p>
        <p class="text-2xl font-bold text-ink-2 mt-1">{{ courses.data?.length || 0 }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-brand font-medium uppercase tracking-wider">Học phí TB</p>
        <p class="text-2xl font-bold text-brand mt-1">{{ formatCurrencyShort(avgFee) }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-blue-600 font-medium uppercase tracking-wider">Học phí cao nhất</p>
        <p class="text-2xl font-bold text-blue-600 mt-1">{{ formatCurrencyShort(maxFee) }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="courses.loading" class="flex items-center justify-center h-48">
      <div class="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!filteredCourses.length" class="flex flex-col items-center justify-center h-48 text-faint">
      <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <p class="text-sm font-medium">Chưa có khóa học nào</p>
    </div>

    <!-- Cards Grid -->
    <div v-else class="flex-1 overflow-y-auto">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="c in filteredCourses" :key="c.name"
          class="bg-white rounded-xl border border-border p-5 hover:shadow-md transition-shadow group">
          <div class="flex items-start justify-between mb-3">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <svg class="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <a :href="`/app/course/${c.name}`" target="_blank"
              class="text-xs text-faint hover:text-muted opacity-0 group-hover:opacity-100 transition-opacity border border-border rounded px-2 py-0.5">
              ↗ Desk
            </a>
          </div>
          <h3 class="font-semibold text-ink-2 mb-1">{{ c.course_name }}</h3>
          <p class="text-xs text-faint font-mono mb-3">{{ c.name }}</p>
          <div class="flex items-center justify-between">
            <span class="text-sm font-bold text-brand">{{ formatCurrency(c.base_fee) }}</span>
            <span class="text-xs text-faint">/ khóa</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" @click.self="showAddModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Thêm khóa học mới</h2>
          <button @click="showAddModal = false" class="text-faint hover:text-muted">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Tên khóa học *</label>
            <input v-model="newCourse.course_name" placeholder="VD: Tiếng Nhật N5..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Học phí (VNĐ)</label>
            <input v-model="newCourse.base_fee" type="number" placeholder="0"
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showAddModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveCourse" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : '✓ Lưu' }}
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
const showAddModal = ref(false)
const saving = ref(false)
const newCourse = ref({ course_name: '', base_fee: 0 })

const courses = apiResource('get_courses', { auto: true })

const avgFee = computed(() => {
  const data = courses.data || []
  if (!data.length) return 0
  return data.reduce((s, c) => s + (c.base_fee || 0), 0) / data.length
})
const maxFee = computed(() => Math.max(...(courses.data || []).map(c => c.base_fee || 0)))

const filteredCourses = computed(() =>
  (courses.data || []).filter(c =>
    !search.value || c.course_name?.toLowerCase().includes(search.value.toLowerCase())
  )
)

const formatCurrency = (v) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(v || 0)
const formatCurrencyShort = (v) => {
  if (!v) return '0₫'
  if (v >= 1000000) return (v / 1000000).toFixed(1) + 'M₫'
  if (v >= 1000) return (v / 1000).toFixed(0) + 'K₫'
  return v + '₫'
}

const saveCourse = async () => {
  if (!newCourse.value.course_name) return
  saving.value = true
  try {
    await db.insert({ doctype: 'Course', course_name: newCourse.value.course_name, base_fee: parseFloat(newCourse.value.base_fee) || 0 })
    showAddModal.value = false
    courses.fetch()
    newCourse.value = { course_name: '', base_fee: 0 }
  } catch (err) {
    alert('Lỗi: ' + (err.message || 'Không thể lưu'))
  } finally {
    saving.value = false
  }
}
</script>
