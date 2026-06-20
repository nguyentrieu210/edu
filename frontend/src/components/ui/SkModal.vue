<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="modelValue" class="sk-modal__overlay" @click="close">
        <div class="sk-modal" :style="{ width: width }" @click.stop>
          <div class="sk-modal__head">
            <span class="sk-modal__title">{{ title }}</span>
            <button class="sk-modal__x" aria-label="Đóng" @click="close">
              <FeatherIcon name="x" style="width:17px;height:17px;" />
            </button>
          </div>
          <div class="sk-modal__body sk-scroll">
            <slot />
          </div>
          <div v-if="$slots.footer" class="sk-modal__foot">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  width: { type: String, default: '460px' },
})
const emit = defineEmits(['update:modelValue', 'close'])
function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped>
.sk-modal__overlay {
  position: fixed; inset: 0; z-index: 60;
  background: rgba(60, 20, 35, 0.32); backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center; padding: 16px;
}
.sk-modal {
  max-width: 92%; background: #fffdfe; border-radius: 14px;
  box-shadow: 0 24px 60px rgba(80, 30, 50, 0.35); overflow: hidden;
  animation: skpop 0.2s ease; display: flex; flex-direction: column; max-height: 88vh;
}
.sk-modal__head { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid #f4dde5; }
.sk-modal__title { font-size: 15px; font-weight: 600; color: #3d2530; }
.sk-modal__x { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: none; background: none; border-radius: 7px; cursor: pointer; color: #b07e90; }
.sk-modal__x:hover { background: #fbe6ee; }
.sk-modal__body { padding: 20px; overflow-y: auto; }
.sk-modal__foot { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px; border-top: 1px solid #f4dde5; background: #fffafb; }
</style>
