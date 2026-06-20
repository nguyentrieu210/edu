<template>
  <!-- loading: skeleton -->
  <div v-if="state === 'loading'" class="sk-state-skel" :style="{ padding: pad }">
    <div class="sk-skel" style="height:14px;width:60%;" />
    <div class="sk-skel" style="height:14px;width:90%;" />
    <div class="sk-skel" style="height:14px;width:75%;" />
    <div class="sk-skel" style="height:14px;width:45%;" />
  </div>

  <!-- empty / error / denied -->
  <div v-else class="sk-state" :class="{ 'sk-state--error': state === 'error' }">
    <FeatherIcon :name="icon" class="sk-state__icon" :style="{ color: iconColor }" />
    <div class="sk-state__title" :style="{ color: titleColor }">{{ title }}</div>
    <div class="sk-state__desc">{{ message }}</div>
    <SkButton v-if="actionLabel" :variant="state === 'error' ? 'danger' : 'secondary'" size="md" class="mt-1" @click="$emit('action')">
      {{ actionLabel }}
    </SkButton>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import SkButton from './SkButton.vue'

const props = defineProps({
  state: { type: String, default: 'empty' }, // loading | empty | error | denied
  title: String,
  message: String,
  actionLabel: String,
  pad: { type: String, default: '26px' },
})
defineEmits(['action'])

const icon = computed(() => ({ empty: 'inbox', error: 'alert-circle', denied: 'lock' }[props.state] || 'inbox'))
const iconColor = computed(() => ({ empty: '#cf9bab', error: '#c44a3f', denied: '#a98c98' }[props.state] || '#cf9bab'))
const titleColor = computed(() => (props.state === 'error' ? '#b03b31' : '#3d2530'))
</script>

<style scoped>
.sk-state-skel { display: flex; flex-direction: column; gap: 12px; }
.sk-state {
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 9px;
  padding: 36px 26px;
}
.sk-state--error { background: #fdeeec; border-radius: 12px; }
.sk-state__icon { width: 30px; height: 30px; }
.sk-state__title { font-size: 14px; font-weight: 600; }
.sk-state__desc { font-size: 12.5px; color: #a98c98; max-width: 280px; }
.mt-1 { margin-top: 6px; }
</style>
