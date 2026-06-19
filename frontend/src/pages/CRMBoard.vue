<template>
  <div class="space-y-6 h-[calc(100vh-140px)] flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-bold text-ink-2">CRM Pipeline</h3>
        <p class="text-xs text-muted mt-1 font-medium">Kéo thả Khách hàng tiềm năng (Leads) & Học thử giữa các trạng thái để theo dõi phễu tuyển sinh.</p>
      </div>
      <button @click="showCreateModal = true" class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo Lead Mới
      </button>
    </div>

    <!-- Search Toolbar -->
    <div class="relative bg-white p-3 rounded-xl border border-border shadow-sm flex items-center flex-shrink-0">
      <span class="absolute left-6 text-faint">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </span>
      <input v-model="searchQuery" placeholder="Lọc nhanh lead theo tên, mã lead, số điện thoại hoặc email..."
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
            {{ getLeads(col.id).length }}
          </span>
        </h4>
        
        <div class="flex-1 overflow-y-auto space-y-2 pr-0.5 min-h-[200px]">
          <div v-for="lead in getLeads(col.id)" :key="lead.name" 
            draggable="true"
            @dragstart="onDragStart($event, lead)"
            @click="openDetailModal(lead)"
            class="bg-white p-2.5 rounded-lg shadow-sm border border-border/70 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer active:cursor-grabbing border-l-4"
            :class="getLeadBorder(lead.status)"
          >
            <div class="space-y-1.5 mb-2">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <div class="h-5 w-5 rounded-full bg-slate-50 text-slate-600 border border-slate-200 flex items-center justify-center text-[9px] font-bold flex-shrink-0 uppercase">
                    {{ lead.lead_name ? lead.lead_name.charAt(0) : 'L' }}
                  </div>
                  <a :href="`/app/student-lead/${lead.name}`" target="_blank" class="text-[9px] text-brand hover:bg-brand-tint font-semibold font-mono bg-brand-soft px-1.5 py-0.5 rounded border border-brand-soft flex-shrink-0 transition-colors" @click.stop>{{ lead.name }}</a>
                </div>
              </div>
              <span class="font-bold text-ink-2 text-xs leading-snug break-words block">{{ lead.lead_name }}</span>
            </div>
            
            <div class="text-[11px] text-muted mb-2 space-y-1 bg-slate-50/50 rounded-lg p-1.5 border border-slate-100/80">
              <p v-if="lead.phone" class="flex items-center text-ink-2 font-medium">
                <svg class="w-3 h-3 mr-1 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                {{ lead.phone }}
              </p>
              <p v-if="lead.email" class="flex items-center text-slate-600 break-all">
                <svg class="w-3 h-3 mr-1 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {{ lead.email }}
              </p>
              <div class="flex flex-wrap gap-1 pt-1 border-t border-slate-100 mt-1">
                <span class="inline-flex items-center text-[9px] text-slate-500 bg-white border border-slate-200 px-1 py-0.5 rounded font-medium">
                  {{ lead.source || 'Không rõ' }}
                </span>
                <span v-if="lead.occupation" class="inline-flex items-center text-[9px] text-slate-500 bg-white border border-slate-200 px-1 py-0.5 rounded font-medium break-words">
                  {{ lead.occupation }}
                </span>
              </div>
            </div>
            
            <div class="pt-1.5 border-t border-divider flex items-center justify-between">
              <span class="text-[9px] text-slate-400 font-medium">Kéo thả để chuyển</span>
              <select 
                class="text-[9px] bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-brand/20 text-muted font-medium transition-colors cursor-pointer"
                @change="updateStatus(lead, $event.target.value)"
                @click.stop
              >
                <option v-for="c in columns" :key="c.id" :value="c.id" :selected="c.id === lead.status">
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
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6 overflow-y-auto max-h-[90vh] cursor-default">
        <div class="flex items-center justify-between mb-5 border-b border-divider pb-3">
          <h2 class="text-lg font-bold text-ink-2">Thêm Khách Hàng Tiềm Năng</h2>
          <button @click="showCreateModal = false" class="text-faint hover:text-muted transition-colors">
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

          <FormControl label="Họ và tên *" v-model="newLead.lead_name" :required="true" placeholder="Nhập tên khách hàng..." />
          <div class="grid grid-cols-2 gap-3">
            <FormControl label="Số điện thoại" v-model="newLead.phone" placeholder="VD: 090..." />
            <FormControl label="Email" v-model="newLead.email" type="email" placeholder="VD: email@..." />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <FormControl label="Ngày sinh" v-model="newLead.date_of_birth" type="date" />
            <FormControl type="select" label="Giới tính" v-model="newLead.gender" :options="['', 'Nam', 'Nữ', 'Khác']" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <FormControl label="Ngành nghề" v-model="newLead.occupation" placeholder="VD: Học sinh..." />
            <FormControl type="select" label="Nguồn thông tin" v-model="newLead.source" :options="['Website', 'Facebook', 'Hotline', 'Word of Mouth', 'Other']" />
          </div>

          <!-- Guardian Details -->
          <div class="border-t border-dashed border-divider pt-4 space-y-3">
            <span class="text-xs font-bold text-ink-2 block uppercase tracking-wider">Thông tin người giám hộ (Nếu có)</span>
            <div class="grid grid-cols-2 gap-3">
              <FormControl label="Họ tên phụ huynh" v-model="newLead.guardian_name" placeholder="Họ và tên..." />
              <FormControl label="SĐT phụ huynh" v-model="newLead.guardian_phone" placeholder="Số điện thoại..." />
            </div>
          </div>

          <!-- File Upload Attachment Field -->
          <div class="border-t border-dashed border-divider pt-4">
            <label class="block text-xs font-bold text-ink-2 mb-1.5 uppercase tracking-wider">Tài liệu đính kèm (Ảnh, CV, học bạ...)</label>
            <input type="file" @change="handleFileChange" class="w-full text-xs text-muted file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-soft file:text-brand hover:file:bg-brand hover:file:text-white file:cursor-pointer cursor-pointer border border-border rounded-lg p-1.5 bg-white" />
            <p v-if="selectedFile" class="text-[10px] text-emerald-600 mt-1">✓ Đã chọn: {{ selectedFile.name }} ({{ (selectedFile.size / 1024).toFixed(1) }} KB)</p>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6 border-t border-divider pt-4">
          <button @click="showCreateModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">Hủy</button>
          <button @click="saveLead" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">{{ saving ? 'Đang lưu...' : 'Lưu khách hàng' }}</button>
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

                <span class="font-semibold">Trạng thái hiện tại:</span>
                <span class="col-span-2 text-ink-2 font-bold">{{ getStatusLabel(detailModal.lead.status) }}</span>

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
                <p class="text-ink-2 leading-relaxed" v-html="log.notes"></p>
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
            {{ quickTestModal.saving ? 'Đang lưu...' : '✓ Ghi điểm' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { FormControl } from 'frappe-ui'
import { apiResource, listResource, db, call } from '../api'

const columns = [
  { id: 'New', label: 'Mới' },
  { id: 'Consulting', label: 'Đang tư vấn' },
  { id: 'Testing', label: 'Test đầu vào' },
  { id: 'Trial', label: 'Học thử' },
  { id: 'Enrolled', label: 'Đã nhập học' },
  { id: 'Lost', label: 'Không thành công' }
]

const showCreateModal = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const selectedFile = ref(null)

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length) {
    selectedFile.value = files[0]
  } else {
    selectedFile.value = null
  }
}

const uploadAttachedFile = async (doctype, docname, file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('doctype', doctype)
  formData.append('docname', docname)
  formData.append('is_private', 0)
  
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

const aiRawText = ref('')
const parsingAI = ref(false)

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

const draggedLead = ref(null)
const activeDropCol = ref('')

const leads = listResource('Student Lead', {
  fields: ['name', 'lead_name', 'phone', 'email', 'source', 'status', 'date_of_birth', 'gender', 'occupation', 'guardian_name', 'guardian_phone'],
  limit_page_length: 500,
  auto: true
})

const getLeads = (status) => {
  if (!leads.data) return []
  return leads.data.filter(l => l.status === status && 
    (!searchQuery.value || 
     l.lead_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
     l.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
     (l.phone && l.phone.includes(searchQuery.value)) ||
     (l.email && l.email.toLowerCase().includes(searchQuery.value.toLowerCase())))
  )
}

const getColumnStyles = (colId) => {
  const styles = {
    'New': {
      bg: 'bg-blue-50/20 border-blue-100/60',
      bgDragover: 'bg-blue-50/60 border-blue-400 ring-4 ring-blue-500/10',
      badge: 'bg-blue-100 text-blue-700',
      dot: 'bg-blue-500'
    },
    'Consulting': {
      bg: 'bg-indigo-50/20 border-indigo-100/60',
      bgDragover: 'bg-indigo-50/60 border-indigo-400 ring-4 ring-indigo-500/10',
      badge: 'bg-indigo-100 text-indigo-700',
      dot: 'bg-indigo-500'
    },
    'Testing': {
      bg: 'bg-purple-50/20 border-purple-100/60',
      bgDragover: 'bg-purple-50/60 border-purple-400 ring-4 ring-purple-500/10',
      badge: 'bg-purple-100 text-purple-700',
      dot: 'bg-purple-500'
    },
    'Trial': {
      bg: 'bg-amber-50/20 border-amber-100/60',
      bgDragover: 'bg-amber-50/60 border-amber-400 ring-4 ring-amber-500/10',
      badge: 'bg-amber-100 text-amber-700',
      dot: 'bg-amber-500'
    },
    'Enrolled': {
      bg: 'bg-emerald-50/20 border-emerald-100/60',
      bgDragover: 'bg-emerald-50/60 border-emerald-400 ring-4 ring-emerald-500/10',
      badge: 'bg-emerald-100 text-emerald-700',
      dot: 'bg-emerald-500'
    },
    'Lost': {
      bg: 'bg-slate-50/20 border-slate-200/60',
      bgDragover: 'bg-slate-100/60 border-slate-400 ring-4 ring-slate-500/10',
      badge: 'bg-slate-200 text-slate-700',
      dot: 'bg-slate-400'
    }
  }
  return styles[colId] || {
    bg: 'bg-slate-50/20 border-slate-200/60',
    bgDragover: 'bg-slate-100/60 border-slate-400 ring-4 ring-slate-500/10',
    badge: 'bg-slate-200 text-slate-700',
    dot: 'bg-slate-400'
  }
}

const getLeadBorder = (status) => {
  if (status === 'New') return 'border-l-blue-500'
  if (status === 'Consulting') return 'border-l-indigo-500'
  if (status === 'Testing') return 'border-l-purple-500'
  if (status === 'Trial') return 'border-l-amber-500'
  if (status === 'Enrolled') return 'border-l-emerald-500'
  return 'border-l-slate-400'
}

// Drag & Drop Handlers
const onDragStart = (event, lead) => {
  draggedLead.value = lead
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
  if (!draggedLead.value) return
  const lead = draggedLead.value
  draggedLead.value = null

  if (lead.status === newStatus) return
  await handleStatusChange(lead, newStatus)
}

const updateStatus = async (lead, newStatus) => {
  if (lead.status === newStatus) return
  await handleStatusChange(lead, newStatus)
}

const courses = apiResource('get_courses', { auto: true })

const pipelineSteps = [
  { id: 'New', label: 'Mới' },
  { id: 'Consulting', label: 'Đang tư vấn' },
  { id: 'Testing', label: 'Test đầu vào' },
  { id: 'Trial', label: 'Học thử' },
  { id: 'Enrolled', label: 'Đã nhập học' }
]

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

const quickLogModal = reactive({
  show: false,
  lead: null,
  saving: false,
  form: { contact_date: '', notes: '', next_follow_up: '' }
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
  form: { test_date: '', score: 0, recommended_course: '' }
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

const transitionModal = reactive({
  show: false,
  lead: null,
  targetStatus: '',
  aiLoading: false,
  aiSuggestion: '',
  saving: false,
  form: {
    contact_date: '',
    notes: '',
    next_follow_up: '',
    test_date: '',
    score: 0,
    recommended_course: '',
    lost_reason: ''
  }
})

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
      if (detailModal.lead && detailModal.lead.name === lead.name) {
        detailModal.lead.status = targetStatus
      }
    } else {
      if (detailModal.lead && detailModal.lead.name === lead.name) {
        detailModal.lead.status = 'Enrolled'
      }
    }

    transitionModal.show = false
    leads.fetch()
    if (detailModal.show && detailModal.lead && detailModal.lead.name === lead.name) {
      fetchLeadDetails(lead.name)
    }
  } catch (err) {
    alert('Lỗi chuyển trạng thái: ' + err.message)
  } finally {
    transitionModal.saving = false
  }
}

const handleStatusChange = async (lead, newStatus) => {
  await triggerStatusTransition(lead, newStatus)
}

const saveLead = async () => {
  if (!newLead.value.lead_name) return alert('Nhập tên')
  saving.value = true
  try {
    const res = await db.insert({
      doctype: 'Student Lead',
      status: 'New',
      ...newLead.value
    })

    if (selectedFile.value) {
      await uploadAttachedFile('Student Lead', res.name, selectedFile.value)
    }

    showCreateModal.value = false
    leads.fetch()
    newLead.value = initLead()
    selectedFile.value = null
  } catch (err) {
    console.error(err)
    alert('Lỗi: ' + (err.messages ? err.messages[0] : (err.message || JSON.stringify(err))))
  } finally {
    saving.value = false
  }
}
</script>
