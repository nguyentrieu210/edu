<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Điểm Danh Lớp Học</h3>
        <p class="text-xs text-muted mt-1">Điểm danh theo từng buổi học (Class Session); mỗi học viên một bản ghi duy nhất / buổi.</p>
      </div>
      <button @click="saveAttendance" :disabled="saving" v-if="sessionLoaded" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-1.5-1.5M12 14l3-3m-3 3V4" />
        </svg>
        Lưu Điểm Danh
      </button>
    </div>

    <!-- Filters Toolbar -->
    <div class="rounded-xl border border-border bg-white p-4 shadow-sm flex flex-col md:flex-row items-stretch md:items-end gap-4">
      <div class="flex-1">
        <FormControl type="select" label="Lớp học *" v-model="selectedClass" :options="classOptions" @change="onClassChange" />
      </div>
      <div class="flex-1">
        <FormControl type="select" label="Buổi học *" v-model="selectedSession" :options="sessionOptions" :disabled="!selectedClass || loadingSessions" :placeholder="loadingSessions ? 'Đang tải buổi học...' : 'Chọn buổi học'" />
      </div>
      <button @click="loadSessionData" :disabled="loading || !selectedSession" class="px-6 py-2.5 text-sm font-medium text-ink-2 bg-white border border-border rounded-lg hover:bg-hover/40 transition-colors disabled:opacity-50">
        {{ loading ? 'Đang tải...' : 'Tải Danh Sách' }}
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <div v-else-if="sessionLoaded" class="space-y-6 animate-fade-in">
      <!-- Stats -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-5">
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng học viên</p>
          <h4 class="text-lg font-bold text-ink-2 mt-1">{{ stats.total }}</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Có mặt</p>
          <h4 class="text-lg font-bold text-brand mt-1">{{ stats.present }}</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Đi muộn</p>
          <h4 class="text-lg font-bold text-blue-600 mt-1">{{ stats.late }}</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Vắng (Có phép)</p>
          <h4 class="text-lg font-bold text-amber-600 mt-1">{{ stats.excused }}</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Vắng (Không phép)</p>
          <h4 class="text-lg font-bold text-thaco-red mt-1">{{ stats.unexcused }}</h4>
        </div>
      </div>

      <!-- Session + Teacher Attendance -->
      <div class="rounded-xl border border-border bg-white p-6 shadow-sm">
        <h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider mb-4">Buổi học & Điểm danh Giáo viên</h4>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-brand-soft text-brand flex items-center justify-center font-bold text-sm">
              {{ (currentSession.teacher || 'GV').charAt(0) }}
            </div>
            <div>
              <p class="font-semibold text-ink-2">{{ currentSession.session_date }} · {{ formatTime(currentSession.start_time) }}–{{ formatTime(currentSession.end_time) }}</p>
              <p class="text-xs text-muted">GV: {{ currentSession.teacher || '—' }} · Chủ đề: {{ currentSession.lesson_topic || 'Chưa cập nhật' }}</p>
            </div>
          </div>
          <div class="w-full sm:w-64">
            <select v-model="teacherStatus"
              class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white font-medium text-ink-2">
              <option value="">Điểm danh GV: chưa chọn...</option>
              <option value="Present">Có mặt (Present)</option>
              <option value="Absent">Vắng mặt (Absent)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Student Attendance Table -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40 flex items-center justify-between">
          <h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Danh sách Học viên (Active)</h4>
          <span class="text-xs text-muted font-medium font-mono">{{ students.length }} học viên</span>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-border">
            <thead class="bg-hover/40">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Học Viên</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-72">Trạng Thái</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-40">Loại tham dự</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted w-32">Phút muộn</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border bg-white">
              <tr v-if="students.length === 0">
                <td colspan="4" class="px-6 py-8 text-center text-sm text-muted">Lớp này chưa có học viên Active nào. Hãy đăng ký học viên vào lớp trước.</td>
              </tr>
              <tr v-for="st in students" :key="st.program_enrollment" class="hover:bg-hover/40 transition-colors">
                <td class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-ink-2">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-hover flex items-center justify-center font-bold text-xs text-muted">{{ (st.student || 'S').charAt(4) || 'S' }}</div>
                    <div>
                      <p class="font-medium text-ink-2">{{ st.student }}</p>
                      <p class="text-[11px] text-faint font-mono">{{ st.program_enrollment }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <select v-model="st.status"
                    class="w-full px-3 py-1.5 border border-border rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white font-medium text-ink-2">
                    <option value="Present">Có mặt</option>
                    <option value="Late">Đi muộn</option>
                    <option value="Absent with Permission">Vắng có phép</option>
                    <option value="Absent without Permission">Vắng không phép</option>
                  </select>
                </td>
                <td class="px-6 py-4">
                  <select v-model="st.attendance_type"
                    class="w-full px-3 py-1.5 border border-border rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white text-ink-2">
                    <option value="Regular">Chính khóa</option>
                    <option value="Make-up">Học bù</option>
                    <option value="Trial">Học thử</option>
                  </select>
                </td>
                <td class="px-6 py-4">
                  <input v-if="st.status === 'Late'" type="number" min="0" v-model="st.minutes_late"
                    class="w-24 px-3 py-1.5 border border-border rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand/30 text-ink-2" />
                  <span v-else class="text-xs text-faint">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else-if="searched && !sessionLoaded" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <svg class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <h3 class="mt-4 text-sm font-semibold text-ink">Chưa tải được buổi học</h3>
      <p class="mt-1 text-sm text-muted">Hãy chọn lớp và buổi học rồi bấm "Tải Danh Sách".</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, call } from '../api'

const classesList = apiResource('get_classes', { auto: true })

const classOptions = computed(() => {
  if (!classesList.data) return []
  return [{ label: 'Chọn lớp...', value: '' }, ...classesList.data.map(c => ({ label: `${c.name} - ${c.class_name}`, value: c.name }))]
})

const selectedClass = ref('')
const selectedSession = ref('')
const sessions = ref([])
const loadingSessions = ref(false)
const loading = ref(false)
const saving = ref(false)
const searched = ref(false)
const sessionLoaded = ref(false)
const currentSession = ref({})
const teacherStatus = ref('')
const students = ref([])

const sessionOptions = computed(() => [
  { label: 'Chọn buổi học...', value: '' },
  ...sessions.value.map(s => ({
    label: `${s.session_date} · ${formatTime(s.start_time)} · ${s.lesson_topic || 'Buổi học'}`,
    value: s.name,
  })),
])

const stats = computed(() => {
  const list = students.value || []
  return {
    total: list.length,
    present: list.filter(s => s.status === 'Present').length,
    late: list.filter(s => s.status === 'Late').length,
    excused: list.filter(s => s.status === 'Absent with Permission').length,
    unexcused: list.filter(s => s.status === 'Absent without Permission').length,
  }
})

const onClassChange = async () => {
  selectedSession.value = ''
  sessions.value = []
  sessionLoaded.value = false
  searched.value = false
  if (!selectedClass.value) return
  loadingSessions.value = true
  try {
    sessions.value = await call('get_class_sessions', { class_id: selectedClass.value }) || []
  } catch (err) {
    console.error(err)
  } finally {
    loadingSessions.value = false
  }
}

const loadSessionData = async () => {
  if (!selectedSession.value) { alert('Vui lòng chọn buổi học.'); return }
  loading.value = true
  searched.value = true
  sessionLoaded.value = false
  try {
    const res = await call('get_session_roster', { class_session: selectedSession.value })
    currentSession.value = res.session || {}
    teacherStatus.value = res.session?.teacher_attendance_status || ''
    students.value = (res.rows || []).map(r => ({ ...r }))
    sessionLoaded.value = true
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra khi tải dữ liệu.')
  } finally {
    loading.value = false
  }
}

const saveAttendance = async () => {
  saving.value = true
  try {
    const rows = students.value.map(s => ({
      program_enrollment: s.program_enrollment,
      student: s.student,
      status: s.status,
      attendance_type: s.attendance_type,
      minutes_late: s.status === 'Late' ? Number(s.minutes_late || 0) : 0,
    }))
    const res = await call('save_session_attendance', {
      class_session: selectedSession.value,
      rows: JSON.stringify(rows),
      teacher_attendance_status: teacherStatus.value || undefined,
    })
    alert(`Đã lưu điểm danh cho ${res.saved} học viên.`)
    loadSessionData()
  } catch (err) {
    console.error(err)
    alert('Lỗi khi lưu: ' + (err.messages?.join('\n') || err.message || ''))
  } finally {
    saving.value = false
  }
}

const formatTime = (t) => (t ? String(t).slice(0, 5) : '')
</script>
