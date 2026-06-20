<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="modelValue" class="sk-drawer__overlay" @click="close">
        <div class="sk-drawer" :style="{ width: width }" @click.stop>
          <div class="sk-drawer__head">
            <span class="sk-drawer__title">{{ title }}</span>
            <button class="sk-drawer__x" aria-label="Đóng" @click="close">
              <FeatherIcon name="x" style="width:18px;height:18px;" />
            </button>
          </div>
          <div class="sk-drawer__body sk-scroll">
            <slot />
          </div>
          <div v-if="$slots.footer" class="sk-drawer__foot">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  modelValue: Boolean,
  title: String,
  width: { type: String, default: '420px' },
})
const emit = defineEmits(['update:modelValue', 'close'])
function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped>
.sk-drawer__overlay { position: fixed; inset: 0; z-index: 60; background: rgba(60, 20, 35, 0.28); backdrop-filter: blur(2px); display: flex; justify-content: flex-end; }
.sk-drawer { max-width: 92%; height: 100%; background: #fffdfe; box-shadow: -12px 0 40px rgba(80, 30, 50, 0.22); display: flex; flex-direction: column; animation: skpop 0.22s ease; }
.sk-drawer__head { height: 56px; flex: none; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid #f1dbe3; }
.sk-drawer__title { font-size: 15px; font-weight: 600; color: #3d2530; }
.sk-drawer__x { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: none; background: none; border-radius: 7px; cursor: pointer; color: #b07e90; }
.sk-drawer__x:hover { background: #fbe6ee; }
.sk-drawer__body { flex: 1; overflow-y: auto; padding: 20px; }
.sk-drawer__foot { flex: none; padding: 14px 20px; border-top: 1px solid #f1dbe3; background: #fffafb; }
</style>
