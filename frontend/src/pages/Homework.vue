<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Bài Tập & Tài Liệu</h3>
        <p class="text-xs text-muted mt-1">Giao bài tập theo lớp/buổi, publish cho học viên và quản lý tài liệu ôn tập.</p>
      </div>
      <button @click="openHwModal" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
        Giao bài tập
      </button>
    </div>

    <div class="rounded-xl border border-border bg-white p-4 shadow-sm">
      <FormControl type="select" label="Lọc theo lớp" v-model="filterClass" :options="classOptions" @change="reload" />
    </div>

    <!-- Homework list -->
    <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
      <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Bài tập</h4></div>
      <div v-if="homework.loading" class="flex justify-center py-8"><LoadingIndicator /></div>
      <div v-else-if="(homework.data || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Chưa có bài tập nào.</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-border">
          <thead class="bg-hover/40">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Tiêu đề</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Lớp</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Đối tượng</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Hạn nộp</th>
              <th class="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wider text-muted">Bài nộp</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng thái</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr v-for="h in homework.data" :key="h.name" class="hover:bg-hover/40">
              <td class="px-6 py-4 text-sm font-medium text-ink-2">{{ h.title }}</td>
              <td class="px-6 py-4 text-sm text-muted">{{ h.class_id }}</td>
              <td class="px-6 py-4 text-sm text-muted">{{ h.target === 'Individual' ? `Riêng: ${h.student}` : 'Cả lớp' }}</td>
              <td class="px-6 py-4 text-sm text-muted">{{ h.due_date || '—' }}</td>
              <td class="px-6 py-4 text-sm text-center tabular-nums">{{ h.submission_count }}</td>
              <td class="px-6 py-4 text-sm">
                <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium" :class="hwStatusClass(h.status)">{{ hwStatusLabel(h.status) }}</span>
              </td>
              <td class="px-6 py-4 text-right space-x-2">
                <button v-if="h.status === 'Draft'" @click="publishHw(h)" class="px-2.5 py-1 text-xs font-medium text-brand border border-brand/30 rounded-lg hover:bg-brand-tint/40">Publish</button>
                <button v-if="h.status === 'Published'" @click="closeHw(h)" class="px-2.5 py-1 text-xs font-medium text-ink-2 border border-border rounded-lg hover:bg-hover/40">Đóng</button>
                <span v-if="!['Draft','Published'].includes(h.status)" class="text-xs text-faint">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Materials -->
    <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
      <div class="px-6 py-4 border-b border-border bg-hover/40 flex items-center justify-between">
        <h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Tài liệu ôn tập</h4>
        <button @click="openMatModal" class="px-3 py-1.5 text-xs font-medium text-brand border border-brand/30 rounded-lg hover:bg-brand-tint/40">+ Thêm tài liệu</button>
      </div>
      <div v-if="materials.loading" class="flex justify-center py-6"><LoadingIndicator /></div>
      <div v-else-if="(materials.data || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Chưa có tài liệu.</div>
      <div v-else class="divide-y divide-border">
        <div v-for="m in materials.data" :key="m.name" class="px-6 py-3 flex items-center justify-between hover:bg-hover/30">
          <div class="min-w-0">
            <p class="text-sm font-medium text-ink-2">{{ m.title }} <span class="text-xs text-faint">· {{ m.material_type }}</span></p>
            <a v-if="m.url" :href="m.url" target="_blank" class="text-xs text-brand hover:underline break-all">{{ m.url }}</a>
          </div>
          <div class="flex items-center gap-3 flex-shrink-0">
            <span v-if="m.is_public" class="text-xs text-emerald-600">Công khai</span>
            <span v-else class="text-xs text-faint">Nội bộ</span>
            <button @click="deleteMat(m)" class="text-xs text-red-500 hover:text-red-700">Xóa</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Homework Modal -->
    <div v-if="showHwModal" @click.self="showHwModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 my-8 cursor-default">
        <h2 class="text-lg font-bold text-ink-2 mb-4">Giao bài tập</h2>
        <div class="space-y-4">
          <FormControl label="Tiêu đề *" v-model="hwForm.title" />
          <FormControl type="select" label="Lớp *" v-model="hwForm.class_id" :options="classOptions" />
          <FormControl type="select" label="Đối tượng" v-model="hwForm.target" :options="[{label:'Cả lớp',value:'Whole Class'},{label:'Cá nhân',value:'Individual'}]" />
          <FormControl v-if="hwForm.target === 'Individual'" type="select" label="Học viên *" v-model="hwForm.student" :options="studentOptions" />
          <FormControl type="date" label="Hạn nộp" v-model="hwForm.due_date" />
          <FormControl type="textarea" label="Nội dung bài tập" v-model="hwForm.description" />
          <FormControl type="textarea" label="Tài liệu / đường dẫn" v-model="hwForm.materials" />
        </div>
        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showHwModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveHw" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu (Draft)' }}</button>
        </div>
      </div>
    </div>

    <!-- Material Modal -->
    <div v-if="showMatModal" @click.self="showMatModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <h2 class="text-lg font-bold text-ink-2 mb-4">Thêm tài liệu</h2>
        <div class="space-y-4">
          <FormControl label="Tên tài liệu *" v-model="matForm.title" />
          <FormControl type="select" label="Loại" v-model="matForm.material_type" :options="[{label:'Tài liệu',value:'Document'},{label:'Liên kết',value:'Link'},{label:'Video',value:'Video'},{label:'Khác',value:'Other'}]" />
          <FormControl type="select" label="Lớp (tùy chọn)" v-model="matForm.class_id" :options="classOptions" />
          <FormControl label="Đường dẫn / URL" v-model="matForm.url" />
          <label class="flex items-center gap-2 text-sm text-ink-2"><input type="checkbox" v-model="matForm.is_public" class="w-4 h-4 rounded border-border text-brand focus:ring-brand" /> Hiển thị cho học viên</label>
          <FormControl type="textarea" label="Mô tả" v-model="matForm.description" />
        </div>
        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showMatModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveMat" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, LoadingIndicator } from 'frappe-ui'
import { apiResource, call, db } from '../api'

const classesList = apiResource('get_classes', { auto: true })
const classOptions = computed(() => [
  { label: 'Tất cả lớp', value: '' },
  ...(classesList.data || []).map(c => ({ label: `${c.name} - ${c.class_name}`, value: c.name })),
])

const filterClass = ref('')
const saving = ref(false)
const studentsList = ref([])

const homework = apiResource('get_homework', { auto: true })
const materials = apiResource('get_materials', { auto: true })

const reload = () => {
  homework.submit({ class_id: filterClass.value || undefined })
}

const studentOptions = computed(() => [
  { label: 'Chọn học viên...', value: '' },
  ...studentsList.value.map(s => ({ label: `${s.name} - ${s.full_name}`, value: s.name })),
])

// Homework modal
const showHwModal = ref(false)
const hwForm = ref({})
const openHwModal = async () => {
  hwForm.value = { title: '', class_id: filterClass.value || '', target: 'Whole Class', student: '', due_date: '', description: '', materials: '' }
  showHwModal.value = true
  if (!studentsList.value.length) {
    try { studentsList.value = await call('get_students') || [] } catch (e) { console.error(e) }
  }
}
const saveHw = async () => {
  if (!hwForm.value.title || !hwForm.value.class_id) { alert('Nhập tiêu đề và lớp.'); return }
  if (hwForm.value.target === 'Individual' && !hwForm.value.student) { alert('Chọn học viên.'); return }
  saving.value = true
  try {
    await db.insert({
      doctype: 'Homework', title: hwForm.value.title, class_id: hwForm.value.class_id,
      target: hwForm.value.target, student: hwForm.value.target === 'Individual' ? hwForm.value.student : null,
      due_date: hwForm.value.due_date || null, description: hwForm.value.description, materials: hwForm.value.materials, status: 'Draft',
    })
    showHwModal.value = false
    reload()
  } catch (err) { alert('Lỗi: ' + (err.message || '')) } finally { saving.value = false }
}
const publishHw = async (h) => {
  try { await call('publish_homework', { homework: h.name }); reload() } catch (err) { alert('Lỗi: ' + (err.messages?.join('\n') || err.message || '')) }
}
const closeHw = async (h) => {
  try { await call('close_homework', { homework: h.name }); reload() } catch (err) { alert('Lỗi: ' + (err.message || '')) }
}

// Material modal
const showMatModal = ref(false)
const matForm = ref({})
const openMatModal = () => { matForm.value = { title: '', material_type: 'Document', class_id: filterClass.value || '', url: '', is_public: true, description: '' }; showMatModal.value = true }
const saveMat = async () => {
  if (!matForm.value.title) { alert('Nhập tên tài liệu.'); return }
  saving.value = true
  try {
    await db.insert({
      doctype: 'Learning Material', title: matForm.value.title, material_type: matForm.value.material_type,
      class_id: matForm.value.class_id || null, url: matForm.value.url, is_public: matForm.value.is_public ? 1 : 0, description: matForm.value.description,
    })
    showMatModal.value = false
    materials.reload()
  } catch (err) { alert('Lỗi: ' + (err.message || '')) } finally { saving.value = false }
}
const deleteMat = async (m) => {
  if (!confirm(`Xóa tài liệu "${m.title}"?`)) return
  try { await db.delete('Learning Material', m.name); materials.reload() } catch (err) { alert('Lỗi: ' + (err.message || '')) }
}

const hwStatusLabel = (s) => ({ Draft: 'Nháp', Published: 'Đã publish', Closed: 'Đã đóng', Cancelled: 'Đã hủy' }[s] || s)
const hwStatusClass = (s) => ({ Draft: 'bg-slate-100 text-slate-600', Published: 'bg-emerald-50 text-emerald-700', Closed: 'bg-amber-50 text-amber-700', Cancelled: 'bg-red-50 text-red-700' }[s] || 'bg-slate-100 text-slate-600')
</script>
