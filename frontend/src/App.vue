<template>
  <div class="sk-app">
    <!-- ===================== PRIMARY SIDEBAR ===================== -->
    <aside class="sk-side">
      <!-- brand -->
      <div class="sk-brand">
        <div class="sk-brand__logo">
          <svg width="26" height="26" viewBox="0 0 64 64">
            <g fill="#fff">
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(0 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(72 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(144 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(216 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(288 32 32)" />
            </g>
            <circle cx="32" cy="32" r="4.4" fill="#ffd98e" />
          </svg>
        </div>
        <div class="sk-brand__txt">
          <div class="sk-brand__name font-display">IKE Ohashi</div>
          <div class="sk-brand__sub">日本語 · Education ERP</div>
        </div>
      </div>

      <!-- quick actions -->
      <div class="sk-quick">
        <SkButton variant="solid" block left-icon="plus">Tạo mới</SkButton>
      </div>

      <!-- nav -->
      <nav class="sk-nav sk-scroll">
        <template v-for="(section, si) in sections" :key="si">
          <div v-if="section.label" class="eyebrow sk-nav__group">{{ section.label }}</div>
          <router-link
            v-for="item in section.items"
            :key="item.path"
            :to="item.path"
            class="sk-nav__item"
            :class="{ 'sk-nav__item--active': isActive(item.path) }"
          >
            <FeatherIcon :name="item.icon" style="width:18px;height:18px;" />
            <span>{{ item.label }}</span>
            <span v-if="item.badge" class="sk-nav__badge">{{ item.badge }}</span>
          </router-link>
        </template>
      </nav>

      <!-- user -->
      <div class="sk-user">
        <SkAvatar :name="userName" :size="34" />
        <div class="sk-user__info">
          <div class="sk-user__name">{{ userName }}</div>
          <div class="sk-user__role">{{ userRole }}</div>
        </div>
        <button class="sk-user__btn" aria-label="Cài đặt" @click="goToDesk">
          <FeatherIcon name="settings" style="width:17px;height:17px;" />
        </button>
      </div>
    </aside>

    <!-- ===================== WORKSPACE ===================== -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Ô tìm kiếm canh giữa, nổi trên dải tiêu đề của trang -->
    <button class="sk-topsearch" @click="palette?.open()">
      <FeatherIcon name="search" style="width:15px;height:15px;color:#bd8d9c;" />
      <span>Tìm kiếm học viên, lớp, hóa đơn…</span>
      <span class="sk-search__kbd">⌘K</span>
    </button>

    <!-- ===================== GLOBAL OVERLAYS ===================== -->
    <CommandPalette ref="palette" />
    <AIDrawer ref="aiDrawer" />
    <SkToaster />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { NAV_SECTIONS } from './router'
import SkButton from './components/ui/SkButton.vue'
import SkAvatar from './components/ui/SkAvatar.vue'
import CommandPalette from './components/CommandPalette.vue'
import AIDrawer from './components/AIDrawer.vue'
import SkToaster from './components/ui/SkToaster.vue'

const route = useRoute()
const palette = ref(null)
const aiDrawer = ref(null)
const sections = NAV_SECTIONS

const isActive = (path) => (path === '/' ? route.path === '/' : route.path.startsWith(path))

// Người dùng từ boot session (không hardcode).
const boot = typeof window !== 'undefined' ? window.frappe?.boot : null
const userId = boot?.user?.name || window.frappe?.session?.user || ''
const userName = computed(() => boot?.user_info?.[userId]?.fullname || boot?.user?.full_name || userId || 'Người dùng')
const userRole = computed(() => {
  const roles = boot?.user?.roles || []
  if (roles.includes('Academic Manager') || roles.includes('System Manager')) return 'Giáo vụ'
  if (roles.includes('Teacher')) return 'Giáo viên'
  if (roles.includes('Student')) return 'Học viên'
  return 'Người dùng'
})

const goToDesk = () => { window.location.href = '/app' }

// Phím tắt: ⌘K mở palette, Esc đóng overlay.
function onKey(e) {
  if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault()
    palette.value?.toggle()
  } else if (e.key === 'Escape') {
    palette.value?.close()
    aiDrawer.value?.close()
  }
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.sk-app {
  height: 100vh; width: 100vw; display: flex; overflow: hidden;
  background: linear-gradient(140deg, #fff7fa 0%, #fdedf3 48%, #fbe4ee 100%);
  color: #3d2530; font-size: 14px;
}

/* Ô tìm kiếm canh giữa, nổi trên dải tiêu đề của trang (bên phải sidebar 250px) */
.sk-topsearch { position: fixed; top: 10px; left: calc(50vw + 125px); transform: translateX(-50%); z-index: 50; display: flex; align-items: center; gap: 8px; height: 36px; width: min(440px, 32vw); padding: 0 11px; border-radius: 9px; background: rgba(255, 255, 255, 0.9); border: 1px solid #f1d2de; cursor: pointer; font-family: inherit; box-shadow: 0 2px 10px rgba(180, 80, 120, 0.12); backdrop-filter: blur(4px); }
.sk-topsearch:hover { background: #fff; }
.sk-topsearch > span { font-size: 13px; color: #bd8d9c; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* sidebar */
.sk-side { flex: none; width: 250px; display: flex; flex-direction: column; background: linear-gradient(185deg, #fdeef4 0%, #fce0ea 100%); border-right: 1px solid #f2d4df; }
.sk-brand { display: flex; align-items: center; gap: 11px; padding: 16px 16px 14px; }
.sk-brand__logo { flex: none; width: 40px; height: 40px; border-radius: 11px; background: linear-gradient(140deg, #f7a8c4, #d6557e); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(214, 85, 126, 0.32); }
.sk-brand__name { font-weight: 900; font-size: 19px; letter-spacing: 0.5px; color: #4a2230; line-height: 1; }
.sk-brand__sub { font-size: 10.5px; color: #b07e90; margin-top: 3px; font-weight: 500; }

.sk-quick { padding: 2px 12px 10px; display: flex; flex-direction: column; gap: 9px; }
.sk-search { display: flex; align-items: center; gap: 8px; height: 36px; padding: 0 11px; border-radius: 8px; background: rgba(255, 255, 255, 0.7); border: 1px solid #f1d2de; cursor: pointer; font-family: inherit; width: 100%; }
.sk-search:hover { background: #fff; }
.sk-search span { font-size: 13px; color: #bd8d9c; }
.sk-search__kbd { margin-left: auto; font-size: 10.5px !important; color: #caa6b4 !important; border: 1px solid #ecd0da; border-radius: 5px; padding: 1px 5px; }

.sk-nav { flex: 1; overflow-y: auto; padding: 6px 12px 12px; }
.sk-nav__group { padding: 14px 10px 6px; }
.sk-nav__item { display: flex; align-items: center; gap: 11px; height: 36px; width: 100%; padding: 0 10px; border: none; border-radius: 8px; cursor: pointer; font-family: inherit; text-align: left; color: #7a5c68; background: transparent; border-left: 3px solid transparent; font-size: 13.5px; font-weight: 500; margin-bottom: 2px; text-decoration: none; transition: background 0.12s ease; }
.sk-nav__item:hover { background: rgba(255, 255, 255, 0.55); }
.sk-nav__item--active { background: #fbd9e5; color: #a8345f; border-left-color: #d6557e; font-weight: 600; }
.sk-nav__badge { margin-left: auto; font-size: 11px; font-weight: 600; color: #b8456a; background: rgba(255, 255, 255, 0.7); border-radius: 6px; padding: 1px 7px; }
.sk-nav__ai { margin-top: 8px; color: #7a5c68; }

.sk-user { border-top: 1px solid #f2d4df; padding: 10px 12px; display: flex; align-items: center; gap: 10px; }
.sk-user__info { flex: 1; min-width: 0; }
.sk-user__name { font-size: 13px; font-weight: 600; color: #4a2230; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sk-user__role { font-size: 11px; color: #b07e90; }
.sk-user__btn { flex: none; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: none; background: none; border-radius: 7px; cursor: pointer; color: #b07e90; }
.sk-user__btn:hover { background: rgba(255, 255, 255, 0.6); }
</style>
