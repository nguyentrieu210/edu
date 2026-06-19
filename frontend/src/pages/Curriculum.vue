<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Chương Trình & Giáo Án</h3>
        <p class="text-xs text-muted mt-1">Cấu trúc khóa học theo học phần và giáo án từng buổi (Kanji, từ vựng, ngữ pháp, đọc, nghe, kaiwa).</p>
      </div>
      <button v-if="selectedCourse" @click="openModuleModal()" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
        Thêm học phần
      </button>
    </div>

    <div class="rounded-xl border border-border bg-white p-4 shadow-sm">
      <FormControl type="select" label="Khóa học *" v-model="selectedCourse" :options="courseOptions" @change="loadCurriculum" />
    </div>

    <div v-if="loading" class="flex justify-center py-8"><LoadingIndicator /></div>

    <div v-else-if="selectedCourse && modules.length === 0" class="rounded-xl border border-border bg-white p-12 text-center shadow-sm">
      <h3 class="text-sm font-semibold text-ink">Khóa học chưa có học phần</h3>
      <p class="mt-1 text-sm text-muted">Thêm học phần đầu tiên để xây dựng chương trình.</p>
    </div>

    <div v-else class="space-y-4">
      <div v-for="m in modules" :key="m.name" class="rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40 flex items-center justify-between">
          <div>
            <h4 class="text-sm font-bold text-ink-2">{{ m.sequence ? `${m.sequence}. ` : '' }}{{ m.module_name }}</h4>
            <p v-if="m.description" class="text-xs text-muted mt-0.5">{{ m.description }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button @click="openLessonModal(m)" class="px-3 py-1.5 text-xs font-medium text-brand border border-brand/30 rounded-lg hover:bg-brand-tint/40">+ Buổi học</button>
            <button @click="deleteModule(m)" class="px-2 py-1.5 text-xs text-red-500 hover:text-red-700">Xóa</button>
          </div>
        </div>
        <div v-if="m.lessons && m.lessons.length" class="divide-y divide-border">
          <div v-for="l in m.lessons" :key="l.name" class="px-6 py-3 hover:bg-hover/30">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-ink-2">Buổi {{ l.lesson_no }}: {{ l.title }} <span v-if="l.duration_minutes" class="text-xs text-faint font-normal">· {{ l.duration_minutes }}'</span></p>
                <div class="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-xs text-muted">
                  <span v-if="l.kanji"><b class="text-faint">Kanji:</b> {{ l.kanji }}</span>
                  <span v-if="l.vocabulary"><b class="text-faint">Từ vựng:</b> {{ l.vocabulary }}</span>
                  <span v-if="l.grammar"><b class="text-faint">Ngữ pháp:</b> {{ l.grammar }}</span>
                  <span v-if="l.reading"><b class="text-faint">Đọc:</b> {{ l.reading }}</span>
                  <span v-if="l.listening"><b class="text-faint">Nghe:</b> {{ l.listening }}</span>
                  <span v-if="l.kaiwa"><b class="text-faint">Kaiwa:</b> {{ l.kaiwa }}</span>
                </div>
              </div>
              <button @click="deleteLesson(l)" class="px-2 py-1 text-xs text-red-500 hover:text-red-700 flex-shrink-0">Xóa</button>
            </div>
          </div>
        </div>
        <div v-else class="px-6 py-4 text-xs text-muted">Chưa có buổi học nào.</div>
      </div>
    </div>

    <!-- Module Modal -->
    <div v-if="showModuleModal" @click.self="showModuleModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <h2 class="text-lg font-bold text-ink-2 mb-4">Thêm học phần</h2>
        <div class="space-y-4">
          <FormControl label="Tên học phần *" v-model="moduleForm.module_name" placeholder="VD: Bài 1-5 (Minna no Nihongo)" />
          <FormControl type="number" label="Thứ tự" v-model="moduleForm.sequence" />
          <FormControl type="textarea" label="Mô tả" v-model="moduleForm.description" />
        </div>
        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showModuleModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveModule" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>

    <!-- Lesson Modal -->
    <div v-if="showLessonModal" @click.self="showLessonModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6 my-8 cursor-default">
        <h2 class="text-lg font-bold text-ink-2 mb-1">Thêm buổi học</h2>
        <p class="text-xs text-muted mb-4">Học phần: {{ activeModule?.module_name }}</p>
        <div class="space-y-4">
          <div class="grid grid-cols-3 gap-4">
            <FormControl type="number" label="Buổi số *" v-model="lessonForm.lesson_no" />
            <div class="col-span-2"><FormControl label="Tiêu đề *" v-model="lessonForm.title" /></div>
          </div>
          <FormControl type="number" label="Thời lượng (phút)" v-model="lessonForm.duration_minutes" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Kanji" v-model="lessonForm.kanji" />
            <FormControl label="Từ vựng" v-model="lessonForm.vocabulary" />
            <FormControl label="Ngữ pháp" v-model="lessonForm.grammar" />
            <FormControl label="Đọc hiểu" v-model="lessonForm.reading" />
            <FormControl label="Nghe hiểu" v-model="lessonForm.listening" />
            <FormControl label="Kaiwa" v-model="lessonForm.kaiwa" />
          </div>
          <FormControl type="textarea" label="Bài tập về nhà" v-model="lessonForm.homework" />
          <FormControl type="textarea" label="Tài liệu / đường dẫn" v-model="lessonForm.materials" />
        </div>
        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showLessonModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveLesson" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, call, db } from '../api'

const coursesList = apiResource('get_courses', { auto: true })
const courseOptions = computed(() => [
  { label: 'Chọn khóa học...', value: '' },
  ...(coursesList.data || []).map(c => ({ label: c.course_name, value: c.name })),
])

const selectedCourse = ref('')
const modules = ref([])
const loading = ref(false)
const saving = ref(false)

const showModuleModal = ref(false)
const moduleForm = ref({})
const showLessonModal = ref(false)
const activeModule = ref(null)
const lessonForm = ref({})

const loadCurriculum = async () => {
  modules.value = []
  if (!selectedCourse.value) return
  loading.value = true
  try {
    modules.value = await call('get_curriculum', { course: selectedCourse.value }) || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openModuleModal = () => {
  moduleForm.value = { module_name: '', sequence: modules.value.length + 1, description: '' }
  showModuleModal.value = true
}

const saveModule = async () => {
  if (!moduleForm.value.module_name) { alert('Nhập tên học phần.'); return }
  saving.value = true
  try {
    await db.insert({
      doctype: 'Curriculum Module',
      course: selectedCourse.value,
      module_name: moduleForm.value.module_name,
      sequence: Number(moduleForm.value.sequence || 0),
      description: moduleForm.value.description || '',
    })
    showModuleModal.value = false
    loadCurriculum()
  } catch (err) { alert('Lỗi: ' + (err.message || '')) } finally { saving.value = false }
}

const deleteModule = async (m) => {
  if (!confirm(`Xóa học phần "${m.module_name}" và toàn bộ buổi học bên trong?`)) return
  try {
    for (const l of (m.lessons || [])) await db.delete('Lesson Template', l.name)
    await db.delete('Curriculum Module', m.name)
    loadCurriculum()
  } catch (err) { alert('Lỗi: ' + (err.message || '')) }
}

const openLessonModal = (m) => {
  activeModule.value = m
  lessonForm.value = { lesson_no: (m.lessons?.length || 0) + 1, title: '', duration_minutes: '', kanji: '', vocabulary: '', grammar: '', reading: '', listening: '', kaiwa: '', homework: '', materials: '' }
  showLessonModal.value = true
}

const saveLesson = async () => {
  if (!lessonForm.value.title) { alert('Nhập tiêu đề buổi học.'); return }
  saving.value = true
  try {
    await db.insert({
      doctype: 'Lesson Template',
      curriculum_module: activeModule.value.name,
      lesson_no: Number(lessonForm.value.lesson_no || 0),
      title: lessonForm.value.title,
      duration_minutes: Number(lessonForm.value.duration_minutes || 0),
      kanji: lessonForm.value.kanji, vocabulary: lessonForm.value.vocabulary,
      grammar: lessonForm.value.grammar, reading: lessonForm.value.reading,
      listening: lessonForm.value.listening, kaiwa: lessonForm.value.kaiwa,
      homework: lessonForm.value.homework, materials: lessonForm.value.materials,
    })
    showLessonModal.value = false
    loadCurriculum()
  } catch (err) { alert('Lỗi: ' + (err.message || '')) } finally { saving.value = false }
}

const deleteLesson = async (l) => {
  if (!confirm(`Xóa buổi "${l.title}"?`)) return
  try { await db.delete('Lesson Template', l.name); loadCurriculum() } catch (err) { alert('Lỗi: ' + (err.message || '')) }
}
</script>
