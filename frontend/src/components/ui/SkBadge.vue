<template>
  <span class="sk-badge" :style="style">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

// variant theo labels.js: success | info | warning | danger | neutral
const VARIANTS = {
  success: { bg: '#e4f3ea', color: '#2f8a5d' },
  info: { bg: '#e7eefb', color: '#4a6fb5' },
  warning: { bg: '#fbe6cf', color: '#b07a1f' },
  danger: { bg: '#fbe0dd', color: '#c44a3f' },
  neutral: { bg: '#eef0f4', color: '#7a7986' },
  sakura: { bg: '#fbdce7', color: '#b8456a' },
}

const props = defineProps({
  label: String,
  variant: { type: String, default: 'neutral' },
})

const style = computed(() => {
  const v = VARIANTS[props.variant] || VARIANTS.neutral
  return { background: v.bg, color: v.color }
})
</script>

<style scoped>
.sk-badge {
  display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 600; line-height: 1;
  padding: 3px 9px; border-radius: 5px; white-space: nowrap;
}
</style>
