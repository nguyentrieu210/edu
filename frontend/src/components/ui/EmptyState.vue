<template>
  <div class="flex flex-col items-center justify-center text-center py-14 px-6">
    <FeatherIcon :name="icon" class="h-8 w-8 text-faint mb-3" />
    <p class="text-sm font-medium text-ink">{{ title }}</p>
    <p v-if="description" class="text-xs text-muted mt-1 max-w-sm">{{ description }}</p>
    <button v-if="actionLabel && can" class="btn btn-brand mt-4" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

// Empty state (§10.2): icon 32px + tiêu đề ngắn + một câu + 1 action (nếu có quyền).
defineProps({
  icon: { type: String, default: 'inbox' },
  title: { type: String, default: 'Chưa có dữ liệu' },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  can: { type: Boolean, default: true },
})
defineEmits(['action'])
</script>
