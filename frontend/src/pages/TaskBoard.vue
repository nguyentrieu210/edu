<template>
  <div class="space-y-6 h-[calc(100vh-140px)] flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Quản Lý Công Việc</h3>
        <p class="text-xs text-muted mt-1 font-medium">Kéo thả công việc để cập nhật tiến độ (To Do, In Progress, Done) một cách nhanh chóng.</p>
      </div>
      <button @click="showCreateModal = true" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo Công Việc
      </button>
    </div>

    <!-- Search Toolbar -->
    <div class="relative bg-white p-3 rounded-xl border border-border shadow-sm flex items-center flex-shrink-0">
      <span class="absolute left-6 text-faint">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </span>
      <input v-model="searchQuery" placeholder="Lọc nhanh công việc theo tiêu đề hoặc người phụ trách..."
        class="w-full pl-9 pr-4 py-1.5 border border-border rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40" />
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 flex space-x-2 pb-2 items-stretch select-none overflow-hidden">
      <div v-for="col in columns" :key="col.id" 
        class="flex-1 min-w-0 flex flex-col rounded-xl border p-2 transition-all duration-300"
        :class="[
          getColumnStyles(col.id).bg,
          activeDropCol === col.id ? getColumnStyles(col.id).bgDragover : 'border-slate-200/60'
        ]"
        @dragover.prevent="onDragOver(col.id)"
        @dragleave="onDragLeave"
        @drop="onDrop($event, col.id)"
      >
        <h4 class="font-bold text-ink-2 mb-3 px-1 flex justify-between items-center">
          <div class="flex items-center gap-1.5">
            <span class="h-1.5 w-1.5 rounded-full" :class="getColumnStyles(col.id).dot"></span>
            <span class="text-[11px] uppercase tracking-wider font-semibold">{{ col.label }}</span>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full transition-colors duration-200" :class="getColumnStyles(col.id).badge">
            {{ getTasks(col.id).length }}
          </span>
        </h4>
        
        <div class="flex-1 overflow-y-auto space-y-2 pr-0.5 min-h-[200px]">
          <div v-for="task in getTasks(col.id)" :key="task.name" 
            draggable="true"
            @dragstart="onDragStart($event, task)"
            class="bg-white p-2.5 rounded-lg shadow-sm border border-border/70 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-grab active:cursor-grabbing border-l-4" 
            :class="getPriorityBorder(task.priority)"
          >
            <div class="space-y-1.5 mb-2">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <div class="h-5 w-5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 flex items-center justify-center text-[9px] font-bold flex-shrink-0 uppercase">
                    {{ task.title ? task.title.charAt(0) : 'T' }}
                  </div>
                  <span class="text-[9px] text-slate-500 font-mono bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200 flex-shrink-0">{{ task.name }}</span>
                </div>
              </div>
              <span class="font-semibold text-ink-2 text-xs leading-snug break-words block">{{ task.title }}</span>
            </div>
            
            <div class="text-[11px] text-muted mb-2 space-y-1 bg-slate-50/50 rounded-lg p-1.5 border border-slate-100/80">
              <p class="flex items-center text-ink-2 font-medium">
                <svg class="w-3 h-3 mr-1 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="truncate">{{ task.assigned_to || 'Chưa giao phụ trách' }}</span>
              </p>
              <p class="flex items-center text-slate-500">
                <svg class="w-3 h-3 mr-1 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Hạn: {{ task.due_date || 'Không giới hạn' }}</span>
              </p>
            </div>
            
            <div class="pt-1.5 border-t border-divider flex items-center justify-between">
              <span class="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                :class="task.priority === 'High' ? 'bg-rose-50 text-rose-600 border border-rose-100' : task.priority === 'Medium' ? 'bg-amber-50 text-amber-600 border border-amber-100' : 'bg-slate-50 text-slate-500 border border-slate-200'">
                {{ task.priority === 'High' ? 'Cao' : task.priority === 'Medium' ? 'Vừa' : 'Thấp' }}
              </span>
              <select 
                class="text-[9px] bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-brand/20 text-muted font-medium transition-colors cursor-pointer"
                @change="updateStatus(task, $event.target.value)"
              >
                <option v-for="c in columns" :key="c.id" :value="c.id" :selected="c.id === task.status">
                  Mức: {{ c.label }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Modal -->
    <div v-if="showCreateModal" @click.self="showCreateModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Giao Việc Mới</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <FormControl label="Tên công việc *" v-model="newTask.title" :required="true" placeholder="VD: Chuẩn bị tài liệu khai giảng lớp mới" />
          <FormControl label="Người phụ trách" v-model="newTask.assigned_to" placeholder="Nhập email hoặc tên cán bộ..." />
          <FormControl label="Hạn chót" type="date" v-model="newTask.due_date" />
          <FormControl type="select" label="Mức độ ưu tiên" v-model="newTask.priority" :options="['Low', 'Medium', 'High']" />
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveTask" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu công việc' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { listResource, db } from '../api'

const columns = [
  { id: 'To Do', label: 'Cần làm' },
  { id: 'In Progress', label: 'Đang làm' },
  { id: 'Done', label: 'Đã xong' }
]

const showCreateModal = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const newTask = ref({ title: '', assigned_to: '', due_date: '', priority: 'Medium' })

const draggedTask = ref(null)
const activeDropCol = ref('')

const tasks = listResource('Internal Task', {
  fields: ['name', 'title', 'assigned_to', 'due_date', 'priority', 'status'],
  limit_page_length: 500,
  order_by: 'due_date asc',
  auto: true
})

const getTasks = (status) => {
  if (!tasks.data) return []
  return tasks.data.filter(t => t.status === status && 
    (!searchQuery.value || t.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
     (t.assigned_to && t.assigned_to.toLowerCase().includes(searchQuery.value.toLowerCase())))
  )
}

const getColumnStyles = (colId) => {
  const styles = {
    'To Do': {
      bg: 'bg-blue-50/20 border-blue-100/60',
      bgDragover: 'bg-blue-50/60 border-blue-400 ring-4 ring-blue-500/10',
      badge: 'bg-blue-100 text-blue-700',
      dot: 'bg-blue-500'
    },
    'In Progress': {
      bg: 'bg-amber-50/20 border-amber-100/60',
      bgDragover: 'bg-amber-50/60 border-amber-400 ring-4 ring-amber-500/10',
      badge: 'bg-amber-100 text-amber-700',
      dot: 'bg-amber-500'
    },
    'Done': {
      bg: 'bg-emerald-50/20 border-emerald-100/60',
      bgDragover: 'bg-emerald-50/60 border-emerald-400 ring-4 ring-emerald-500/10',
      badge: 'bg-emerald-100 text-emerald-700',
      dot: 'bg-emerald-500'
    }
  }
  return styles[colId] || {
    bg: 'bg-slate-50/20 border-slate-200/60',
    bgDragover: 'bg-slate-100/60 border-slate-400 ring-4 ring-slate-500/10',
    badge: 'bg-slate-200 text-slate-700',
    dot: 'bg-slate-400'
  }
}

const getPriorityBorder = (priority) => {
  if (priority === 'High') return 'border-l-rose-500'
  if (priority === 'Medium') return 'border-l-amber-500'
  return 'border-l-slate-300'
}

// Drag & Drop Handlers
const onDragStart = (event, task) => {
  draggedTask.value = task
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOver = (colId) => {
  activeDropCol.value = colId
}

const onDragLeave = () => {
  activeDropCol.value = ''
}

const onDrop = async (event, newStatus) => {
  activeDropCol.value = ''
  if (!draggedTask.value) return
  const task = draggedTask.value
  draggedTask.value = null

  if (task.status === newStatus) return

  const oldStatus = task.status
  task.status = newStatus // Optimistic update

  try {
    await db.setValue('Internal Task', task.name, 'status', newStatus)
    tasks.fetch()
  } catch (err) {
    console.error(err)
    task.status = oldStatus
    alert('Lỗi cập nhật trạng thái')
  }
}

const updateStatus = async (task, newStatus) => {
  if (task.status === newStatus) return
  
  try {
    await db.setValue('Internal Task', task.name, 'status', newStatus)
    tasks.fetch()
  } catch (err) {
    console.error(err)
    alert('Lỗi cập nhật trạng thái')
  }
}

const saveTask = async () => {
  if (!newTask.value.title) return alert('Nhập tên công việc')
  saving.value = true
  try {
    await db.insert({
      doctype: 'Internal Task',
      status: 'To Do',
      ...newTask.value
    })
    showCreateModal.value = false
    tasks.fetch()
    newTask.value = { title: '', assigned_to: '', due_date: '', priority: 'Medium' }
  } catch (err) {
    console.error(err)
    alert('Lỗi')
  } finally {
    saving.value = false
  }
}
</script>
