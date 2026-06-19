<template>
  <div class="relative h-full flex flex-col space-y-4 overflow-hidden">
    <!-- Header Toolbar -->
    <div class="flex items-center justify-between flex-shrink-0">
      <div>
        <h3 class="ff-display text-xl font-bold text-ink">Danh sách Học Viên</h3>
        <p class="text-xs text-muted mt-1 font-medium">Quản lý hồ sơ học viên, thông tin liên hệ và trạng thái học tập.</p>
      </div>
      <button @click="openCreateModal" class="btn btn-brand">Thêm Học Viên</button>
    </div>

    <!-- Search & Filters -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-white p-4 rounded-xl border border-border shadow-sm flex-shrink-0 flex-wrap">
      <div class="relative flex-1">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-faint">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm theo tên, mã học viên..."
          class="w-full pl-10 pr-4 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
        />
      </div>

      <!-- Filters -->
      <select v-model="filterGender" class="text-sm border border-border rounded-lg px-3 py-2 bg-white text-muted focus:outline-none focus:ring-2 focus:ring-brand/30">
        <option value="">Tất cả giới tính</option>
        <option value="Nam">Nam</option>
        <option value="Nữ">Nữ</option>
        <option value="Khác">Khác</option>
      </select>

      <select v-model="filterClass" class="text-sm border border-border rounded-lg px-3 py-2 bg-white text-muted focus:outline-none focus:ring-2 focus:ring-brand/30 w-48">
        <option value="">Tất cả lớp học</option>
        <option v-for="c in classesList.data" :key="c.name" :value="c.name">{{ c.class_name }}</option>
      </select>

      <div class="flex items-center gap-1 bg-hover/40 border border-border rounded-lg p-1">
        <button v-for="p in periods" :key="p.value" @click="periodFilter = p.value"
          class="px-3 py-1 text-xs font-medium rounded-md transition-all border border-transparent"
          :class="periodFilter === p.value ? 'bg-white text-ink-2 shadow-sm border-border' : 'text-muted hover:bg-white'">
          {{ p.label }}
        </button>
      </div>

      <!-- Bulk delete bar -->
      <transition name="fade">
        <div v-if="selected.length > 0" class="flex items-center gap-2 px-3 py-1.5 bg-red-50 border border-red-200 rounded-lg">
          <span class="text-xs text-red-700 font-medium">Đã chọn {{ selected.length }}</span>
          <button @click="showDeleteConfirm = true" class="flex items-center gap-1 px-2.5 py-1 bg-red-600 text-white text-xs font-semibold rounded-md hover:bg-red-700">
            Xóa
          </button>
          <button @click="selected = []" class="text-xs text-red-500 hover:text-red-700">Bỏ chọn</button>
        </div>
      </transition>

      <span class="text-xs text-muted font-medium bg-hover/80 px-3 py-1.5 rounded-lg border border-border">
        Tổng số: <strong class="text-ink font-semibold">{{ filteredStudents.length }}</strong>
      </span>
    </div>

    <!-- Main Table View -->
    <div class="flex-1 overflow-y-auto bg-white border border-border rounded-xl shadow-sm">
      <div v-if="students.loading" class="flex justify-center py-12">
        <LoadingIndicator />
      </div>
      <div v-else-if="filteredStudents.length === 0" class="flex flex-col items-center justify-center py-20 text-faint">
        <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p class="text-sm font-medium">Không tìm thấy học viên nào</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-hover/40 border-b border-border sticky top-0 z-10">
            <tr>
              <th class="px-4 py-3 w-10">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </th>
              <th class="px-3 py-3 text-left text-xs font-semibold text-muted uppercase tracking-wider w-12">STT</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Họ tên / Mã HV</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Thông tin liên hệ</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Giới tính / Ngày sinh</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Đánh giá</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Tình trạng học tập</th>
              <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Trạng thái (Vòng đời)</th>
              <th class="text-right px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider w-24">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr
              v-for="(student, idx) in filteredStudents"
              :key="student.name"
              @click="selectStudent(student)"
              class="hover:bg-hover/40 transition-colors cursor-pointer"
              :class="selected.includes(student.name) ? 'bg-brand-tint/30' : (selectedStudent?.name === student.name ? 'bg-brand-tint/10 border-l-2 border-brand' : '')"
            >
              <td class="px-4 py-3" @click.stop>
                <input type="checkbox" :value="student.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
              </td>
              <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
              <td class="px-6 py-4">
                <div class="font-bold text-ink-2">{{ student.full_name }}</div>
                <div class="text-[11px] text-faint font-mono mt-0.5">{{ student.name }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="font-medium text-ink-2 text-xs">{{ student.phone || 'Không có SĐT' }}</div>
                <div class="text-[11px] text-faint mt-0.5">{{ student.email || 'Chưa cập nhật email' }}</div>
              </td>
              <td class="px-6 py-4 text-xs">
                <div class="font-medium text-ink-2">{{ student.gender || 'Chưa rõ' }}</div>
                <div class="text-faint mt-0.5">{{ student.date_of_birth || '---' }}</div>
              </td>
              <td class="px-6 py-4 text-amber text-xs font-semibold">
                {{ getStars(student.rating) }}
              </td>
              <td class="px-6 py-4">
                <span class="pill" :class="getHealthPillClass(student.health_status)">
                  {{ student.health_status || 'Đang học đều' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="getLifecycleBadgeClass(student.student_status)">
                  {{ student.student_status || 'Mới nhập học' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right" @click.stop>
                <div class="flex items-center justify-end gap-2">
                  <button @click="editStudent(student)" class="p-1 text-muted hover:text-brand hover:bg-hover rounded transition-colors" title="Chỉnh sửa">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Student Detail Modal (Replacing Drawer) -->
    <div v-if="selectedStudent" @click.self="selectedStudent = null" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl mx-4 p-6 overflow-y-auto max-h-[90vh] cursor-default flex flex-col">
        <div class="flex items-center justify-between mb-4 border-b border-divider pb-3 flex-shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-brand-soft flex items-center justify-center text-brand font-bold text-sm">
              {{ selectedStudent.full_name?.charAt(0) }}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-lg font-bold text-ink-2">{{ selectedStudent.full_name }}</h2>
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-muted border border-border">{{ selectedStudent.name }}</span>
              </div>
              <p class="text-xs text-muted mt-0.5 flex items-center gap-2">
                <span class="flex items-center gap-1"><svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg> {{ selectedStudent.phone || 'Chưa cập nhật' }}</span>
                <span class="text-border">•</span>
                <span class="flex items-center gap-1"><svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg> {{ selectedStudent.email || 'Chưa cập nhật' }}</span>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="editStudent(selectedStudent)" class="p-1.5 text-muted hover:text-brand hover:bg-hover rounded border border-transparent transition-colors" title="Chỉnh sửa">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button @click="selectedStudent = null" class="p-1.5 text-faint hover:text-muted rounded transition-colors">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Pipeline Lifecycle Progress Bar -->
        <div class="mb-5 bg-hover/40 p-3 rounded-xl border border-border flex items-center justify-between flex-shrink-0">
          <div class="flex items-center gap-1.5 flex-1">
            <template v-for="(step, idx) in lifecycleSteps" :key="step.id">
              <button 
                @click="triggerStatusTransition(selectedStudent, step.id)"
                class="flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all text-center"
                :class="getLifecycleStepClass(selectedStudent.student_status, step.id)"
              >
                {{ step.label }}
              </button>
              <svg v-if="idx < lifecycleSteps.length - 1" class="h-4 w-4 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </template>
          </div>
          <div class="ml-4 border-l border-divider pl-4 flex gap-2">
            <button 
              @click="triggerStatusTransition(selectedStudent, 'Bảo lưu')"
              class="px-4 py-1.5 text-xs font-bold rounded-lg border transition-all"
              :class="selectedStudent.student_status === 'Bảo lưu' ? 'bg-amber-500 text-white border-amber-500 shadow-sm shadow-amber-500/20' : 'bg-white border-border text-amber-600 hover:bg-amber-50'"
            >
              Bảo lưu
            </button>
            <button 
              @click="triggerStatusTransition(selectedStudent, 'Nghỉ học')"
              class="px-4 py-1.5 text-xs font-bold rounded-lg border transition-all"
              :class="selectedStudent.student_status === 'Nghỉ học' ? 'bg-red-500 text-white border-red-500 shadow-sm shadow-red-500/20' : 'bg-white border-border text-red-600 hover:bg-red-50'"
            >
              Nghỉ học
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto grid grid-cols-12 gap-5 pr-1">
          <!-- Cột 1: Thông tin cá nhân -->
          <div class="col-span-4 bg-slate-50 p-4 rounded-xl border border-border space-y-4 text-xs h-max">
            <div>
              <h4 class="font-bold text-ink-2 border-b border-divider pb-2 text-xs uppercase tracking-wider text-brand">Hồ sơ chi tiết</h4>
              <div class="grid grid-cols-3 gap-y-2 mt-3 text-muted">
                <span class="font-semibold">Ngày sinh:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.date_of_birth || '—' }}</span>

                <span class="font-semibold">Giới tính:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.gender || '—' }}</span>

                <span class="font-semibold">Nguồn:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.source || '—' }}</span>

                <span class="font-semibold">Ngành nghề:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.occupation || '—' }}</span>

                <span class="font-semibold">Người giám hộ:</span>
                <span class="col-span-2 text-ink-2 font-medium">{{ selectedStudent.guardian_name || '—' }}</span>

                <span class="font-semibold">SĐT Phụ huynh:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.guardian_phone || '—' }}</span>

                <span class="font-semibold text-brand">Đánh giá:</span>
                <span class="col-span-2 text-amber-500 font-bold">{{ getStars(selectedStudent.rating) }}</span>
                
                <span class="font-semibold">Rep tin nhắn:</span>
                <span class="col-span-2 text-ink-2">{{ selectedStudent.message_response || '—' }}</span>
                
                <span class="font-semibold">Ngày nhập học:</span>
                <span class="col-span-2 text-ink-2 font-medium">{{ (selectedStudent.creation || '').split(' ')[0] }}</span>
              </div>
            </div>

            <div class="border-t border-divider pt-3 space-y-2">
              <h5 class="font-bold text-ink-2 text-xs uppercase tracking-wider text-brand">Tiến độ học tập chung</h5>
              <div class="grid grid-cols-2 gap-2 mt-2">
                <div class="bg-white p-2 rounded border border-border">
                  <p class="text-[10px] text-faint font-semibold uppercase">Điểm TB</p>
                  <p class="text-base font-bold text-brand mt-0.5">{{ selectedStudent.average_score || '0' }}</p>
                </div>
                <div class="bg-white p-2 rounded border border-border">
                  <p class="text-[10px] text-faint font-semibold uppercase">Chuyên cần</p>
                  <p class="text-sm font-bold text-ink-2 mt-0.5">{{ selectedStudent.attendance_status || 'Tốt' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Cột 2: Khóa học, Điểm danh, Lịch sử học -->
          <div class="col-span-4 bg-white p-4 rounded-xl border border-border flex flex-col h-[400px]">
            <div class="flex items-center justify-between border-b border-divider pb-2 mb-3 flex-shrink-0">
              <h4 class="font-bold text-ink-2 text-xs uppercase tracking-wider text-brand">Lớp học đang tham gia</h4>
            </div>
            
            <div class="flex-1 overflow-y-auto space-y-3">
              <div v-if="loadingEnrollments" class="text-center py-4"><span class="animate-pulse text-faint">Đang tải...</span></div>
              <div v-else-if="!studentEnrollments.length" class="text-center py-8 text-faint text-xs">
                Học viên chưa đăng ký lớp học nào.
              </div>
              <div v-else v-for="enr in studentEnrollments" :key="enr.name" class="p-3 bg-brand-soft/30 border border-brand/20 rounded-lg">
                <div class="flex justify-between items-start mb-1">
                  <h5 class="font-bold text-ink-2 text-sm">{{ getClassName(enr.class_id) }}</h5>
                  <span class="px-2 py-0.5 text-[10px] bg-emerald-100 text-emerald-700 font-bold rounded border border-emerald-200">Đang học</span>
                </div>
                <p class="text-[11px] text-muted">Ngày ghi danh: {{ enr.enrollment_date }}</p>
              </div>
              
              <!-- Placeholder cho Lịch sử kiểm tra / điểm danh -->
              <div class="mt-4 pt-4 border-t border-border">
                <h5 class="font-bold text-ink-2 text-xs mb-2 uppercase tracking-wider text-brand">Lịch sử điểm danh</h5>
                <div class="text-[11px] text-faint italic p-3 bg-slate-50 rounded border border-border">
                  Chưa có dữ liệu điểm danh.
                </div>
              </div>
            </div>
          </div>

          <!-- Cột 3: Phễu Cảnh báo & Ghi chú -->
          <div class="col-span-4 flex flex-col gap-4">
            <div class="bg-white p-4 rounded-xl border border-border flex flex-col items-center relative overflow-hidden flex-1 h-[400px]">
              <h4 class="text-xs font-bold text-muted uppercase tracking-wider mb-2 self-start w-full">Phễu Tình Trạng Học Tập</h4>
              
              <div class="relative w-full flex-1 flex justify-center items-center mt-2 min-h-[220px]">
                <svg viewBox="0 0 120 200" class="absolute w-24 h-full z-0" preserveAspectRatio="none">
                  <polygon points="10,2 110,2 102,38 18,38" :fill="getFunnelFill(0)"/>
                  <polygon points="18,42 102,42 94,78 26,78" :fill="getFunnelFill(1)"/>
                  <polygon points="26,82 94,82 86,118 34,118" :fill="getFunnelFill(2)"/>
                  <polygon points="34,122 86,122 78,158 42,158" :fill="getFunnelFill(3)"/>
                  <polygon points="42,162 78,162 70,198 50,198" :fill="getFunnelFill(4)"/>
                </svg>
                <div class="absolute inset-0 flex flex-col justify-between py-2 z-10 pl-10">
                  <div v-for="(stage, idx) in funnelStages" :key="stage.label" class="flex items-center w-full relative">
                    <div class="w-3 h-3 rounded-full mr-3 z-20 shadow-sm border border-white/50" :class="stage.colorClass + (selectedStudent?.health_status === stage.label ? ' ring-4 ring-opacity-40 ' + stage.ringClass : '')"></div>
                    <span class="text-[11px] font-semibold whitespace-nowrap" :class="selectedStudent?.health_status === stage.label ? 'text-ink font-bold' : 'text-muted'">{{ stage.label }}</span>
                  </div>
                </div>
              </div>
              
              <div class="mt-4 w-full">
                <label class="block text-[10px] font-bold text-muted uppercase mb-1">Cập nhật phân khúc:</label>
                <select @change="updateHealthStatus($event.target.value)" :value="selectedStudent.health_status || 'Đang học đều'" class="w-full text-xs px-2 py-2 border border-border rounded-lg bg-white text-ink-2 font-semibold focus:ring-1 focus:ring-brand">
                  <option v-for="s in funnelStages" :key="s.label" :value="s.label">{{ s.label }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" @click.self="closeCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden cursor-default animate-fade-in animate-duration-200">
        <div class="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 class="ff-display text-base font-bold text-ink-2">{{ isEditing ? 'Chỉnh Sửa Học Viên' : 'Thêm Học Viên Mới' }}</h3>
          <button @click="closeCreateModal" class="text-faint hover:text-muted transition-colors"><FeatherIcon name="x" class="w-4 h-4" /></button>
        </div>
        <div class="p-5 max-h-[70vh] overflow-y-auto space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Họ và tên *</label>
              <input type="text" v-model="formData.full_name" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" placeholder="Nhập họ và tên" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Email</label>
              <input type="email" v-model="formData.email" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" placeholder="example@mail.com" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Số điện thoại</label>
              <input type="text" v-model="formData.phone" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" placeholder="Số điện thoại" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngày sinh</label>
              <input type="date" v-model="formData.date_of_birth" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Giới tính</label>
              <select v-model="formData.gender" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
                <option value="Khác">Khác</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Trạng thái (Vòng đời)</label>
              <select v-model="formData.student_status" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
                <option value="Mới nhập học">Mới nhập học</option>
                <option value="Đang học">Đang học</option>
                <option value="Bảo lưu">Bảo lưu</option>
                <option value="Đã tốt nghiệp">Đã tốt nghiệp</option>
                <option value="Nghỉ học">Nghỉ học</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngành nghề</label>
              <input type="text" v-model="formData.occupation" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400" placeholder="Ngành nghề" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Đánh giá</label>
              <select v-model="formData.rating" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
                <option value="1 Sao">1 Sao</option>
                <option value="2 Sao">2 Sao</option>
                <option value="3 Sao">3 Sao</option>
                <option value="4 Sao">4 Sao</option>
                <option value="5 Sao">5 Sao</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Phản hồi tin nhắn</label>
              <select v-model="formData.message_response" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
                <option value="Tốt">Tốt</option>
                <option value="Bình thường">Bình thường</option>
                <option value="Chậm">Chậm</option>
                <option value="Không trả lời">Không trả lời</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Tình trạng học tập</label>
              <select v-model="formData.health_status" class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
                <option value="Đang học đều">Đang học đều</option>
                <option value="Cần theo dõi">Cần theo dõi</option>
                <option value="Cảnh báo">Cảnh báo</option>
                <option value="Khẩn cấp">Khẩn cấp</option>
                <option value="Ngừng học">Ngừng học</option>
              </select>
            </div>
          </div>
        </div>
        <!-- Modal Footer -->
        <div class="px-5 py-3.5 border-t border-border bg-hover/40 flex justify-end gap-2.5">
          <button @click="closeCreateModal" class="flex-1 sm:flex-none px-4 py-2 border border-border text-sm font-semibold text-muted rounded-lg hover:bg-hover transition-colors">Hủy</button>
          <button @click="saveStudent" :disabled="saving" class="flex-1 sm:flex-none px-5 py-2 bg-brand text-white text-sm font-semibold rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : 'Lưu học viên' }}
          </button>
        </div>
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
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> học viên. Hành động này không thể hoàn tác.</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40">Hủy</button>
          <button @click="confirmDelete" :disabled="deleting" class="flex-1 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { LoadingIndicator, FeatherIcon } from 'frappe-ui'
import { apiResource, listResource, db } from '../api'

const showCreateModal = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const selectedStudent = ref(null)
const searchQuery = ref('')
const selected = ref([])
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const filterGender = ref('')
const filterClass = ref('')
const periodFilter = ref('')
const periods = [
  { label: 'Tất cả', value: '' },
  { label: 'Tháng này', value: 'month' },
  { label: 'Năm nay', value: 'year' },
]

function getDateRange(period) {
  const now = new Date()
  if (period === 'month') return new Date(now.getFullYear(), now.getMonth(), 1)
  if (period === 'year') return new Date(now.getFullYear(), 0, 1)
  return null
}

const defaultForm = {
  full_name: '', email: '', phone: '', date_of_birth: '', gender: 'Nam', 
  source: 'Facebook', occupation: '', rating: '5 Sao', message_response: 'Tốt', health_status: 'Đang học đều',
  student_status: 'Mới nhập học'
}
const formData = ref({ ...defaultForm })
const editableStudentFields = [
  'full_name',
  'email',
  'phone',
  'date_of_birth',
  'gender',
  'source',
  'occupation',
  'rating',
  'message_response',
  'health_status',
  'student_status',
]

const students = apiResource('get_students', { auto: true })

const classesList = listResource('Class', {
  fields: ['name', 'class_name'],
  limit_page_length: 500,
  auto: true
})

// Fetch enrollments mapped by student
const enrollmentsList = listResource('Program Enrollment', {
  fields: ['name', 'student', 'class_id', 'enrollment_date'],
  limit_page_length: 1000,
  auto: true
})

const studentEnrollmentsMap = computed(() => {
  const map = {}
  if (enrollmentsList.data) {
    enrollmentsList.data.forEach(e => {
      if (!map[e.student]) map[e.student] = []
      map[e.student].push(e)
    })
  }
  return map
})

const getClassName = (classId) => {
  const cls = classesList.data?.find(c => c.name === classId)
  return cls ? cls.class_name : classId
}

const filteredStudents = computed(() => {
  if (!students.data) return []
  let data = students.data
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    data = data.filter(s => s.full_name.toLowerCase().includes(q) || s.name.toLowerCase().includes(q))
  }
  
  if (filterGender.value) {
    data = data.filter(s => s.gender === filterGender.value)
  }
  
  if (filterClass.value) {
    data = data.filter(s => {
      const enrs = studentEnrollmentsMap.value[s.name] || []
      return enrs.some(e => e.class_id === filterClass.value)
    })
  }
  
  const start = getDateRange(periodFilter.value)
  if (start) {
    data = data.filter(s => {
      if (!s.creation) return false
      return new Date(s.creation) >= start
    })
  }
  
  return data
})

const allSelected = computed(() =>
  filteredStudents.value.length > 0 && filteredStudents.value.every(s => selected.value.includes(s.name))
)

const toggleSelectAll = () => {
  allSelected.value ? selected.value = [] : selected.value = filteredStudents.value.map(s => s.name)
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Student', name)
    }
    selected.value = []
    showDeleteConfirm.value = false
    await students.fetch()
    selectedStudent.value = null
  } catch (err) {
    alert('Lỗi khi xóa: ' + (err.message || ''))
  } finally {
    deleting.value = false
  }
}

// Lifecycle Pipeline
const lifecycleSteps = [
  { id: 'Mới nhập học', label: 'Mới' },
  { id: 'Đang học', label: 'Đang học' },
  { id: 'Đã tốt nghiệp', label: 'Tốt nghiệp' }
]

const getLifecycleStepClass = (currentStatus, stepId) => {
  if (currentStatus === stepId) {
    return 'bg-brand text-white border-brand shadow-sm shadow-emerald-500/20'
  }
  const statusOrder = ['Mới nhập học', 'Đang học', 'Đã tốt nghiệp']
  const curIdx = statusOrder.indexOf(currentStatus || 'Mới nhập học')
  const stIdx = statusOrder.indexOf(stepId)
  if (stIdx < curIdx && currentStatus !== 'Bảo lưu' && currentStatus !== 'Nghỉ học') {
    return 'bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100'
  }
  return 'bg-white border-border text-muted hover:bg-slate-100'
}

const getLifecycleBadgeClass = (status) => {
  if (status === 'Đang học') return 'bg-emerald-100 text-emerald-700'
  if (status === 'Bảo lưu') return 'bg-amber-100 text-amber-700'
  if (status === 'Đã tốt nghiệp') return 'bg-blue-100 text-blue-700'
  if (status === 'Nghỉ học') return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-700' // Mới nhập học
}

const triggerStatusTransition = async (student, newStatus) => {
  if (student.student_status === newStatus) return
  if (!confirm(`Chuyển trạng thái học viên sang: ${newStatus}?`)) return
  try {
    await db.setValue('Student', student.name, 'student_status', newStatus)
    student.student_status = newStatus
    students.fetch()
  } catch (err) {
    alert('Lỗi: ' + err.message)
  }
}

// Funnel
const funnelStages = [
  { label: 'Đang học đều', colorClass: 'bg-sage', ringClass: 'ring-sage', activeColor: 'var(--sage)', inactiveColor: 'var(--sage-soft)' },
  { label: 'Cần theo dõi', colorClass: 'bg-brand', ringClass: 'ring-brand', activeColor: 'var(--brand)', inactiveColor: 'var(--brand-soft)' },
  { label: 'Cảnh báo', colorClass: 'bg-amber', ringClass: 'ring-amber', activeColor: 'var(--amber)', inactiveColor: 'var(--amber-soft)' },
  { label: 'Khẩn cấp', colorClass: 'bg-rose', ringClass: 'ring-rose', activeColor: 'var(--rose)', inactiveColor: 'var(--rose-soft)' },
  { label: 'Ngừng học', colorClass: 'bg-ink', ringClass: 'ring-ink', activeColor: 'var(--ink)', inactiveColor: 'var(--hover)' }
]

const getFunnelFill = (idx) => {
  if (!selectedStudent.value) return 'var(--hover)'
  const studentStatus = selectedStudent.value.health_status || 'Đang học đều'
  const currentIdx = funnelStages.findIndex(s => s.label === studentStatus)
  const stage = funnelStages[idx]
  if (idx === currentIdx) return stage.activeColor
  return stage.inactiveColor
}

const updateHealthStatus = async (val) => {
  try {
    await db.setValue('Student', selectedStudent.value.name, 'health_status', val)
    selectedStudent.value.health_status = val
    students.fetch()
  } catch (err) {
    alert('Lỗi cập nhật phễu.')
  }
}

const getStars = (val) => {
  if (!val) return '⭐⭐⭐⭐⭐'
  const n = parseInt(val.split(' ')[0])
  return '⭐'.repeat(n)
}

const loadingEnrollments = ref(false)
const studentEnrollments = ref([])

const selectStudent = (student) => {
  selectedStudent.value = student
  studentEnrollments.value = studentEnrollmentsMap.value[student.name] || []
}

const openCreateModal = () => {
  formData.value = { ...defaultForm }
  isEditing.value = false
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  formData.value = { ...defaultForm }
  isEditing.value = false
}

const editStudent = (student) => {
  formData.value = { ...student }
  isEditing.value = true
  showCreateModal.value = true
}

const getHealthPillClass = (status) => {
  if (status === 'Khẩn cấp') return 'pill-rose'
  if (status === 'Cảnh báo') return 'pill-amber'
  if (status === 'Cần theo dõi') return 'pill-sky'
  if (status === 'Đang học đều') return 'pill-sage'
  return 'pill-faint'
}

const saveStudent = async () => {
  if (!formData.value.full_name) {
    alert('Vui lòng nhập họ và tên học viên.')
    return
  }
  
  saving.value = true
  try {
    if (isEditing.value) {
      const values = {}
      for (const key of editableStudentFields) values[key] = formData.value[key]
      await db.setValue('Student', formData.value.name, values)
    } else {
      const doc = { doctype: 'Student' }
      for (const key of editableStudentFields) doc[key] = formData.value[key]
      await db.insert(doc)
    }
    showCreateModal.value = false
    await students.fetch()
    if (isEditing.value) {
      selectedStudent.value = students.data.find(s => s.name === formData.value.name)
    }
    formData.value = { ...defaultForm }
    isEditing.value = false
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra.')
  } finally {
    saving.value = false
  }
}
</script>
