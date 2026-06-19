<template>
  <div class="h-full flex flex-col">
    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-5 flex-shrink-0 flex-wrap gap-3">
      <div class="flex items-center gap-3 flex-wrap">
        <div class="relative">
          <input v-model="search" type="text" placeholder="Tìm khách hàng..."
            class="pl-9 pr-4 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 w-64" />
          <svg class="absolute left-3 top-2.5 h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select v-model="filterStatus" class="text-sm border border-border rounded-lg px-3 py-2 bg-white text-muted focus:outline-none focus:ring-2 focus:ring-brand/30">
          <option value="">Tất cả trạng thái</option>
          <option value="New">Mới</option>
          <option value="Consulting">Đang tư vấn</option>
          <option value="Testing">Test đầu vào</option>
          <option value="Trial">Học thử</option>
          <option value="Enrolled">Đã nhập học</option>
          <option value="Lost">Không thành công</option>
        </select>
        <!-- Period Filter -->
        <div class="flex items-center gap-1 bg-white border border-border rounded-lg p-1">
          <button v-for="p in periods" :key="p.value" @click="periodFilter = p.value"
            class="px-3 py-1 text-xs font-medium rounded-md transition-all"
            :class="periodFilter === p.value ? 'bg-brand text-white shadow-sm' : 'text-muted hover:bg-hover/60'">
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
      <button @click="showAddModal = true"
        class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Thêm khách hàng
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4 mb-5 flex-shrink-0">
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-muted font-medium uppercase tracking-wider">Tổng Leads</p>
        <p class="text-2xl font-bold text-ink-2 mt-1">{{ leads.data?.length || 0 }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-blue-500 font-medium uppercase tracking-wider">Mới</p>
        <p class="text-2xl font-bold text-blue-500 mt-1">{{ countStatus('New') }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-indigo-500 font-medium uppercase tracking-wider">Đang tư vấn</p>
        <p class="text-2xl font-bold text-indigo-500 mt-1">{{ countStatus('Consulting') }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4">
        <p class="text-xs text-emerald-500 font-medium uppercase tracking-wider">Thành công (Enrolled)</p>
        <p class="text-2xl font-bold text-emerald-500 mt-1">{{ countStatus('Enrolled') }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="leads.loading" class="flex items-center justify-center h-48">
      <div class="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!filteredLeads.length" class="flex flex-col items-center justify-center h-48 text-faint">
      <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <p class="text-sm font-medium">Chưa có khách hàng nào</p>
    </div>

    <!-- Table -->
    <div v-else class="flex-1 overflow-y-auto">
      <div class="bg-white rounded-xl border border-border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-divider bg-hover/40">
              <th class="px-4 py-3 w-10">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </th>
              <th class="text-left px-3 py-3 text-xs font-semibold text-muted uppercase tracking-wider w-12">STT</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Khách hàng</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Liên hệ</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Nguồn</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Trạng thái</th>
              <th class="text-left px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Ngày tạo</th>
              <th class="text-right px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(l, idx) in filteredLeads" :key="l.name"
              @click="openDetailModal(l)"
              class="border-b border-slate-50 hover:bg-hover/30 transition-colors cursor-pointer"
              :class="selected.includes(l.name) ? 'bg-brand-tint/30' : ''"
            >
              <td class="px-4 py-3" @click.stop>
                <input type="checkbox" :value="l.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-3.5 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-xs">
                    {{ l.lead_name?.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium text-ink-2">{{ l.lead_name }}</p>
                    <p class="text-xs text-faint font-mono">{{ l.name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-3.5">
                <p class="text-ink-2">{{ l.phone || '—' }}</p>
                <p class="text-xs text-faint">{{ l.email || '—' }}</p>
              </td>
              <td class="px-5 py-3.5 text-muted">
                <div>{{ l.source || '—' }}</div>
                <div v-if="l.occupation" class="text-xs text-faint">{{ l.occupation }}</div>
              </td>
              <td class="px-5 py-3.5">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusClass(l.status)">
                  {{ getStatusLabel(l.status) }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-muted text-xs">
                {{ l.creation ? l.creation.split(' ')[0] : '—' }}
              </td>
              <td class="px-5 py-3.5 text-right" @click.stop>
                <select 
                  @change="triggerStatusTransition(l, $event.target.value)"
                  class="text-xs bg-white border border-border rounded-lg p-1.5 focus:outline-none focus:ring-1 focus:ring-brand font-semibold text-muted cursor-pointer"
                >
                  <option value="" disabled selected>Chuyển Trạng thái...</option>
                  <option v-for="col in pipelineSteps" :key="col.id" :value="col.id" :disabled="col.id === l.status">
                    Mức: {{ col.label }}
                  </option>
                  <option value="Lost" :disabled="l.status === 'Lost'">Thất bại (Lost)</option>
                </select>
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
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> khách hàng. Hành động này không thể hoàn tác.</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>

    <!-- Lead Detail Modal -->
    <div v-if="detailModal.show" @click.self="detailModal.show = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl mx-4 p-6 overflow-y-auto max-h-[90vh] cursor-default">
        <div class="flex items-center justify-between mb-4 border-b border-divider pb-3">
          <div>
            <h2 class="text-lg font-bold text-ink-2">{{ detailModal.lead.lead_name }}</h2>
            <p class="text-xs text-faint font-mono mt-0.5">{{ detailModal.lead.name }}</p>
          </div>
          <button @click="detailModal.show = false" class="text-faint hover:text-muted">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Pipeline Progress Bar -->
        <div class="mb-5 bg-hover/40 p-3 rounded-xl border border-border flex items-center justify-between">
          <div class="flex items-center gap-1.5 flex-1">
            <template v-for="(step, idx) in pipelineSteps" :key="step.id">
              <button 
                @click="triggerStatusTransition(detailModal.lead, step.id)"
                class="flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all text-center"
                :class="getPipelineStepClass(detailModal.lead.status, step.id)"
              >
                {{ step.label }}
              </button>
              <svg v-if="idx < pipelineSteps.length - 1" class="h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </template>
          </div>
          <div class="ml-4 border-l border-divider pl-4">
            <button 
              @click="triggerStatusTransition(detailModal.lead, 'Lost')"
              class="px-4 py-1.5 text-xs font-bold rounded-lg border transition-all"
              :class="detailModal.lead.status === 'Lost' ? 'bg-red-500 text-white border-red-500' : 'bg-white border-border text-red-500 hover:bg-red-50'"
            >
              Thất bại (Lost)
            </button>
          </div>
        </div>

        <div class="grid grid-cols-12 gap-5">
          <!-- Column 1: Info & Files -->
          <div class="col-span-4 bg-slate-50 p-4 rounded-xl border border-border space-y-4 text-xs">
            <div>
              <h4 class="font-bold text-ink-2 border-b border-divider pb-2 text-xs uppercase tracking-wider text-brand">Hồ sơ chi tiết</h4>
              <div class="grid grid-cols-3 gap-y-2 mt-2 text-muted">
                <span class="font-semibold">Ngày sinh:</span>
                <span class="col-span-2 text-ink-2">{{ detailModal.lead.date_of_birth || '—' }}</span>

                <span class="font-semibold">Giới tính:</span>
                <span class="col-span-2 text-ink-2">{{ detailModal.lead.gender || '—' }}</span>

                <span class="font-semibold">Ngành nghề:</span>
                <span class="col-span-2 text-ink-2">{{ detailModal.lead.occupation || '—' }}</span>

                <span class="font-semibold">Người giám hộ:</span>
                <span class="col-span-2 text-ink-2 font-medium">{{ detailModal.lead.guardian_name || '—' }}</span>

                <span class="font-semibold">SĐT Phụ huynh:</span>
                <span class="col-span-2 text-ink-2">{{ detailModal.lead.guardian_phone || '—' }}</span>

                <span v-if="detailModal.lead.status === 'Lost'" class="font-semibold text-red-500">Lý do thất bại:</span>
                <span v-if="detailModal.lead.status === 'Lost'" class="col-span-2 text-red-600 font-medium bg-red-50 p-1.5 rounded">{{ detailModal.lead.lost_reason || 'Chưa ghi nhận' }}</span>
              </div>
            </div>

            <div class="border-t border-divider pt-3 space-y-2">
              <h5 class="font-bold text-ink-2 text-xs uppercase tracking-wider text-brand">Tài liệu đính kèm</h5>
              <div v-if="!details[detailModal.lead.name]?.files?.length" class="text-faint text-[11px]">
                Chưa có tài liệu đính kèm nào
              </div>
              <div v-else class="space-y-1.5">
                <div v-for="f in details[detailModal.lead.name]?.files" :key="f.name" class="flex items-center gap-1.5 text-xs text-brand hover:underline bg-white p-2 rounded-lg border border-border shadow-sm">
                  <span>📎</span>
                  <a :href="f.file_url" target="_blank" class="truncate font-medium text-brand hover:text-brand-deep">{{ f.file_name }}</a>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Consultation History -->
          <div class="col-span-4 bg-white p-4 rounded-xl border border-border flex flex-col h-[350px]">
            <div class="flex items-center justify-between border-b border-divider pb-2 mb-3">
              <h4 class="font-bold text-ink-2 text-xs uppercase tracking-wider text-brand">Nhật ký tư vấn</h4>
              <button 
                @click="openQuickAddLog(detailModal.lead)"
                class="text-[10px] font-bold text-white bg-brand px-2 py-0.5 rounded hover:bg-brand-deep"
              >+ Thêm</button>
            </div>

            <div class="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
              <div v-if="!details[detailModal.lead.name]?.logs.length" class="text-faint text-center py-8">
                Chưa có nhật ký tư vấn nào
              </div>
              <div v-for="log in details[detailModal.lead.name]?.logs" :key="log.name" class="p-2.5 bg-slate-50 border border-border rounded-lg relative">
                <div class="flex justify-between items-center text-[10px] text-faint mb-1">
                  <span>Ngày: {{ log.contact_date }}</span>
                  <span v-if="log.next_follow_up" class="text-amber-600 font-medium">Hẹn lại: {{ log.next_follow_up }}</span>
                </div>
                <p class="text-ink-2 leading-relaxed whitespace-pre-line">{{ log.notes }}</p>
              </div>
            </div>
          </div>

          <!-- Column 3: Placement Test -->
          <div class="col-span-4 bg-white p-4 rounded-xl border border-border flex flex-col h-[350px]">
            <div class="flex items-center justify-between border-b border-divider pb-2 mb-3">
              <h4 class="font-bold text-ink-2 text-xs uppercase tracking-wider text-brand">Placement Test</h4>
              <button 
                @click="openQuickAddTest(detailModal.lead)"
                class="text-[10px] font-bold text-white bg-brand px-2 py-0.5 rounded hover:bg-brand-deep"
              >+ Ghi điểm</button>
            </div>

            <div class="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
              <div v-if="!details[detailModal.lead.name]?.tests.length" class="text-faint text-center py-8">
                Chưa có kết quả kiểm tra
              </div>
              <div v-for="t in details[detailModal.lead.name]?.tests" :key="t.name" class="p-2.5 bg-emerald-50/50 border border-emerald-100 rounded-lg">
                <div class="flex justify-between items-center text-[10px] text-faint mb-1">
                  <span class="text-emerald-700 font-bold">Ngày thi: {{ t.test_date }}</span>
                  <span class="font-bold text-white bg-emerald-600 px-1.5 py-0.5 rounded text-[10px]">{{ t.score }} Điểm</span>
                </div>
                <p class="text-ink-2 font-medium text-[11px]" v-if="t.recommended_course">Đề xuất khóa học: {{ t.recommended_course }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Consultation Log Add Inline Modal -->
    <div v-if="quickLogModal.show" @click.self="quickLogModal.show = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <h3 class="text-sm font-bold text-ink-2 mb-4 uppercase tracking-wider text-brand">Thêm nhật ký tư vấn</h3>
        <div class="space-y-3 text-xs">
          <div>
            <label class="block text-muted font-bold mb-1">Ngày liên hệ</label>
            <input type="date" v-model="quickLogModal.form.contact_date" class="w-full px-3 py-2 border border-border rounded-lg" />
          </div>
          <div>
            <label class="block text-muted font-bold mb-1">Hẹn ngày gọi lại (Không bắt buộc)</label>
            <input type="date" v-model="quickLogModal.form.next_follow_up" class="w-full px-3 py-2 border border-border rounded-lg" />
          </div>
          <div>
            <label class="block text-muted font-bold mb-1">Nội dung trao đổi</label>
            <textarea v-model="quickLogModal.form.notes" rows="4" placeholder="Nhập ghi chú chi tiết..." class="w-full px-3 py-2 border border-border rounded-lg"></textarea>
          </div>
        </div>
        <div class="flex gap-2 mt-5 border-t border-divider pt-3 text-xs">
          <button @click="quickLogModal.show = false" class="flex-1 py-2 font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveQuickLog" :disabled="quickLogModal.saving" class="flex-1 py-2 font-bold text-white bg-brand rounded-lg hover:bg-brand-deep">
            {{ quickLogModal.saving ? 'Đang lưu...' : '✓ Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Placement Test Score Add Inline Modal -->
    <div v-if="quickTestModal.show" @click.self="quickTestModal.show = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <h3 class="text-sm font-bold text-ink-2 mb-4 uppercase tracking-wider text-brand">Ghi nhận điểm Placement Test</h3>
        <div class="space-y-3 text-xs">
          <div>
            <label class="block text-muted font-bold mb-1">Ngày thi *</label>
            <input type="date" v-model="quickTestModal.form.test_date" class="w-full px-3 py-2 border border-border rounded-lg" />
          </div>
          <div>
            <label class="block text-muted font-bold mb-1">Điểm số *</label>
            <input type="number" step="0.5" v-model="quickTestModal.form.score" placeholder="Nhập số điểm (ví dụ: 7.5)" class="w-full px-3 py-2 border border-border rounded-lg" />
          </div>
          <div>
            <label class="block text-muted font-bold mb-1">Khóa học đề xuất</label>
            <select v-model="quickTestModal.form.recommended_course" class="w-full px-3 py-2 border border-border rounded-lg bg-white">
              <option value="">Chọn khóa học...</option>
              <option v-for="c in courses.data" :key="c.name" :value="c.name">{{ c.course_name }}</option>
            </select>
          </div>
        </div>
        <div class="flex gap-2 mt-5 border-t border-divider pt-3 text-xs">
          <button @click="quickTestModal.show = false" class="flex-1 py-2 font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="saveQuickTest" :disabled="quickTestModal.saving" class="flex-1 py-2 font-bold text-white bg-brand rounded-lg hover:bg-brand-deep">
            {{ quickTestModal.saving ? 'Đang lưu...' : '✓ Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Interactive Transition Modal -->
    <div v-if="transitionModal.show" @click.self="transitionModal.show = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6 overflow-y-auto max-h-[90vh] cursor-default">
        <div class="flex items-center justify-between mb-4 border-b border-divider pb-3">
          <h3 class="text-sm font-bold text-ink-2 uppercase tracking-wider text-brand">
            Chuyển trạng thái: {{ getStatusLabel(transitionModal.lead.status) }} → {{ getStatusLabel(transitionModal.targetStatus) }}
          </h3>
          <button @click="transitionModal.show = false" class="text-faint hover:text-muted">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4 text-xs">
          <!-- Step 1: New -> Consulting (Requires Log & Prompts AI Suggestions) -->
          <div v-if="transitionModal.targetStatus === 'Consulting'" class="space-y-3">
            <div class="bg-brand-soft/40 border border-brand/20 p-3 rounded-xl">
              <span class="block text-xs font-bold text-brand uppercase mb-1.5 tracking-wider">💡 Gợi ý kịch bản tư vấn (AI Generated)</span>
              <div v-if="transitionModal.aiLoading" class="flex items-center gap-2 py-3 text-faint">
                <span class="w-3.5 h-3.5 border-2 border-brand border-t-transparent rounded-full animate-spin"></span>
                <span>AI đang phân tích & soạn kịch bản tư vấn riêng...</span>
              </div>
              <p v-else class="text-ink-2 leading-relaxed whitespace-pre-wrap select-text font-mono bg-white/60 p-2.5 rounded-lg border border-brand/10">{{ transitionModal.aiSuggestion }}</p>
            </div>

            <div>
              <label class="block text-muted font-bold mb-1">Ngày liên hệ tư vấn *</label>
              <input type="date" v-model="transitionModal.form.contact_date" class="w-full px-3 py-2 border border-border rounded-lg" />
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Nội dung cuộc trao đổi *</label>
              <textarea v-model="transitionModal.form.notes" rows="3" placeholder="Ghi chép nhanh ý kiến, mục tiêu của học viên..." class="w-full px-3 py-2 border border-border rounded-lg"></textarea>
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Hẹn gọi lại sau (Không bắt buộc)</label>
              <input type="date" v-model="transitionModal.form.next_follow_up" class="w-full px-3 py-2 border border-border rounded-lg" />
            </div>
          </div>

          <!-- Step 2: -> Testing (Requires Placement Test) -->
          <div v-else-if="transitionModal.targetStatus === 'Testing'" class="space-y-3">
            <div class="bg-blue-50 border border-blue-200 text-blue-800 p-2.5 rounded-lg">
              Yêu cầu ghi nhận điểm số bài thi test đầu vào của học viên tiềm năng để phục vụ phân lớp.
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Ngày thi test *</label>
              <input type="date" v-model="transitionModal.form.test_date" class="w-full px-3 py-2 border border-border rounded-lg" />
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Điểm thi test *</label>
              <input type="number" step="0.5" v-model="transitionModal.form.score" placeholder="VD: 6.5" class="w-full px-3 py-2 border border-border rounded-lg" />
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Khóa học đề xuất sau test</label>
              <select v-model="transitionModal.form.recommended_course" class="w-full px-3 py-2 border border-border rounded-lg bg-white">
                <option value="">Chọn khóa học đề xuất...</option>
                <option v-for="c in courses.data" :key="c.name" :value="c.name">{{ c.course_name }}</option>
              </select>
            </div>
          </div>

          <!-- Step 3: -> Trial (Trial Details) -->
          <div v-else-if="transitionModal.targetStatus === 'Trial'" class="space-y-3">
            <div>
              <label class="block text-muted font-bold mb-1">Ngày thi / Bắt đầu học thử *</label>
              <input type="date" v-model="transitionModal.form.contact_date" class="w-full px-3 py-2 border border-border rounded-lg" />
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Ghi chú lớp học thử, ca học xếp lớp</label>
              <textarea v-model="transitionModal.form.notes" rows="3" placeholder="Ví dụ: Đăng ký học thử 3 buổi lớp IELTS Starter ca T2-T4..." class="w-full px-3 py-2 border border-border rounded-lg"></textarea>
            </div>
          </div>

          <!-- Step 4: -> Enrolled -->
          <div v-else-if="transitionModal.targetStatus === 'Enrolled'" class="space-y-2">
            <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl">
              <p class="font-bold mb-1">Xác nhận Đăng ký Nhập học!</p>
              <p>Hệ thống sẽ tự động chuyển đổi thông tin của <strong>{{ transitionModal.lead.lead_name }}</strong> thành Học viên chính thức, đồng thời tự động tạo thông tin Người giám hộ (nếu được khai báo).</p>
            </div>
          </div>

          <!-- Step 5: -> Lost (Requires Lost Reason) -->
          <div v-else-if="transitionModal.targetStatus === 'Lost'" class="space-y-3">
            <div class="bg-red-50 border border-red-200 text-red-800 p-2.5 rounded-lg">
              Vui lòng nhập lý do cụ thể khách hàng không nhập học thành công.
            </div>
            <div>
              <label class="block text-muted font-bold mb-1">Lý do thất bại *</label>
              <textarea v-model="transitionModal.form.lost_reason" rows="4" placeholder="VD: Giá học phí cao, Không sắp xếp được ca học, Đã tìm trung tâm khác..." class="w-full px-3 py-2 border border-border rounded-lg"></textarea>
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-6 border-t border-divider pt-4 text-xs">
          <button @click="transitionModal.show = false" class="flex-1 py-2 font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="submitTransition" :disabled="transitionModal.saving" class="flex-1 py-2 font-bold text-white bg-brand rounded-lg hover:bg-brand-deep">
            {{ transitionModal.saving ? 'Đang cập nhật...' : '✓ Xác nhận' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" @click.self="showAddModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6 overflow-y-auto max-h-[90vh] cursor-default">
        <div class="flex items-center justify-between mb-5 border-b border-divider pb-3">
          <h2 class="text-lg font-bold text-ink-2">Thêm khách hàng mới</h2>
          <button @click="showAddModal = false" class="text-faint hover:text-muted">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <!-- AI Autofill Section -->
          <div class="bg-brand-soft/40 border border-brand/20 p-3 rounded-xl space-y-2">
            <label class="block text-xs font-bold text-brand uppercase tracking-wider">Trợ lý AI Điền Form Tự động</label>
            <textarea v-model="aiRawText" placeholder="Dán tin nhắn thô ở đây. Ví dụ: Nguyễn Văn A, sđt 0987654321, sinh năm 2005, phụ huynh là Nguyễn Văn B sđt 0912345678..."
              class="w-full h-16 p-2 text-xs border border-border rounded-lg focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand bg-white" rows="2"></textarea>
            <button @click="autoFillWithAI" :disabled="parsingAI"
              class="w-full py-1.5 bg-brand text-white text-xs font-medium rounded-lg hover:bg-brand-deep transition-all flex items-center justify-center gap-1.5">
              <span v-if="parsingAI" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span v-else>🪄</span>
              AI Tự động điền Form
            </button>
          </div>

          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Họ và tên *</label>
            <input v-model="newLead.lead_name" placeholder="Nhập họ và tên..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Số điện thoại</label>
              <input v-model="newLead.phone" placeholder="0901234567"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Email</label>
              <input v-model="newLead.email" type="email" placeholder="email@..."
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngày sinh</label>
              <input v-model="newLead.date_of_birth" type="date"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Giới tính</label>
              <select v-model="newLead.gender"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
                <option value="">Chọn giới tính...</option>
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
                <option value="Khác">Khác</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngành nghề</label>
              <input v-model="newLead.occupation" placeholder="Học sinh, Sinh viên..."
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Nguồn</label>
              <select v-model="newLead.source"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white">
                <option value="Website">Website</option>
                <option value="Facebook">Facebook</option>
                <option value="Hotline">Hotline</option>
                <option value="Word of Mouth">Truyền miệng</option>
                <option value="Other">Khác</option>
              </select>
            </div>
          </div>
          
          <!-- Guardian Details -->
          <div class="border-t border-dashed border-divider pt-4 space-y-3">
            <span class="text-xs font-bold text-ink-2 block uppercase tracking-wider">Thông tin người giám hộ (Nếu có)</span>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Họ tên phụ huynh</label>
                <input v-model="newLead.guardian_name" placeholder="Tên phụ huynh..."
                  class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">SĐT phụ huynh</label>
                <input v-model="newLead.guardian_phone" placeholder="Số điện thoại..."
                  class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
              </div>
            </div>
          </div>

          <!-- File Upload Attachment Field -->
          <div class="border-t border-dashed border-divider pt-4">
            <label class="block text-xs font-bold text-ink-2 mb-1.5 uppercase tracking-wider">Tài liệu đính kèm (Ảnh, CV, học bạ...)</label>
            <input type="file" @change="handleFileChange" class="w-full text-xs text-muted file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-soft file:text-brand hover:file:bg-brand hover:file:text-white file:cursor-pointer cursor-pointer border border-border rounded-lg p-1.5 bg-white" />
            <p v-if="selectedFile" class="text-[10px] text-emerald-600 mt-1">✓ Đã chọn: {{ selectedFile.name }} ({{ (selectedFile.size / 1024).toFixed(1) }} KB)</p>
          </div>
        </div>
        <div class="flex gap-3 mt-6 border-t border-divider pt-4">
          <button @click="showAddModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveLead" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : '✓ Lưu' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { apiResource, db, call } from '../api'

const search = ref('')
const filterStatus = ref('')
const periodFilter = ref('')
const showAddModal = ref(false)
const saving = ref(false)
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

const aiRawText = ref('')
const parsingAI = ref(false)
const selectedFile = ref(null)

const initLead = () => ({
  lead_name: '',
  phone: '',
  email: '',
  source: 'Facebook',
  date_of_birth: '',
  gender: '',
  occupation: '',
  guardian_name: '',
  guardian_phone: ''
})

const newLead = ref(initLead())

const leads = apiResource('get_leads', { auto: true })
const courses = apiResource('get_courses', { auto: true })

const countStatus = (status) => leads.data?.filter(l => l.status === status).length || 0

const filteredLeads = computed(() => {
  const start = getDateRange(periodFilter.value)
  return (leads.data || []).filter(l => {
    const matchSearch = !search.value || l.lead_name?.toLowerCase().includes(search.value.toLowerCase()) || l.phone?.includes(search.value)
    const matchStatus = !filterStatus.value || l.status === filterStatus.value
    const periodMatch = !start || !l.creation || new Date(l.creation) >= start
    return matchSearch && matchStatus && periodMatch
  })
})

const allSelected = computed(() =>
  filteredLeads.value.length > 0 && filteredLeads.value.every(l => selected.value.includes(l.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredLeads.value.map(l => l.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Student Lead', name)
    }
    selected.value = []; showDeleteConfirm.value = false; leads.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

const pipelineSteps = [
  { id: 'New', label: 'Mới' },
  { id: 'Consulting', label: 'Đang tư vấn' },
  { id: 'Testing', label: 'Test đầu vào' },
  { id: 'Trial', label: 'Học thử' },
  { id: 'Enrolled', label: 'Đã nhập học' }
]

const getStatusLabel = (status) => {
  const map = {
    'New': 'Mới',
    'Consulting': 'Đang tư vấn',
    'Testing': 'Test đầu vào',
    'Trial': 'Học thử',
    'Enrolled': 'Đã nhập học',
    'Lost': 'Không thành công'
  }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = {
    'New': 'bg-blue-100 text-blue-700',
    'Consulting': 'bg-indigo-100 text-indigo-700',
    'Testing': 'bg-purple-100 text-purple-700',
    'Trial': 'bg-amber-100 text-amber-700',
    'Enrolled': 'bg-emerald-100 text-emerald-700',
    'Lost': 'bg-red-100 text-red-700'
  }
  return map[status] || 'bg-slate-100 text-slate-700'
}

// Collapsible Row Expansion and Fetch logs/tests
const detailModal = reactive({
  show: false,
  lead: null
})

const details = reactive({})

const openDetailModal = (lead) => {
  detailModal.lead = lead
  detailModal.show = true
  fetchLeadDetails(lead.name)
}

const fetchLeadDetails = async (leadName) => {
  try {
    const [logsRes, testsRes, filesRes] = await Promise.all([
      call('get_consultation_logs', { lead_id: leadName }),
      call('get_placement_tests', { lead_id: leadName }),
      db.getList('File', {
        filters: { attached_to_doctype: 'Student Lead', attached_to_name: leadName },
        fields: ['name', 'file_name', 'file_url']
      })
    ])
    details[leadName] = {
      logs: logsRes || [],
      tests: testsRes || [],
      files: filesRes || []
    }
  } catch (err) {
    console.error(err)
  }
}

// File Selection Handler
const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length) {
    selectedFile.value = files[0]
  } else {
    selectedFile.value = null
  }
}

// Upload File helper API
const uploadAttachedFile = async (doctype, docname, file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('doctype', doctype)
  formData.append('docname', docname)
  formData.append('is_private', 1)
  
  const response = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: formData
  })
  if (!response.ok) {
    throw new Error('Lỗi tải file đính kèm lên hệ thống')
  }
  return await response.json()
}

// Quick Add Log & Test modals
const quickLogModal = reactive({
  show: false,
  lead: null,
  saving: false,
  form: { contact_date: new Date().toISOString().split('T')[0], notes: '', next_follow_up: '' }
})

const openQuickAddLog = (lead) => {
  quickLogModal.lead = lead
  quickLogModal.form = { contact_date: new Date().toISOString().split('T')[0], notes: '', next_follow_up: '' }
  quickLogModal.show = true
}

const saveQuickLog = async () => {
  if (!quickLogModal.form.notes) return alert('Nhập nội dung')
  quickLogModal.saving = true
  try {
    await call('add_consultation_log', {
      lead_id: quickLogModal.lead.name,
      notes: quickLogModal.form.notes,
      contact_date: quickLogModal.form.contact_date,
      next_follow_up: quickLogModal.form.next_follow_up || null
    })
    quickLogModal.show = false
    fetchLeadDetails(quickLogModal.lead.name)
  } catch (err) {
    alert('Lỗi: ' + err.message)
  } finally {
    quickLogModal.saving = false
  }
}

const quickTestModal = reactive({
  show: false,
  lead: null,
  saving: false,
  form: { test_date: new Date().toISOString().split('T')[0], score: 0, recommended_course: '' }
})

const openQuickAddTest = (lead) => {
  quickTestModal.lead = lead
  quickTestModal.form = { test_date: new Date().toISOString().split('T')[0], score: 0, recommended_course: '' }
  quickTestModal.show = true
}

const saveQuickTest = async () => {
  if (!quickTestModal.form.test_date || quickTestModal.form.score === null) return alert('Nhập đầy đủ thông tin bắt buộc')
  quickTestModal.saving = true
  try {
    await call('add_placement_test', {
      lead_id: quickTestModal.lead.name,
      test_date: quickTestModal.form.test_date,
      score: quickTestModal.form.score,
      recommended_course: quickTestModal.form.recommended_course || null
    })
    quickTestModal.show = false
    fetchLeadDetails(quickTestModal.lead.name)
  } catch (err) {
    alert('Lỗi: ' + err.message)
  } finally {
    quickTestModal.saving = false
  }
}

// Pipeline Bar Styling
const getPipelineStepClass = (currentStatus, stepId) => {
  const stepsOrder = ['New', 'Consulting', 'Testing', 'Trial', 'Enrolled']
  const currentIdx = stepsOrder.indexOf(currentStatus)
  const stepIdx = stepsOrder.indexOf(stepId)

  if (currentStatus === stepId) {
    return 'bg-brand text-white border-brand shadow-sm shadow-red-500/20'
  }
  if (stepIdx < currentIdx && currentStatus !== 'Lost') {
    return 'bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100'
  }
  return 'bg-white border-border text-muted hover:bg-slate-100'
}

// Transition Modals Management
const transitionModal = reactive({
  show: false,
  lead: null,
  targetStatus: '',
  aiLoading: false,
  aiSuggestion: '',
  saving: false,
  form: {
    contact_date: new Date().toISOString().split('T')[0],
    notes: '',
    next_follow_up: '',
    test_date: new Date().toISOString().split('T')[0],
    score: 0,
    recommended_course: '',
    lost_reason: ''
  }
})

const triggerStatusTransition = async (lead, targetStatus) => {
  transitionModal.lead = lead
  transitionModal.targetStatus = targetStatus
  transitionModal.show = true
  transitionModal.aiSuggestion = ''
  transitionModal.form = {
    contact_date: new Date().toISOString().split('T')[0],
    notes: '',
    next_follow_up: '',
    test_date: new Date().toISOString().split('T')[0],
    score: 0,
    recommended_course: '',
    lost_reason: ''
  }

  if (targetStatus === 'Consulting') {
    transitionModal.aiLoading = true
    try {
      const prompt = `Hãy soạn kịch bản tư vấn hoặc 3 câu gợi ý tiếp cận ngắn gọn, chuyên nghiệp nhất cho học viên tiềm năng sau:
Tên: ${lead.lead_name}
Độ tuổi: ${lead.date_of_birth || 'Không rõ'}
Ngành nghề: ${lead.occupation || 'Không rõ'}
Nguồn đăng ký: ${lead.source}

Tập trung vào gợi ý câu thoại mở đầu và ưu đãi khóa học đề xuất.`

      transitionModal.aiSuggestion = await call('ai_chat', {
        messages: JSON.stringify([{ role: 'user', content: prompt }]),
        temperature: 0.7
      })
    } catch (e) {
      transitionModal.aiSuggestion = 'Không thể tải kịch bản AI: ' + e.message
    } finally {
      transitionModal.aiLoading = false
    }
  }
}

const submitTransition = async () => {
  const { lead, targetStatus, form } = transitionModal
  transitionModal.saving = true

  try {
    // 1. Save data specific to the state
    if (targetStatus === 'Consulting') {
      if (!form.notes) return alert('Nội dung tư vấn là bắt buộc')
      await call('add_consultation_log', {
        lead_id: lead.name,
        notes: form.notes,
        contact_date: form.contact_date,
        next_follow_up: form.next_follow_up || null
      })
      if (form.next_follow_up) {
        await db.insert({
          doctype: 'Student Appointment',
          lead: lead.name,
          appointment_date: form.next_follow_up,
          appointment_time: '09:00',
          purpose: 'Tư vấn / Gọi lại',
          status: 'Scheduled'
        })
      }
    } else if (targetStatus === 'Testing') {
      if (!form.test_date || form.score === null) return alert('Ngày thi và điểm số là bắt buộc')
      await call('add_placement_test', {
        lead_id: lead.name,
        test_date: form.test_date,
        score: form.score,
        recommended_course: form.recommended_course || null
      })
    } else if (targetStatus === 'Trial') {
      await call('add_consultation_log', {
        lead_id: lead.name,
        notes: `[Bắt đầu học thử] ` + (form.notes || 'Không có ghi chú'),
        contact_date: form.contact_date
      })
    } else if (targetStatus === 'Lost') {
      if (!form.lost_reason) return alert('Vui lòng nhập lý do thất bại')
      await db.setValue('Student Lead', lead.name, 'lost_reason', form.lost_reason)
    } else if (targetStatus === 'Enrolled') {
      // Call convert to student API
      const convRes = await call('convert_lead_to_student', { lead_id: lead.name })
      alert(`Chuyển đổi thành công! Mã học viên: ${convRes.student_id}`)
    }

    // 2. Set the status value if it wasn't 'Enrolled' (since convert API already sets status to Enrolled)
    if (targetStatus !== 'Enrolled') {
      await db.setValue('Student Lead', lead.name, 'status', targetStatus)
      // Local sync
      detailModal.lead.status = targetStatus
    } else {
      detailModal.lead.status = 'Enrolled'
    }

    transitionModal.show = false
    leads.fetch()
    fetchLeadDetails(lead.name)
  } catch (err) {
    alert('Lỗi chuyển trạng thái: ' + err.message)
  } finally {
    transitionModal.saving = false
  }
}

const saveLead = async () => {
  if (!newLead.value.lead_name) return
  saving.value = true
  try {
    const res = await db.insert({ doctype: 'Student Lead', status: 'New', ...newLead.value })
    
    if (selectedFile.value) {
      await uploadAttachedFile('Student Lead', res.name, selectedFile.value)
    }

    showAddModal.value = false
    leads.fetch()
    newLead.value = initLead()
    selectedFile.value = null
  } catch (err) {
    alert('Lỗi: ' + (err.message || 'Không thể lưu khách hàng'))
  } finally {
    saving.value = false
  }
}

const autoFillWithAI = async () => {
  if (!aiRawText.value.trim()) return alert('Vui lòng nhập thông tin thô')
  parsingAI.value = true
  try {
    const prompt = `Bạn là trợ lý AI phân tích thông tin học viên tiềm năng từ tin nhắn thô.
Hãy phân tích đoạn tin nhắn sau và trả về DUY NHẤT một chuỗi JSON hợp lệ chứa các trường sau (nếu không có thông tin, hãy để giá trị trống hoặc null):
{
  "lead_name": "Tên học viên",
  "phone": "Số điện thoại học viên",
  "email": "Email học viên",
  "date_of_birth": "Ngày sinh (định dạng YYYY-MM-DD)",
  "gender": "Giới tính (chỉ nhận: 'Nam', 'Nữ', 'Khác')",
  "occupation": "Ngành nghề (VD: Học sinh, Sinh viên, Đi làm...)",
  "guardian_name": "Họ và tên phụ huynh / người giám hộ",
  "guardian_phone": "Số điện thoại phụ huynh / người giám hộ"
}

Tin nhắn thô: "${aiRawText.value}"`

    const content = await call('ai_chat', {
      messages: JSON.stringify([{ role: 'user', content: prompt }]),
      temperature: 0.1,
      response_format: JSON.stringify({ type: 'json_object' })
    })
    const result = JSON.parse(content)
    
    // Fill fields
    if (result.lead_name) newLead.value.lead_name = result.lead_name
    if (result.phone) newLead.value.phone = result.phone
    if (result.email) newLead.value.email = result.email
    if (result.date_of_birth) newLead.value.date_of_birth = result.date_of_birth
    if (result.gender) newLead.value.gender = result.gender
    if (result.occupation) newLead.value.occupation = result.occupation
    if (result.guardian_name) newLead.value.guardian_name = result.guardian_name
    if (result.guardian_phone) newLead.value.guardian_phone = result.guardian_phone
    
    aiRawText.value = ''
  } catch (err) {
    alert('Lỗi phân tích AI: ' + err.message)
  } finally {
    parsingAI.value = false
  }
}
</script>
