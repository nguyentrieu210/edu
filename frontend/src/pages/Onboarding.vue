<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Quy Trình Nhập Học (Onboarding)</h3>
        <p class="text-xs text-muted mt-1">Quản lý và kiểm tra danh sách thủ tục nhập học của học viên mới.</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="rounded-xl border border-border bg-white p-4 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-end gap-4">
      <div class="flex-1">
        <FormControl type="select" label="Đăng ký học (Enrollment) *" v-model="selectedEnrollment" :options="enrollmentOptions" />
      </div>
      <button @click="loadTasks" :disabled="loading || !selectedEnrollment" class="px-6 py-2.5 text-sm font-medium text-ink-2 bg-white border border-border rounded-lg hover:bg-hover/40 transition-colors disabled:opacity-50">
        Tải Checklist
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="tasks.length > 0" class="space-y-6 animate-fade-in">
      <!-- Dynamic Progress -->
      <div class="bg-white p-6 rounded-xl border border-border shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm font-semibold text-ink-2">Tiến trình hoàn thành:</span>
            <p class="text-xs text-muted mt-0.5">Checklist cho học viên: <span class="font-semibold text-ink-2">{{ currentStudent }}</span></p>
          </div>
          <span class="text-sm font-bold text-brand">{{ completedCount }}/{{ totalCount }} ({{ progressPercentage }}%)</span>
        </div>
        <div class="w-full bg-hover rounded-full h-2.5 overflow-hidden">
          <div class="bg-brand h-2.5 rounded-full transition-all duration-500" :style="`width: ${progressPercentage}%`"></div>
        </div>
      </div>

      <!-- Checklist Tasks -->
      <div class="rounded-xl border border-border bg-white shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-border bg-hover/40 flex items-center justify-between">
          <h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Danh sách thủ tục nhập học</h4>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
            :class="progressPercentage === 100 ? 'bg-brand-soft text-brand' : 'bg-amber-100 text-amber-700'">
            {{ progressPercentage === 100 ? 'Hoàn thành' : 'Đang xử lý' }}
          </span>
        </div>
        
        <div class="p-6 space-y-3">
          <div v-for="task in tasks" :key="task.name" 
            class="flex items-center space-x-3 p-4 bg-white border rounded-xl hover:bg-hover/40/50 transition-all border-border hover:border-emerald-200">
            <input 
              type="checkbox" 
              class="w-5 h-5 text-brand rounded border-slate-300 focus:ring-brand cursor-pointer"
              :checked="task.is_completed"
              @change="toggleTask(task, $event.target.checked)"
            />
            <span class="text-sm font-medium transition-all duration-300" 
              :class="task.is_completed ? 'text-faint line-through' : 'text-ink-2'">
              {{ task.task_name }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="searched && tasks.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không có công việc nào</h3>
      <p class="mt-1 text-sm text-muted">Chưa có checklist cho đăng ký học này hoặc tính năng tự động sinh chưa chạy.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { listResource, db } from '../api'

const enrollmentsList = listResource('Program Enrollment', {
  fields: ['name', 'student'],
  limit_page_length: 100,
  order_by: 'creation desc',
  auto: true
})

const enrollmentOptions = computed(() => {
  if (!enrollmentsList.data) return []
  return enrollmentsList.data.map(e => ({ label: `${e.name} - ${e.student}`, value: e.name }))
})

const selectedEnrollment = ref('')
const loading = ref(false)
const searched = ref(false)
const tasks = ref([])
const currentStudent = ref('')

// Progress tracking calculations
const completedCount = computed(() => tasks.value.filter(t => t.is_completed).length)
const totalCount = computed(() => tasks.value.length)
const progressPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const loadTasks = async () => {
  if (!selectedEnrollment.value) return
  
  loading.value = true
  searched.value = true
  
  try {
    const res = await db.getList('Onboarding Task', {
      filters: { program_enrollment: selectedEnrollment.value },
      fields: ['name', 'task_name', 'is_completed', 'student'],
      limit_page_length: 50
    })

    tasks.value = res || []
    if (tasks.value.length > 0) {
      currentStudent.value = tasks.value[0].student
    }
  } catch (err) {
    console.error(err)
    alert('Lỗi tải dữ liệu')
  } finally {
    loading.value = false
  }
}

const toggleTask = async (task, isChecked) => {
  try {
    await db.setValue('Onboarding Task', task.name, 'is_completed', isChecked ? 1 : 0)
    task.is_completed = isChecked ? 1 : 0
  } catch (err) {
    console.error(err)
    alert('Lỗi cập nhật')
    // revert checkbox visually
    task.is_completed = !isChecked
  }
}
</script>
