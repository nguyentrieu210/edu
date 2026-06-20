<template>
  <div class="tl">
    <div v-if="!items.length" class="tl__empty">Chưa có hoạt động nào.</div>
    <div v-for="(it, i) in items" :key="it.name || i" class="tl__item">
      <div class="tl__rail">
        <span class="tl__dot" :style="{ background: KIND[it.kind]?.color || '#bd97a5' }">
          <FeatherIcon :name="KIND[it.kind]?.icon || 'circle'" style="width:11px;height:11px;" />
        </span>
        <span v-if="i < items.length - 1" class="tl__line" />
      </div>
      <div class="tl__body">
        <div class="tl__top">
          <span class="tl__title">{{ it.title }}</span>
          <SkBadge v-if="badge(it)" v-bind="badge(it)" />
        </div>
        <div v-if="it.detail" class="tl__detail">{{ it.detail }}</div>
        <div class="tl__foot">
          <span>{{ formatDate(it.date) }}</span>
          <span v-if="it.next_follow_up" class="tl__follow">↻ Theo dõi: {{ formatDate(it.next_follow_up) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { formatDate } from '../../utils/format'
import { statusMeta } from '../../utils/labels'
import SkBadge from '../ui/SkBadge.vue'

defineProps({ items: { type: Array, default: () => [] } })

const KIND = {
  consultation: { icon: 'message-circle', color: '#4a6fb5' },
  placement: { icon: 'edit-3', color: '#c98a2e' },
  appointment: { icon: 'calendar', color: '#e07a8f' },
}

const DT_BY_KIND = {
  appointment: 'Student Appointment',
  placement: 'Placement Test',
}

function badge(it) {
  if (!it.status) return null
  const dt = DT_BY_KIND[it.kind]
  return dt ? statusMeta(dt, 'status', it.status) : { label: it.status, variant: 'neutral' }
}
</script>

<style scoped>
.tl { display: flex; flex-direction: column; }
.tl__empty { font-size: 13px; color: #bd97a5; padding: 12px 0; text-align: center; }
.tl__item { display: flex; gap: 12px; }
.tl__rail { display: flex; flex-direction: column; align-items: center; flex: none; }
.tl__dot { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; flex: none; }
.tl__line { flex: 1; width: 2px; background: #f3d9e1; margin: 3px 0; min-height: 14px; }
.tl__body { flex: 1; min-width: 0; padding-bottom: 16px; }
.tl__top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.tl__title { font-size: 13px; font-weight: 600; color: #3d2530; }
.tl__detail { font-size: 12.5px; color: #7a5c68; margin-top: 4px; white-space: pre-wrap; word-break: break-word; }
.tl__foot { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 5px; font-size: 11px; color: #bd97a5; }
.tl__follow { color: #b8456a; }
</style>
