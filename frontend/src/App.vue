<template>
  <div class="flex h-screen font-sans antialiased overflow-hidden text-ink bg-canvas">

    <!-- Command Palette -->
    <CommandPalette ref="paletteRef" />

    <!-- ===================== PRIMARY SIDEBAR ===================== -->
    <aside
      class="flex flex-col flex-shrink-0 select-none transition-all duration-200 ease-out relative z-30"
      :class="isSidebarExpanded ? 'w-[240px]' : 'w-16'"
      style="background: var(--bg-sidebar); border-right: 1px solid var(--border);"
    >
      <!-- Brand -->
      <div class="flex items-center gap-2.5 overflow-hidden"
        :class="isSidebarExpanded ? 'px-3 pt-4 pb-3' : 'justify-center px-0 pt-4 pb-3'">
        <div class="flex-none flex items-center justify-center text-white font-bold"
          style="width:32px;height:32px;border-radius:7px;background:var(--brand);font-size:13px;letter-spacing:.5px;">
          IKE
        </div>
        <transition name="fade-slide">
          <div v-if="isSidebarExpanded" class="min-w-0 leading-tight">
            <div style="font-weight:600;font-size:14px;color:var(--ink);line-height:1.1;">Education ERP</div>
            <div style="font-size:11px;color:var(--muted);margin-top:2px;">日本語 · IKE Ohashi</div>
          </div>
        </transition>
      </div>

      <!-- Collapse toggle -->
      <button
        @click="collapsed = !collapsed"
        class="absolute -right-3 top-14 z-10 w-6 h-6 rounded-full flex items-center justify-center transition-colors"
        style="background:#fff;border:1px solid var(--border);"
        :aria-label="collapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'"
      >
        <FeatherIcon :name="collapsed ? 'chevron-right' : 'chevron-left'" class="h-3.5 w-3.5" style="color:var(--muted);" />
      </button>

      <!-- Quick actions -->
      <div class="flex flex-col gap-2" :class="isSidebarExpanded ? 'px-2.5 pb-2 pt-1' : 'px-2 pb-2 pt-1'">
        <button
          @click="paletteRef?.open()"
          class="flex items-center justify-center gap-2 btn-ghost press"
          :class="isSidebarExpanded ? 'h-[38px] px-3' : 'h-10 w-10 mx-auto'"
          style="border-radius:6px;font-size:14px;font-weight:500;"
        >
          <FeatherIcon name="plus" class="h-[17px] w-[17px]" />
          <span v-if="isSidebarExpanded">Tạo mới</span>
        </button>
        <button
          v-if="isSidebarExpanded"
          @click="paletteRef?.open()"
          class="flex items-center gap-2 h-9 px-2.5 w-full transition-colors"
          style="border-radius:6px;background:#fff;border:1px solid var(--border);"
        >
          <FeatherIcon name="search" class="h-[15px] w-[15px]" style="color:var(--muted);" />
          <span style="font-size:13px;color:var(--muted);">Tìm kiếm</span>
          <span class="ml-auto" style="font-size:11px;color:var(--faint);border:1px solid var(--border);border-radius:5px;padding:1px 5px;">Ctrl K</span>
        </button>
      </div>

      <!-- Navigation -->
      <nav class="sk-scroll flex-1 overflow-y-auto" :class="isSidebarExpanded ? 'px-2.5 pb-3' : 'px-2 pb-3'">
        <template v-for="(section, sIdx) in menu" :key="sIdx">
          <div v-if="section.label && isSidebarExpanded" class="eyebrow" style="padding:14px 8px 6px;">
            {{ section.label }}
          </div>
          <div v-else-if="section.label && sIdx > 0" class="my-2 mx-2" style="border-top:1px solid var(--border);"></div>

          <router-link
            v-for="item in section.items"
            :key="item.path"
            :to="item.path"
            class="group relative flex items-center transition-colors duration-100 rounded-md"
            :class="[
              isSidebarExpanded ? 'gap-2.5 h-9 px-2.5 mb-0.5' : 'justify-center h-10 w-10 mx-auto mb-1',
              isActive(item.path) ? 'font-semibold' : 'font-medium',
            ]"
            :style="navStyle(item.path)"
            :title="!isSidebarExpanded ? item.label : null"
          >
            <FeatherIcon :name="item.icon" class="flex-none" :class="isSidebarExpanded ? 'h-[18px] w-[18px]' : 'h-5 w-5'" />
            <span v-if="isSidebarExpanded" class="truncate" style="font-size:14px;">{{ item.label }}</span>
            <span v-if="!isSidebarExpanded"
              class="absolute left-full ml-2 px-2.5 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50"
              style="background:var(--ink);color:#fff;font-size:12px;font-weight:500;box-shadow:var(--shadow-menu);">
              {{ item.label }}
            </span>
          </router-link>
        </template>

        <!-- AI Assistant -->
        <button
          @click="openAi"
          class="flex items-center transition-colors mt-2 rounded-md"
          :class="isSidebarExpanded ? 'gap-2.5 h-9 px-2.5 w-full' : 'justify-center h-10 w-10 mx-auto'"
          style="background:transparent;color:var(--ink-2);font-size:14px;font-weight:500;"
          onmouseover="this.style.background='var(--hover)'" onmouseout="this.style.background='transparent'"
        >
          <FeatherIcon name="zap" class="flex-none h-[18px] w-[18px]" />
          <span v-if="isSidebarExpanded">AI Assistant</span>
        </button>
      </nav>

      <!-- User -->
      <div class="flex items-center gap-2.5" style="border-top:1px solid var(--border);"
        :class="isSidebarExpanded ? 'px-3 py-2.5' : 'px-2 py-2.5 justify-center'">
        <div class="flex-none flex items-center justify-center font-semibold text-white"
          style="width:32px;height:32px;border-radius:50%;background:var(--brand);font-size:12px;">
          {{ userInitials }}
        </div>
        <div v-if="isSidebarExpanded" class="flex-1 min-w-0 leading-tight">
          <div style="font-size:13px;font-weight:600;color:var(--ink);" class="truncate">{{ userName }}</div>
          <div style="font-size:11px;color:var(--muted);" class="truncate">{{ userId }}</div>
        </div>
      </div>
    </aside>

    <!-- ===================== MAIN ===================== -->
    <main class="flex flex-1 flex-col overflow-hidden min-w-0 bg-paper">
      <header class="flex items-center gap-3 flex-shrink-0 px-6"
        style="height:56px;border-bottom:1px solid var(--border);background:var(--paper);">
        <div class="min-w-0">
          <h1 class="truncate" style="font-size:16px;font-weight:600;color:var(--ink);">{{ currentRouteName }}</h1>
        </div>
        <span class="hidden md:inline" style="font-size:13px;color:var(--muted);">· {{ todayLabel }}</span>

        <div class="ml-auto flex items-center gap-2">
          <button
            @click="paletteRef?.open()"
            class="md:hidden flex items-center justify-center"
            style="width:34px;height:34px;border:1px solid var(--border);background:#fff;border-radius:6px;color:var(--ink-2);"
            aria-label="Tìm kiếm"
          >
            <FeatherIcon name="search" class="h-4 w-4" />
          </button>
          <button @click="goToDesk" class="btn btn-ghost press" style="height:34px;">
            <FeatherIcon name="external-link" class="h-3.5 w-3.5" />
            Vào Desk
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-hidden p-5">
        <router-view />
      </div>
    </main>

    <!-- AI Chat Bubble (global floating) -->
    <AIChatBubble ref="aiBubbleRef" />

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import CommandPalette from './components/CommandPalette.vue'
import AIChatBubble from './components/AIChatBubble.vue'

const route = useRoute()
const paletteRef = ref(null)
const aiBubbleRef = ref(null)
const collapsed = ref(false)
const isSidebarExpanded = computed(() => !collapsed.value)

// Người dùng lấy từ boot session, không hardcode (§12.2).
const boot = typeof window !== 'undefined' ? window.frappe?.boot : null
const userId = boot?.user?.name || boot?.sitename || window.frappe?.session?.user || ''
const userName = computed(() => {
  const info = boot?.user_info?.[userId]
  return info?.fullname || boot?.user?.full_name || userId || 'Người dùng'
})
const userInitials = computed(() => {
  const n = (userName.value || 'U').trim()
  const parts = n.split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase() || 'U'
})

// Sidebar phẳng theo nhóm — neutral palette, icon Feather (tương thích Lucide).
const menu = ref([
  {
    label: '',
    items: [
      { label: 'Dashboard', icon: 'grid', path: '/' },
    ],
  },
  {
    label: 'Tuyển sinh & học viên',
    items: [
      { label: 'Tuyển sinh', icon: 'user-plus', path: '/leads' },
      { label: 'CRM Pipeline', icon: 'trending-up', path: '/crm' },
      { label: 'Lịch hẹn', icon: 'phone', path: '/appointments' },
      { label: 'Học viên', icon: 'users', path: '/students' },
      { label: 'Thẻ học viên', icon: 'credit-card', path: '/student-card' },
      { label: 'Onboarding', icon: 'check-square', path: '/onboarding' },
    ],
  },
  {
    label: 'Đào tạo',
    items: [
      { label: 'Lớp học', icon: 'book-open', path: '/classes' },
      { label: 'Khóa học', icon: 'book', path: '/courses' },
      { label: 'Giáo viên', icon: 'award', path: '/teachers' },
      { label: 'Chương trình & Giáo án', icon: 'layers', path: '/curriculum' },
      { label: 'Bài tập & Tài liệu', icon: 'file-text', path: '/homework' },
      { label: 'Đăng ký lớp', icon: 'clipboard', path: '/enrollments' },
      { label: 'Điểm danh', icon: 'check-circle', path: '/attendance' },
      { label: 'Hiệu suất', icon: 'bar-chart-2', path: '/assessments' },
    ],
  },
  {
    label: 'Tài chính',
    items: [
      { label: 'Hóa đơn', icon: 'file-text', path: '/invoices' },
      { label: 'Phiếu thu', icon: 'dollar-sign', path: '/payments' },
    ],
  },
  {
    label: 'Vận hành',
    items: [
      { label: 'Thuê phòng', icon: 'map-pin', path: '/room-booking' },
      { label: 'Task Board', icon: 'list', path: '/task-board' },
    ],
  },
  {
    label: 'Cổng truy cập',
    items: [
      { label: 'Cổng giáo viên', icon: 'briefcase', path: '/teacher-portal' },
      { label: 'Cổng học viên', icon: 'smartphone', path: '/student-portal' },
    ],
  },
])

const isActive = (path) => (path === '/' ? route.path === '/' : route.path.startsWith(path))

// Active = nền chữ nhật bo nhẹ (neutral-200), không pill, không thanh đỏ bên trái (§3.2).
const navStyle = (path) => {
  const active = isActive(path)
  return {
    cursor: 'pointer',
    color: active ? 'var(--ink)' : 'var(--ink-2)',
    background: active ? 'var(--active)' : 'transparent',
  }
}

const openAi = () => {
  if (aiBubbleRef.value?.open) aiBubbleRef.value.open()
}

const currentRouteName = computed(() => {
  const names = {
    '/': 'Bảng điều khiển',
    '/students': 'Học viên',
    '/student-card': 'Thẻ học viên',
    '/leads': 'Tuyển sinh',
    '/crm': 'CRM Pipeline',
    '/appointments': 'Lịch hẹn tư vấn',
    '/onboarding': 'Quy trình nhập học',
    '/teachers': 'Giáo viên',
    '/courses': 'Khóa học',
    '/classes': 'Lớp học',
    '/enrollments': 'Đăng ký lớp học',
    '/curriculum': 'Chương trình & Giáo án',
    '/homework': 'Bài tập & Tài liệu',
    '/teacher-portal': 'Cổng giáo viên',
    '/student-portal': 'Cổng học viên',
    '/room-booking': 'Thuê phòng học',
    '/attendance': 'Điểm danh',
    '/assessments': 'Điểm số & Hiệu suất',
    '/task-board': 'Giao việc nội bộ',
    '/invoices': 'Hóa đơn',
    '/payments': 'Phiếu thu',
  }
  // Khớp prefix để route con (detail) vẫn có tiêu đề.
  const exact = names[route.path]
  if (exact) return exact
  const hit = Object.keys(names)
    .filter((p) => p !== '/' && route.path.startsWith(p))
    .sort((a, b) => b.length - a.length)[0]
  return hit ? names[hit] : ''
})

const todayLabel = computed(() => {
  const d = new Date()
  const days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy']
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  return `${days[d.getDay()]}, ${dd}/${mm}/${d.getFullYear()}`
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
