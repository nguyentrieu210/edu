<template>
  <span class="av sk-av-wrap">
    <img v-if="src" class="sk-av sk-av--img" :src="src" :style="style" :alt="name" />
    <span v-else class="sk-av" :style="style">{{ initials }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const GRADIENTS = [
  'linear-gradient(135deg,#f7a8c4,#d6557e)',
  'linear-gradient(135deg,#f6b8a0,#e07a8f)',
  'linear-gradient(135deg,#c9a6e0,#9b6fc4)',
  'linear-gradient(135deg,#f5a3b8,#cf5b86)',
  'linear-gradient(135deg,#f0b27a,#d97b6a)',
]

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 38 },
  src: { type: String, default: '' },
})

const initials = computed(() => {
  const n = (props.name || '?').trim()
  if (!n) return '?'
  const p = n.split(/\s+/)
  return ((p[0]?.[0] || '') + (p.length > 1 ? p[p.length - 1][0] : '')).toUpperCase()
})

const style = computed(() => {
  // chọn gradient ổn định theo tên
  let h = 0
  for (const c of (props.name || '')) h = (h * 31 + c.charCodeAt(0)) % 997
  const g = GRADIENTS[h % GRADIENTS.length]
  return {
    width: `${props.size}px`,
    height: `${props.size}px`,
    background: g,
    fontSize: `${Math.round(props.size * 0.38)}px`,
  }
})
</script>

<style scoped>
.sk-av-wrap { flex: none; display: inline-flex; }
.sk-av {
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; color: #fff; font-weight: 600; line-height: 1;
}
.sk-av--img { object-fit: cover; background: #f3d9e1; }
</style>
