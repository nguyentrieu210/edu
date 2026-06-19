<template>
  <div class="space-y-2.5">
    <div
      v-for="i in rows"
      :key="i"
      class="animate-pulse rounded bg-hover"
      :style="{ height: height, width: rows > 1 && i === rows ? '60%' : width }"
    />
  </div>
</template>

<script setup>
// Skeleton (§10.1) — đúng kích thước nội dung, không spinner toàn màn hình cho list/detail.
defineProps({
  rows: { type: Number, default: 4 },
  height: { type: String, default: '16px' },
  width: { type: String, default: '100%' },
})
</script>
