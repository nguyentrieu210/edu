<template>
  <div class="flex h-screen bg-canvas font-sans text-ink antialiased overflow-hidden">

    <!-- Command Palette -->
    <CommandPalette ref="paletteRef" />

    <!-- Sidebar -->
    <aside
      class="flex flex-col bg-paper border-r border-border flex-shrink-0 select-none transition-all duration-300 ease-in-out relative z-30"
      :class="isSidebarExpanded ? 'w-64' : 'w-14'"
    >
      <!-- Logo Header -->
      <div class="flex h-14 items-center border-b border-border overflow-hidden"
        :class="!isSidebarExpanded ? 'justify-center px-0' : 'px-5 gap-3'">

        <!-- Icon Google-style -->
        <div class="h-8 w-8 rounded-lg bg-brand text-white flex items-center justify-center flex-shrink-0 shadow-sm shadow-brand/10">
          <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M12 2l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/></svg>
        </div>

        <!-- Wordmark ẩn khi collapsed -->
        <transition name="fade-slide">
          <div v-if="isSidebarExpanded" class="leading-tight overflow-hidden whitespace-nowrap">
            <div class="ff-display text-[15px] font-bold tracking-tight text-ink">IKE Ohashi</div>
            <div class="text-[10.5px] font-medium text-muted uppercase tracking-wider">education · erp</div>
          </div>
        </transition>
      </div>

      <!-- Toggle button -->
      <button
        @click="collapsed = !collapsed"
        class="absolute -right-3 top-16 z-10 w-6 h-6 rounded-full bg-paper border border-border shadow-sm flex items-center justify-center hover:bg-hover transition-all duration-200 hover:shadow"
      >
        <svg class="h-3 w-3 text-muted transition-transform duration-300" :class="collapsed ? 'rotate-180' : ''"
          fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Menu Navigation -->
      <nav class="flex-1 overflow-y-auto py-4 scrollbar-thin"
        :class="!isSidebarExpanded ? 'px-1.5 space-y-1' : 'px-3 space-y-1'">

        <div v-for="(group, idx) in menuGroups" :key="idx">

          <!-- Collapsed: chỉ show icon, tooltip -->
          <template v-if="!isSidebarExpanded">
            <router-link
              v-if="!group.children"
              :to="group.path"
              class="flex items-center justify-center w-10 h-10 mx-auto rounded-full text-muted hover:bg-hover hover:text-ink transition-all duration-150 relative group"
              active-class="bg-brand-soft text-brand font-medium"
              :title="group.label"
            >
              <FeatherIcon :name="group.icon" class="h-4.5 w-4.5" />
              <span class="absolute left-full ml-2 px-2.5 py-1.5 text-xs font-medium bg-ink text-paper rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50 shadow-lg">
                {{ group.label }}
              </span>
            </router-link>

            <button
              v-else
              @click="toggleGroup(group)"
              class="flex items-center justify-center w-10 h-10 mx-auto rounded-full transition-all duration-150 relative group"
              :class="isGroupActive(group) ? 'bg-brand-soft text-brand font-medium' : 'text-muted hover:bg-hover hover:text-ink'"
              :title="group.label"
            >
              <FeatherIcon :name="group.icon" class="h-4 w-4" />
              <span class="absolute left-full ml-2 px-2.5 py-1.5 text-xs font-medium bg-ink text-paper rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50 shadow-lg">
                {{ group.label }}
              </span>
            </button>
          </template>

          <!-- Expanded: full sidebar -->
          <template v-else>
            <!-- Direct link -->
            <router-link
              v-if="!group.children"
              :to="group.path"
              class="flex items-center gap-3 rounded-full px-4 py-2.5 text-sm text-muted hover:text-ink hover:bg-hover transition duration-150 mb-0.5"
              active-class="bg-brand-soft text-brand font-semibold"
            >
              <FeatherIcon :name="group.icon" class="h-4.5 w-4.5 flex-shrink-0" />
              <span class="truncate">{{ group.label }}</span>
            </router-link>

            <!-- Collapsible group -->
            <div v-else class="mb-0.5">
              <div
                @click="toggleGroup(group)"
                class="flex items-center justify-between rounded-full px-4 py-2.5 text-sm font-semibold transition cursor-pointer"
                :class="isGroupActive(group) ? 'text-brand bg-brand-soft/40' : 'text-muted hover:text-ink hover:bg-hover'"
              >
                <div class="flex items-center space-x-3">
                  <FeatherIcon :name="group.icon" class="h-4.5 w-4.5 flex-shrink-0" />
                  <span class="truncate">{{ group.label }}</span>
                </div>
                <FeatherIcon
                  :name="group.isOpen ? 'chevron-down' : 'chevron-right'"
                  class="h-3.5 w-3.5 text-faint flex-shrink-0 transition-transform duration-200"
                />
              </div>

              <!-- Children -->
              <div v-if="group.isOpen" class="pl-4 border-l border-divider/60 ml-6 mt-1 space-y-0.5 animate-fade-in">
                <router-link
                  v-for="child in group.children"
                  :key="child.label"
                  :to="child.path"
                  class="flex items-center gap-2 rounded-full px-4 py-2 text-[13px] text-muted hover:text-ink hover:bg-hover transition duration-150"
                  active-class="bg-brand-soft text-brand font-semibold"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-faint flex-shrink-0"
                    :class="{'bg-brand': route.path === child.path}"></div>
                  <span class="truncate">{{ child.label }}</span>
                </router-link>
              </div>
            </div>
          </template>

          <!-- Divider -->
          <div v-if="group.dividerAfter && isSidebarExpanded" class="my-2 border-t border-border"></div>
        </div>
      </nav>

      <!-- Footer User -->
      <div class="border-t border-border bg-paper overflow-hidden transition-all duration-300 p-4">
        <div class="flex items-center" :class="!isSidebarExpanded ? 'justify-center' : 'gap-3'">
          <div class="h-9 w-9 rounded-full bg-brand-soft text-brand flex items-center justify-center font-semibold text-[13px] ring-2 ring-brand/10 flex-shrink-0">
            AD
          </div>
          <transition name="fade-slide">
            <div v-if="isSidebarExpanded" class="min-w-0 flex-1 leading-tight">
              <div class="text-[13px] font-semibold text-ink truncate">Administrator</div>
              <div class="text-[11px] font-medium text-muted truncate">admin · erp</div>
            </div>
          </transition>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col overflow-hidden bg-canvas min-w-0">
      <header class="flex h-14 items-center border-b border-rose-200/60 px-6 flex-shrink-0 relative overflow-hidden" style="background: linear-gradient(135deg, #fdf2f4 0%, #fce7ec 40%, #fde8e8 70%, #fff0f0 100%)">
        <!-- Left: page title -->
        <div class="flex-1 min-w-0">
          <h1 class="ff-display text-[17px] font-bold text-ink truncate">{{ currentRouteName }}</h1>
        </div>

        <!-- Center: search trigger -->
        <div class="flex-1 flex justify-center">
          <button
            @click="paletteRef?.open()"
            class="flex items-center gap-3 px-4 py-2 rounded-full bg-paper border border-border text-[13px] text-muted hover:text-ink hover:border-brand/40 hover:shadow-sm transition-all duration-200 w-64 group"
          >
            <svg class="h-4 w-4 text-muted flex-shrink-0 group-hover:text-brand transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="flex-1 text-left text-xs text-muted group-hover:text-ink transition-colors">Tìm kiếm tính năng...</span>
            <kbd class="ml-auto text-[10px] scale-90 px-1.5 py-0.5 border border-border bg-hover rounded font-mono text-muted flex-shrink-0 group-hover:border-brand/30 group-hover:bg-brand-soft group-hover:text-brand transition-all">
              Ctrl K
            </kbd>
          </button>
        </div>

        <!-- Right: actions -->
        <div class="flex-1 flex justify-end items-center gap-3">
          <button
            @click="goToDesk"
            class="btn btn-ghost !px-3.5 !py-1.5 !text-xs !gap-2"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Vào Desk
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-hidden p-5">
        <router-view />
      </div>
    </main>

    <!-- AI Chat Bubble (global floating) -->
    <AIChatBubble />

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import CommandPalette from './components/CommandPalette.vue'
import AIChatBubble from './components/AIChatBubble.vue'

const route = useRoute()
const paletteRef = ref(null)
const collapsed = ref(false)
const isSidebarExpanded = computed(() => !collapsed.value)

const menuGroups = ref([
  // --- TỔNG QUAN ---
  { label: 'Dashboard', icon: 'home', path: '/' },

  // --- SALE & LEAD ---
  {
    label: 'Sale & Lead', icon: 'trending-up', isOpen: false,
    children: [
      { label: 'Lead tiềm năng', path: '/leads' },
      { label: 'CRM Pipeline', path: '/crm' },
      { label: 'Lịch hẹn', path: '/appointments' },
    ]
  },

  // --- HỌC VIÊN & THẺ ---
  {
    label: 'Học viên & Thẻ', icon: 'users', isOpen: false,
    children: [
      { label: 'Học viên', path: '/students' },
      { label: 'Thẻ', path: '/student-card' },
      { label: 'Onboarding', path: '/onboarding' },
    ]
  },

  // --- LỚP & ĐÀO TẠO ---
  {
    label: 'Lớp & Đào tạo', icon: 'book-open', isOpen: false,
    children: [
      { label: 'Hiệu suất', path: '/assessments' },
      { label: 'Lịch lớp', path: '/classes' },
      { label: 'Đăng ký lớp', path: '/enrollments' },
      { label: 'Chấm công & Điểm danh', path: '/attendance' },
      { label: 'Giáo viên', path: '/teachers' },
      { label: 'Khóa học', path: '/courses' },
    ]
  },

  // --- TÀI CHÍNH ---
  {
    label: 'Tài chính', icon: 'dollar-sign', isOpen: false,
    children: [
      { label: 'Hóa đơn', path: '/invoices' },
      { label: 'Phiếu thu', path: '/payments' },
    ]
  },

  // --- NHÂN SỰ & LƯƠNG ---
  {
    label: 'Nhân sự & Lương', icon: 'briefcase', isOpen: false,
    children: [
      { label: 'Nhân sự', path: '/' },
      { label: 'Bảng lương', path: '/' },
    ]
  },

  // --- VẬN HÀNH ---
  {
    label: 'Vận hành', icon: 'settings', isOpen: false,
    children: [
      { label: 'Thuê phòng', path: '/room-booking' },
    ]
  },

  // --- BUILD & LEAN ---
  {
    label: 'Build & Lean', icon: 'zap', isOpen: false,
    children: [
      { label: 'Viral Lab', path: '/' },
      { label: 'Task Board', path: '/task-board' },
    ]
  },
])

const toggleGroup = (group) => { group.isOpen = !group.isOpen }

const isGroupActive = (group) => {
  if (!group.children) return route.path === group.path
  return group.children.some(child => route.path === child.path)
}

// Tự động đóng/mở các phân hệ dựa vào route path
const syncGroupExpansion = () => {
  menuGroups.value.forEach(group => {
    if (group.children) {
      const hasActiveChild = group.children.some(child => route.path === child.path)
      group.isOpen = hasActiveChild
    }
  })
}

watch(() => route.path, () => {
  syncGroupExpansion()
}, { immediate: true })

const currentRouteName = computed(() => {
  const names = {
    '/': 'Bảng Điều Khiển',
    '/students': 'Quản Lý Học Viên',
    '/student-card': 'Thẻ Học Viên',
    '/leads': 'Danh Sách Lead',
    '/crm': 'Quản Lý Khách Hàng (CRM)',
    '/appointments': 'Lịch Hẹn Tư Vấn',
    '/onboarding': 'Quy Trình Nhập Học',
    '/teachers': 'Quản Lý Giáo Viên',
    '/courses': 'Quản Lý Khóa Học',
    '/classes': 'Quản Lý Lớp Học',
    '/enrollments': 'Đăng Ký Lớp Học',
    '/room-booking': 'Thuê Phòng Học',
    '/attendance': 'Điểm Danh Học Viên',
    '/assessments': 'Bảng Điểm Thi Cử',
    '/task-board': 'Giao Việc Nội Bộ',
    '/invoices': 'Quản Lý Hóa Đơn',
    '/payments': 'Lịch Sử Phiếu Thu',
  }
  return names[route.path] || ''
})

const goToDesk = () => { window.location.href = '/app' }
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
