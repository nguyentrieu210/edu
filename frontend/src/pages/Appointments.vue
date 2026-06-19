<template>
  <div class="h-full flex flex-col overflow-hidden space-y-6">
    <!-- Header Toolbar -->
    <div class="flex items-center justify-between flex-shrink-0">
      <div>
        <h3 class="text-xl font-bold text-ink-2">Lịch Hẹn Tư Vấn</h3>
        <p class="text-xs text-muted mt-1 font-medium">Đặt lịch, theo dõi trạng thái các cuộc hẹn tư vấn hoặc kiểm tra đầu vào của leads.</p>
      </div>
      <button
        @click="openAddModal"
        class="flex items-center gap-2 px-4 py-2 bg-brand text-white text-sm font-medium rounded-lg hover:bg-brand-deep transition-colors shadow-sm shadow-emerald-600/20"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Đặt lịch hẹn
      </button>
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
          v-model="search"
          type="text"
          placeholder="Tìm lịch hẹn theo tên khách hàng, số điện thoại..."
          class="w-full pl-10 pr-4 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
        />
      </div>
      <div class="w-full sm:w-48">
        <select v-model="filterStatus" class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 bg-white text-muted">
          <option value="">Tất cả trạng thái</option>
          <option value="Scheduled">Sắp tới</option>
          <option value="Completed">Hoàn thành</option>
          <option value="Cancelled">Đã hủy</option>
          <option value="Rescheduled">Dời lịch</option>
        </select>
      </div>
      <!-- Period Filter -->
      <div class="flex items-center gap-1 bg-hover/40 border border-border rounded-lg p-1">
        <button v-for="p in periods" :key="p.value" @click="periodFilter = p.value"
          class="px-3 py-1 text-xs font-medium rounded-md transition-all"
          :class="periodFilter === p.value ? 'bg-brand text-white shadow-sm' : 'text-muted hover:bg-white'">
          {{ p.label }}
        </button>
      </div>
      <div class="flex items-center gap-1 border border-border rounded-lg overflow-hidden p-0.5 bg-hover/40">
        <button @click="viewMode='list'" :class="viewMode==='list' ? 'bg-white text-ink-2 shadow-sm border-border' : 'text-muted hover:bg-hover/50'" class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors border border-transparent">
          ☰ Danh sách
        </button>
        <button @click="viewMode='calendar'" :class="viewMode==='calendar' ? 'bg-white text-ink-2 shadow-sm border-border' : 'text-muted hover:bg-hover/50'" class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors border border-transparent">
          📅 Lịch
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

    <!-- Stats Row -->
    <div v-if="!appointments.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-4 flex-shrink-0 animate-fade-in">
      <div class="bg-white rounded-xl border border-border p-4 shadow-sm">
        <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tổng lịch hẹn</p>
        <p class="text-2xl font-bold text-ink-2 mt-1">{{ appointments.data ? appointments.data.length : 0 }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4 shadow-sm">
        <p class="text-xs text-blue-600 font-semibold uppercase tracking-wider">Sắp tới</p>
        <p class="text-2xl font-bold text-blue-600 mt-1">{{ scheduledCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4 shadow-sm">
        <p class="text-xs text-brand font-semibold uppercase tracking-wider">Hoàn thành</p>
        <p class="text-2xl font-bold text-brand mt-1">{{ completedCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-border p-4 shadow-sm">
        <p class="text-xs text-rose-500 font-semibold uppercase tracking-wider">Đã hủy</p>
        <p class="text-2xl font-bold text-rose-500 mt-1">{{ cancelledCount }}</p>
      </div>
    </div>

    <!-- Today's Appointments Banner -->
    <div v-if="todayAppointments.length > 0" class="p-4 bg-brand-tint border border-emerald-200 rounded-xl flex-shrink-0 animate-fade-in">
      <p class="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-2">📅 Hôm nay ({{ todayAppointments.length }} lịch hẹn)</p>
      <div class="flex flex-wrap gap-2">
        <span v-for="apt in todayAppointments" :key="apt.name" class="inline-flex items-center gap-1.5 text-xs bg-white border border-emerald-200 rounded-lg px-3 py-2 text-emerald-800 font-medium shadow-sm">
          🕐 {{ apt.appointment_time }} — <span class="font-bold">{{ getLeadName(apt.lead) }}</span> — {{ apt.purpose }}
        </span>
      </div>
    </div>

    <div v-if="appointments.loading" class="flex justify-center py-8">
      <LoadingIndicator />
    </div>

    <!-- Appointments List View -->
    <div class="flex-1 overflow-y-auto" v-else-if="viewMode === 'list'">
      <div v-if="filteredAppointments.length === 0" class="flex flex-col items-center justify-center h-48 text-faint bg-white border border-border rounded-xl">
        <svg class="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-sm font-medium">Không tìm thấy lịch hẹn nào</p>
      </div>

      <div v-else class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-hover/40 border-b border-border">
              <tr>
                <th class="px-4 py-3 w-10">
                  <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
                </th>
                <th class="px-3 py-3 text-left text-xs font-semibold text-muted uppercase tracking-wider w-12">STT</th>
                <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Khách hàng / Mã hẹn</th>
                <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Thời gian</th>
                <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Mục đích</th>
                <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Trạng thái Hẹn</th>
                <th class="text-left px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Trạng thái CRM</th>
                <th class="text-right px-6 py-3.5 text-xs font-semibold text-muted uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border bg-white">
              <tr
                v-for="(apt, idx) in filteredAppointments"
                :key="apt.name"
                class="hover:bg-hover/40 transition-colors"
                :class="selected.includes(apt.name) ? 'bg-brand-tint/30' : ''"
              >
                <td class="px-4 py-3">
                  <input type="checkbox" :value="apt.name" v-model="selected" class="w-4 h-4 rounded border-border text-brand focus:ring-brand cursor-pointer" />
                </td>
                <td class="px-3 py-4 text-xs text-faint font-mono tabular-nums">{{ idx + 1 }}</td>
                <td class="px-6 py-4">
                  <div class="font-semibold text-ink-2">{{ getLeadName(apt.lead) }}</div>
                  <div class="text-xs text-faint font-medium mt-0.5">{{ apt.name }} <span v-if="getLeadPhone(apt.lead)">• {{ getLeadPhone(apt.lead) }}</span></div>
                </td>
                <td class="px-6 py-4">
                  <div class="font-medium text-ink-2">{{ formatDate(apt.appointment_date) }}</div>
                  <div class="text-xs text-faint mt-0.5">🕒 {{ apt.appointment_time || 'Chưa hẹn giờ' }}</div>
                </td>
                <td class="px-6 py-4 text-muted text-xs font-medium">{{ apt.purpose || '—' }}</td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold" :class="statusClass(apt.status)">
                    {{ translateStatus(apt.status) }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span v-if="getLeadStatus(apt.lead)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold border" :class="getLeadStatusClass(getLeadStatus(apt.lead))">
                    {{ translateLeadStatus(getLeadStatus(apt.lead)) }}
                  </span>
                  <span v-else class="text-xs text-faint">—</span>
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <button @click="completeApt(apt)" v-if="apt.status === 'Scheduled'" class="text-xs px-2.5 py-1 bg-brand-tint text-brand rounded-lg hover:bg-brand-soft transition-colors font-semibold" title="Hoàn thành">Hoàn thành</button>
                    <button @click="cancelApt(apt)" v-if="apt.status === 'Scheduled'" class="text-xs px-2.5 py-1 bg-thaco-red-soft text-thaco-red rounded-lg hover:bg-thaco-red-soft transition-colors font-semibold" title="Hủy">Hủy</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>


    <!-- Calendar View -->
    <div v-else class="flex-1 min-h-0 flex flex-col lg:flex-row gap-6 overflow-hidden">
      <!-- Left Side: Month Calendar Grid -->
      <div class="flex-1 min-h-0 flex flex-col bg-white rounded-xl border border-border p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4 flex-shrink-0">
          <button @click="prevWeek" class="p-2 rounded-lg hover:bg-hover transition-colors">
            <svg class="h-5 w-5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h3 class="text-sm font-bold text-ink-2 uppercase tracking-wider">{{ weekRangeStr }}</h3>
          <button @click="nextWeek" class="p-2 rounded-lg hover:bg-hover transition-colors">
            <svg class="h-5 w-5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div class="grid grid-cols-7 gap-3 flex-shrink-0">
          <div v-for="day in calendarDays" :key="day.date" 
            @click="selectDate(day.date)"
            class="rounded-xl p-3 text-center relative cursor-pointer hover:bg-hover/50 hover:scale-[1.02] transition-all border flex flex-col items-center justify-center gap-1 select-none h-28" 
            :class="[
              day.date === selectedDate ? 'border-brand ring-2 ring-brand bg-brand-tint/40 shadow-sm' : 'border-border bg-white',
              day.isToday ? 'border-brand/40' : ''
            ]">
            <span class="text-[10px] font-semibold text-muted uppercase tracking-wider">
              {{ ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'][calendarDays.indexOf(day)] }}
            </span>
            <span :class="day.isToday ? 'text-brand font-bold bg-brand-soft px-2.5 py-1 rounded-full' : 'text-ink-2 font-bold text-base'" class="inline-block leading-none my-1">
              {{ day.day }}
            </span>
            <span class="text-[9px] text-faint font-medium">T{{ day.month }}</span>
            
            <div v-if="day.appointments.length > 0" class="flex gap-1 justify-center mt-1">
              <div v-for="apt in day.appointments.slice(0, 3)" :key="apt.name" 
                class="w-1.5 h-1.5 rounded-full" 
                :class="apt.status === 'Completed' ? 'bg-emerald-500' : apt.status === 'Cancelled' ? 'bg-red-500' : apt.status === 'Rescheduled' ? 'bg-amber-500' : 'bg-blue-500'"
                :title="getLeadName(apt.lead) + ' - ' + apt.purpose"></div>
              <span v-if="day.appointments.length > 3" class="text-[8px] text-faint leading-none font-bold">+</span>
            </div>
          </div>
        </div>

        <!-- Weekly Summary List below the calendar row -->
        <div class="flex-1 min-h-0 flex flex-col mt-6 border-t border-border pt-4">
          <h4 class="text-xs font-bold text-muted uppercase tracking-wider mb-3">Tất cả lịch hẹn trong tuần</h4>
          <div class="flex-1 overflow-y-auto space-y-2 pr-1">
            <div v-if="weeklyAppointments.length === 0" class="flex flex-col items-center justify-center h-full text-faint bg-canvas/10 border border-dashed border-border rounded-xl">
              <p class="text-xs">Không có lịch hẹn nào trong tuần này</p>
            </div>
            <div v-else v-for="apt in weeklyAppointments" :key="apt.name" 
              @click="selectDate(apt.appointment_date)"
              class="flex items-center justify-between p-2.5 rounded-lg border border-border/80 hover:border-brand/40 bg-canvas/30 hover:bg-hover/20 cursor-pointer transition-all">
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-ink-2 bg-white px-2 py-1 rounded border border-border">
                  {{ formatDateShort(apt.appointment_date) }}
                </span>
                <div>
                  <span class="text-xs font-semibold text-ink-2 block">{{ getLeadName(apt.lead) }}</span>
                  <span class="text-[10px] text-faint block">{{ apt.appointment_time || 'Chưa hẹn' }} • {{ apt.purpose || '—' }}</span>
                </div>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold" :class="statusClass(apt.status)">
                {{ translateStatus(apt.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side: Details panel for the selected date -->
      <div class="w-full lg:w-96 flex flex-col min-h-0 bg-white rounded-xl border border-border p-5 shadow-sm">
        <div class="border-b border-border pb-3 mb-4 flex-shrink-0 flex items-center justify-between">
          <div>
            <h4 class="text-sm font-bold text-ink-2">Lịch hẹn ngày</h4>
            <p class="text-xs text-muted mt-0.5 font-medium">{{ formatDate(selectedDate) }}</p>
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 bg-hover/80 text-muted rounded-full">
            {{ selectedDateAppointments.length }} cuộc hẹn
          </span>
        </div>

        <!-- Appointment list for selected date -->
        <div class="flex-1 overflow-y-auto space-y-3 pr-1">
          <div v-if="selectedDateAppointments.length === 0" class="flex flex-col items-center justify-center h-full text-faint">
            <svg class="h-8 w-8 mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p class="text-xs font-medium">Không có lịch hẹn trong ngày này</p>
          </div>

          <div v-else v-for="apt in selectedDateAppointments" :key="apt.name" 
            class="p-3 border border-border rounded-xl hover:border-brand/40 transition-colors bg-canvas/30 space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <span class="text-xs font-bold text-ink-2 block truncate">{{ getLeadName(apt.lead) }}</span>
                <span class="text-[11px] text-faint block mt-0.5">{{ getLeadPhone(apt.lead) || 'Không có SĐT' }}</span>
              </div>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold flex-shrink-0" :class="statusClass(apt.status)">
                {{ translateStatus(apt.status) }}
              </span>
            </div>
            
            <div class="text-xs text-muted space-y-1 bg-white p-2 rounded-lg border border-border/60">
              <div class="flex items-center gap-1.5">
                <span class="text-faint text-[11px]">🕒 Giờ:</span>
                <span class="font-medium text-ink-2">{{ apt.appointment_time || 'Chưa hẹn' }}</span>
              </div>
              <div class="flex items-start gap-1.5">
                <span class="text-faint text-[11px] flex-shrink-0">🎯 Mục đích:</span>
                <span class="text-ink-2 line-clamp-2" :title="apt.purpose">{{ apt.purpose || '—' }}</span>
              </div>
            </div>

            <div v-if="apt.status === 'Scheduled'" class="flex gap-2 justify-end pt-1">
              <button @click="cancelApt(apt)" class="px-2.5 py-1 text-[11px] font-semibold border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                Hủy hẹn
              </button>
              <button @click="completeApt(apt)" class="px-2.5 py-1 text-[11px] font-semibold bg-brand text-white rounded-lg hover:bg-brand-deep transition-colors">
                Hoàn thành
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Modal -->
    <div v-if="showAddModal" @click.self="showAddModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 cursor-default">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-bold text-ink-2">Đặt Lịch Hẹn Mới</h2>
          <button @click="showAddModal = false" class="text-faint hover:text-muted transition-colors">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Khách hàng / Lead *</label>
            <select v-model="newApt.lead" 
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400 bg-white">
              <option value="">Chọn khách hàng tiềm năng...</option>
              <option v-for="l in leadsList" :key="l.name" :value="l.name">
                {{ l.lead_name }} ({{ l.phone || 'Không số' }})
              </option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Ngày hẹn *</label>
              <input
                v-model="newApt.appointment_date"
                type="date"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Giờ hẹn</label>
              <input
                v-model="newApt.appointment_time"
                type="time"
                class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
              />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-muted mb-1.5 uppercase tracking-wider">Mục đích</label>
            <input
              v-model="newApt.purpose"
              placeholder="VD: Tư vấn khóa học, Kiểm tra đầu vào..."
              class="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-emerald-400"
            />
          </div>
        </div>

        <div class="flex gap-3 mt-6 border-t border-divider pt-4">
          <button @click="showAddModal = false" class="flex-1 py-2 text-sm font-medium text-muted border border-border rounded-lg hover:bg-hover/40 transition-colors">
            Hủy
          </button>
          <button @click="addAppointment" :disabled="saving" class="flex-1 py-2 text-sm font-medium text-white bg-brand rounded-lg hover:bg-brand-deep transition-colors disabled:opacity-50">
            {{ saving ? 'Đang lưu...' : 'Đặt lịch hẹn' }}
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
            <p class="text-xs text-muted mt-0.5">Bạn sắp xóa <span class="font-bold text-red-600">{{ selected.length }}</span> lịch hẹn. Hành động này không thể hoàn tác.</p>
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
import { LoadingIndicator } from 'frappe-ui'
import { listResource, db } from '../api'

const search = ref('')
const filterStatus = ref('')
const periodFilter = ref('')
const viewMode = ref('calendar')
const showAddModal = ref(false)
const saving = ref(false)
const leadsList = ref([])
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

const currentDate = ref(new Date())

// Load appointments
const appointments = listResource('Student Appointment', {
  fields: ['name', 'lead', 'appointment_date', 'appointment_time', 'purpose', 'status'],
  limit_page_length: 500,
  order_by: 'appointment_date desc',
  auto: true
})

// Load leads for select options
const loadLeads = async () => {
  try {
    const res = await db.getList('Student Lead', {
      fields: ['name', 'lead_name', 'phone', 'status'],
      limit_page_length: 500
    })
    leadsList.value = res || []
  } catch (err) {
    console.error('Error loading leads:', err)
  }
}

const leadMap = computed(() => {
  const map = {}
  leadsList.value.forEach(l => {
    map[l.name] = l
  })
  return map
})

const getLeadName = (leadId) => {
  return leadMap.value[leadId]?.lead_name || leadId
}

const getLeadPhone = (leadId) => {
  return leadMap.value[leadId]?.phone || ''
}

const getLeadStatus = (leadId) => {
  return leadMap.value[leadId]?.status || ''
}

const translateLeadStatus = (status) => {
  const map = {
    'New': 'Mới',
    'Consulting': 'Đang tư vấn',
    'Testing': 'Test đầu vào',
    'Trial': 'Học thử',
    'Enrolled': 'Đã nhập học',
    'Lost': 'Thất bại'
  }
  return map[status] || status
}

const getLeadStatusClass = (status) => {
  const map = {
    'New': 'bg-slate-100 text-slate-700 border-slate-200',
    'Consulting': 'bg-blue-50 text-blue-700 border-blue-200',
    'Testing': 'bg-amber-50 text-amber-700 border-amber-200',
    'Trial': 'bg-purple-50 text-purple-700 border-purple-200',
    'Enrolled': 'bg-emerald-50 text-emerald-700 border-emerald-200',
    'Lost': 'bg-red-50 text-red-700 border-red-200'
  }
  return map[status] || 'bg-slate-100 text-slate-700 border-slate-200'
}

const openAddModal = async () => {
  showAddModal.value = true
  await loadLeads()
}

const newApt = ref({
  lead: '',
  appointment_date: new Date().toISOString().split('T')[0],
  appointment_time: '09:00',
  purpose: ''
})

const today = new Date().toISOString().split('T')[0]
const selectedDate = ref(today)

const selectDate = (dateStr) => {
  selectedDate.value = dateStr
}

const selectedDateAppointments = computed(() => {
  const data = appointments.data || []
  return data.filter(a => a.appointment_date === selectedDate.value)
})

const todayAppointments = computed(() => {
  const data = appointments.data || []
  return data.filter(a => a.appointment_date === today && a.status === 'Scheduled')
})

const scheduledCount = computed(() => (appointments.data || []).filter(a => a.status === 'Scheduled').length)
const completedCount = computed(() => (appointments.data || []).filter(a => a.status === 'Completed').length)
const cancelledCount = computed(() => (appointments.data || []).filter(a => a.status === 'Cancelled').length)

const filteredAppointments = computed(() => {
  const data = appointments.data || []
  const start = getDateRange(periodFilter.value)
  return data.filter(a => {
    const leadName = getLeadName(a.lead).toLowerCase()
    const leadPhone = getLeadPhone(a.lead).toLowerCase()
    const matchSearch = !search.value || 
      leadName.includes(search.value.toLowerCase()) || 
      a.name.toLowerCase().includes(search.value.toLowerCase()) || 
      leadPhone.includes(search.value.toLowerCase())
    const matchStatus = !filterStatus.value || a.status === filterStatus.value
    const periodMatch = !start || !a.appointment_date || new Date(a.appointment_date) >= start
    return matchSearch && matchStatus && periodMatch
  }).sort((a, b) => new Date(b.appointment_date) - new Date(a.appointment_date))
})

const allSelected = computed(() =>
  filteredAppointments.value.length > 0 && filteredAppointments.value.every(a => selected.value.includes(a.name))
)
function toggleSelectAll() {
  allSelected.value ? selected.value = [] : selected.value = filteredAppointments.value.map(a => a.name)
}
const confirmDelete = async () => {
  deleting.value = true
  try {
    for (const name of selected.value) {
      await db.delete('Student Appointment', name)
    }
    selected.value = []; showDeleteConfirm.value = false; appointments.fetch()
  } catch (err) { alert('Lỗi khi xóa: ' + (err.message || '')) } finally { deleting.value = false }
}

const statusClass = (status) => {
  if (status === 'Scheduled') return 'bg-blue-100 text-blue-700'
  if (status === 'Completed') return 'bg-brand-soft text-brand'
  if (status === 'Cancelled') return 'bg-red-100 text-red-700'
  if (status === 'Rescheduled') return 'bg-amber-100 text-amber-700'
  return 'bg-hover text-muted'
}

const translateStatus = (status) => {
  if (status === 'Scheduled') return 'Sắp tới'
  if (status === 'Completed') return 'Hoàn thành'
  if (status === 'Cancelled') return 'Đã hủy'
  if (status === 'Rescheduled') return 'Dời lịch'
  return status
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('vi-VN')
}

const prevWeek = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 7)
  currentDate.value = d
}

const nextWeek = () => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 7)
  currentDate.value = d
}

const calendarDays = computed(() => {
  const current = new Date(currentDate.value)
  const dayOfWeek = current.getDay() // 0 (Sun) to 6 (Sat)
  
  // Start of week (Monday)
  const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  const startOfWeek = new Date(current)
  startOfWeek.setDate(current.getDate() + mondayOffset)
  
  const todayStr = new Date().toISOString().split('T')[0]
  const data = appointments.data || []
  
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek)
    d.setDate(startOfWeek.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    days.push({
      date: dateStr,
      day: d.getDate(),
      month: d.getMonth() + 1,
      isToday: dateStr === todayStr,
      appointments: data.filter(a => a.appointment_date === dateStr)
    })
  }
  return days
})

const weekRangeStr = computed(() => {
  const days = calendarDays.value
  if (days.length === 0) return ''
  const start = new Date(days[0].date)
  const end = new Date(days[6].date)
  const startStr = start.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })
  const endStr = end.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
  return `Tuần: ${startStr} - ${endStr}`
})

const weeklyAppointments = computed(() => {
  const days = calendarDays.value
  if (days.length === 0) return []
  const startStr = days[0].date
  const endStr = days[6].date
  const data = appointments.data || []
  return data.filter(a => a.appointment_date >= startStr && a.appointment_date <= endStr)
             .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date) || a.appointment_time.localeCompare(b.appointment_time))
})

const formatDateShort = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getDate()}/${d.getMonth() + 1}`
}

const completeApt = async (apt) => {
  try {
    await db.setValue('Student Appointment', apt.name, 'status', 'Completed')
    appointments.fetch()
  } catch (err) {
    console.error(err)
    alert('Lỗi cập nhật trạng thái')
  }
}

const cancelApt = async (apt) => {
  try {
    await db.setValue('Student Appointment', apt.name, 'status', 'Cancelled')
    appointments.fetch()
  } catch (err) {
    console.error(err)
    alert('Lỗi cập nhật trạng thái')
  }
}

const addAppointment = async () => {
  if (!newApt.value.lead || !newApt.value.appointment_date) {
    alert('Vui lòng chọn Lead và Ngày hẹn.')
    return
  }
  saving.value = true
  try {
    await db.insert({
      doctype: 'Student Appointment',
      lead: newApt.value.lead,
      appointment_date: newApt.value.appointment_date,
      appointment_time: newApt.value.appointment_time || undefined,
      purpose: newApt.value.purpose || undefined,
      status: 'Scheduled'
    })
    showAddModal.value = false
    appointments.fetch()
    newApt.value = { lead: '', appointment_date: new Date().toISOString().split('T')[0], appointment_time: '09:00', purpose: '' }
  } catch (err) {
    console.error(err)
    alert('Có lỗi xảy ra khi tạo lịch hẹn.')
  } finally {
    saving.value = false
  }
}

// Initial fetch of leads for mapping
loadLeads()
</script>
