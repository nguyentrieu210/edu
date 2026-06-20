<template>
  <teleport to="body">
    <div class="sk-toaster">
      <transition-group name="toast">
        <div v-for="t in toasts" :key="t.id" class="sk-toast">
          <span class="sk-toast__ic" :style="iconWrap(t.type)">
            <FeatherIcon :name="iconName(t.type)" :style="{ width: '15px', height: '15px', color: iconColor(t.type) }" />
          </span>
          <div class="sk-toast__body">
            <div class="sk-toast__title">{{ t.title }}</div>
            <div v-if="t.detail" class="sk-toast__detail">{{ t.detail }}</div>
          </div>
          <button class="sk-toast__x" aria-label="Đóng" @click="dismiss(t.id)">
            <FeatherIcon name="x" style="width:15px;height:15px;" />
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { toasts, dismiss } from '../../utils/toast'

const MAP = {
  success: { bg: '#e4f3ea', color: '#2f8a5d', icon: 'check' },
  error: { bg: '#fbe0dd', color: '#c44a3f', icon: 'alert-circle' },
  info: { bg: '#e7eefb', color: '#4a6fb5', icon: 'info' },
}
const iconName = (t) => (MAP[t] || MAP.info).icon
const iconColor = (t) => (MAP[t] || MAP.info).color
const iconWrap = (t) => ({ background: (MAP[t] || MAP.info).bg })
</script>

<style scoped>
.sk-toaster { position: fixed; right: 24px; bottom: 24px; z-index: 70; display: flex; flex-direction: column; gap: 10px; }
.sk-toast {
  display: flex; align-items: center; gap: 11px;
  background: #fffdfe; border: 1px solid #f0c4d4; border-radius: 11px;
  padding: 13px 16px; box-shadow: 0 12px 32px rgba(160, 60, 100, 0.2);
  min-width: 280px; max-width: 380px; animation: sktoast 0.25s ease;
}
.sk-toast__ic { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex: none; }
.sk-toast__body { flex: 1; min-width: 0; }
.sk-toast__title { font-size: 13px; font-weight: 600; color: #3d2530; }
.sk-toast__detail { font-size: 11.5px; color: #a98c98; margin-top: 1px; }
.sk-toast__x { width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; border: none; background: none; border-radius: 6px; cursor: pointer; color: #b07e90; flex: none; }
.sk-toast__x:hover { background: #fbe6ee; }
.toast-enter-from { opacity: 0; transform: translateY(16px); }
.toast-leave-to { opacity: 0; transform: translateX(16px); }
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
</style>
