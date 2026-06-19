<template>
  <div class="flex flex-col items-center justify-center text-center py-14 px-6">
    <FeatherIcon :name="icon" class="h-8 w-8 text-rose mb-3" />
    <p class="text-sm font-medium text-ink">{{ title }}</p>
    <p v-if="message" class="text-xs text-muted mt-1 max-w-sm">{{ message }}</p>
    <button v-if="retryable" class="btn btn-ghost mt-4" @click="$emit('retry')">Thử lại</button>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

// Error state (§10.3). 403 dùng icon 'lock' + message quyền (§10.4).
defineProps({
  icon: { type: String, default: 'alert-triangle' },
  title: { type: String, default: 'Không tải được dữ liệu' },
  message: { type: String, default: '' },
  retryable: { type: Boolean, default: true },
})
defineEmits(['retry'])
</script>
