<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Bảng Điểm Học Viên</h3>
        <p class="text-xs text-muted mt-1">Cập nhật và theo dõi kết quả các bài kiểm tra định kỳ của lớp học.</p>
      </div>
      <button @click="saveAssessments" :disabled="saving" v-if="students.length > 0" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-1.5-1.5M12 14l3-3m-3 3V4" />
        </svg>
        Lưu Bảng Điểm
      </button>
    </div>

    <!-- Filters Toolbar -->
    <div class="rounded-xl border border-border bg-white p-4 shadow-sm flex flex-col md:flex-row items-stretch md:items-end gap-4">
      <div class="flex-1">
        <FormControl type="select" label="Lớp học *" v-model="selectedClass" :options="classOptions" />
      </div>
      <div class="w-full md:w-64">
        <FormControl label="Tên bài kiểm tra *" v-model="assessmentName" placeholder="VD: Giữa kỳ N5" />
      </div>
      <button @click="loadData" :disabled="loading" class="px-6 py-2.5 text-sm font-medium text-ink-2 bg-white border border-border rounded-lg hover:bg-hover/40 transition-colors disabled:opacity-50">
        {{ loading ? 'Đang tải...' : 'Tải Danh Sách' }}
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="students.length > 0" class="space-y-6 animate-fade-in">
      <!-- Statistics Card Grid -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
          <div class="p-3 bg-hover text-muted rounded-lg">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <p class="text-xs text-muted font-medium font-semibold uppercase tracking-wider">Tổng học viên</p>
            <h4 class="text-lg font-bold text-ink-2">{{ stats.total }}</h4>
          </div>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
          <div class="p-3 bg-brand-tint text-brand rounded-lg">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p class="text-xs text-muted font-medium font-semibold uppercase tracking-wider">Điểm trung bình</p>
            <h4 class="text-lg font-bold text-brand">{{ stats.average }}</h4>
          </div>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
          <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 11l3-3m0 0l3 3m-3-3v8m0-13a9 9 0 110 18 9 9 0 010-18z" />
            </svg>
          </div>
          <div>
            <p class="text-xs text-muted font-medium font-semibold uppercase tracking-wider">Cao nhất</p>
            <h4 class="text-lg font-bold text-blue-600">{{ stats.highest }}</h4>
          </div>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm flex items-center gap-3">
          <div class="p-3 bg-thaco-red-soft text-thaco-red rounded-lg">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13l-3 3m0 0l-3-3m3 3V8m0-5a9 9 0 110 18 9 9 0 010-18z" />
            </svg>
          </div>
          <div>
            <p class="text-xs text-muted font-medium font-semibold uppercase tracking-wider">Thấp nhất</p>
            <h4 class="text-lg font-bold text-thaco-red">{{ stats.lowest }}</h4>
          </div>
        </div>
      </div>

      <!-- Student Assessment Table -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40 flex items-center justify-between">
          <h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Bảng điểm lớp học</h4>
          <span class="text-xs text-muted font-medium font-mono">Bài thi: {{ assessmentName }}</span>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-border">
            <thead class="bg-hover/40">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Mã Học Viên</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-32">Điểm Số</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Nhận Xét</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border bg-white">
              <tr v-for="student in students" :key="student.student" class="hover:bg-hover/40 transition-colors">
                <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-ink-2">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-hover flex items-center justify-center font-bold text-xs text-muted">
                      {{ student.student?.charAt(4) || 'S' }}
                    </div>
                    <div>
                      <p class="font-medium text-ink-2">{{ student.student }}</p>
                    </div>
                  </div>
                </td>
                <td class="whitespace-nowrap px-6 py-4 text-sm">
                  <input type="number" v-model="student.score" min="0" max="100"
                    class="w-24 px-3 py-1.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 font-semibold text-ink-2" />
                </td>
                <td class="whitespace-nowrap px-6 py-4 text-sm">
                  <input type="text" v-model="student.notes" placeholder="Nhận xét của giáo viên (tùy chọn)..."
                    class="w-full max-w-md px-3 py-1.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 text-muted" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <div v-else-if="searched && students.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Không có dữ liệu</h3>
      <p class="mt-1 text-sm text-muted">Lớp học này chưa có học viên nào đăng ký.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, db } from '../api'

const classesList = apiResource('get_classes', { auto: true })

const classOptions = computed(() => {
  if (!classesList.data) return []
  return classesList.data.map(c => ({ label: c.class_name, value: c.name }))
})

const selectedClass = ref('')
const assessmentName = ref('')
const loading = ref(false)
const saving = ref(false)
const searched = ref(false)
const students = ref([])

// Compute stats
const stats = computed(() => {
  const list = students.value || []
  if (list.length === 0) return { total: 0, average: 0, highest: 0, lowest: 0 }
  
  const scores = list.map(s => Number(s.score) || 0)
  const total = list.length
  const sum = scores.reduce((a, b) => a + b, 0)
  const average = total > 0 ? (sum / total).toFixed(1) : 0
  const highest = Math.max(...scores)
  const lowest = Math.min(...scores)
  
  return {
    total,
    average,
    highest,
    lowest
  }
})

const loadData = async () => {
  if (!selectedClass.value || !assessmentName.value) {
    alert('Vui lòng chọn lớp học và nhập tên bài kiểm tra.')
    return
  }
  loading.value = true
  searched.value = true
  
  try {
    // 1. Fetch Enrolled Students
    const enrollmentRes = await db.getList('Program Enrollment', {
      filters: { class_id: selectedClass.value, docstatus: 1 },
      fields: ['student']
    })
    
    if (!enrollmentRes || enrollmentRes.length === 0) {
      students.value = []
      loading.value = false
      return
    }
    
    // 2. Fetch Existing Assessments
    const assessmentRes = await db.getList('Student Assessment', {
      filters: { class_id: selectedClass.value, assessment_name: assessmentName.value },
      fields: ['name', 'student', 'score', 'notes']
    })
    
    const assessMap = {}
    assessmentRes.forEach(a => { assessMap[a.student] = a })
    
    students.value = enrollmentRes.map(e => {
      const existing = assessMap[e.student]
      return {
        docname: existing ? existing.name : null,
        student: e.student,
        score: existing ? existing.score : 0,
        notes: existing ? existing.notes : ''
      }
    })
    
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra khi tải dữ liệu.')
  } finally {
    loading.value = false
  }
}

const saveAssessments = async () => {
  saving.value = true
  try {
    for (const st of students.value) {
      if (st.docname) {
        await db.setValue('Student Assessment', st.docname, { score: st.score, notes: st.notes })
      } else {
        await db.insert({
          doctype: 'Student Assessment',
          class_id: selectedClass.value,
          student: st.student,
          assessment_name: assessmentName.value,
          score: st.score,
          notes: st.notes
        })
      }
    }
    
    alert('Đã lưu bảng điểm thành công!')
    loadData()
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra khi lưu.')
  } finally {
    saving.value = false
  }
}
</script>
