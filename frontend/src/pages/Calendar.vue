<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Lịch học</span>
      <span class="ws-head__sub">Tuần {{ rangeLabel }}</span>
      <div class="ws-head__actions">
        <SkButton variant="secondary" size="sm" @click="shift(-7)">← Trước</SkButton>
        <SkButton variant="secondary" size="sm" @click="shift(0)">Hôm nay</SkButton>
        <SkButton variant="secondary" size="sm" @click="shift(7)">Sau →</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="error" title="Không tải được lịch" :message="error" action-label="Thử lại" @action="load" />

      <div v-else class="cal">
        <div v-for="d in days" :key="d.iso" class="cal-day">
          <div class="cal-day__head">
            <span class="cal-day__label" :style="{ color: d.today ? '#b8456a' : '#7a5c68' }">{{ d.label }}</span>
            <span class="cal-day__date tnum">{{ d.dd }}</span>
          </div>
          <div class="cal-day__body" :style="{ background: d.today ? '#fdf2f6' : 'transparent' }">
            <div v-for="e in d.events" :key="e.name" class="cal-ev" :style="{ background: bg(e.class_id), borderLeftColor: accent(e.class_id) }">
              <div class="cal-ev__time tnum" :style="{ color: accent(e.class_id) }">{{ formatTime(e.start_time) }}</div>
              <div class="cal-ev__klass">{{ e.class_name || e.class_id }}</div>
              <div class="cal-ev__room">{{ e.classroom_name || e.classroom || '—' }}</div>
            </div>
            <div v-if="!d.events.length" class="cal-day__empty">—</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '../api'
import { formatTime, formatDate } from '../utils/format'
import SkButton from '../components/ui/SkButton.vue'
import SkState from '../components/ui/SkState.vue'

const loading = ref(true)
const error = ref('')
const sessions = ref([])
const anchor = ref(new Date()) // ngày bất kỳ trong tuần đang xem

const DAY_LABELS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

function mondayOf(date) {
  const d = new Date(date)
  const wd = (d.getDay() + 6) % 7 // 0 = Monday
  d.setDate(d.getDate() - wd)
  d.setHours(0, 0, 0, 0)
  return d
}
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const weekStart = computed(() => mondayOf(anchor.value))
const weekDates = computed(() => Array.from({ length: 7 }, (_, i) => {
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() + i)
  return d
}))

const todayIso = iso(new Date())
const days = computed(() =>
  weekDates.value.map((d, i) => {
    const key = iso(d)
    return {
      iso: key,
      label: DAY_LABELS[i],
      dd: String(d.getDate()).padStart(2, '0'),
      today: key === todayIso,
      events: sessions.value.filter((s) => s.session_date === key),
    }
  }),
)
const rangeLabel = computed(() => `${formatDate(weekDates.value[0])} – ${formatDate(weekDates.value[6])}`)

const ACCENT = ['#d6557e', '#9b6fc4', '#3f9b6e', '#e07a8f', '#4a6fb5']
const BG = { '#d6557e': '#fdeef4', '#9b6fc4': '#f3edfb', '#3f9b6e': '#e9f6ef', '#e07a8f': '#fdf0f4', '#4a6fb5': '#eef2fb' }
function accent(key) {
  let h = 0
  for (const c of String(key || '')) h = (h * 31 + c.charCodeAt(0)) % 997
  return ACCENT[h % ACCENT.length]
}
const bg = (key) => BG[accent(key)] || '#fdeef4'

function shift(delta) {
  if (delta === 0) anchor.value = new Date()
  else { const d = new Date(anchor.value); d.setDate(d.getDate() + delta); anchor.value = d }
  load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    sessions.value = (await call('get_sessions_by_range', {
      from_date: iso(weekDates.value[0]),
      to_date: iso(weekDates.value[6]),
    })) || []
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.ws { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; height: 100vh; }
.ws-head { height: 56px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 24px; border-bottom: 1px solid #f1dbe3; }
.ws-head__title { font-size: 16px; font-weight: 600; color: #3d2530; }
.ws-head__sub { font-size: 13px; color: #a98c98; }
.ws-head__actions { margin-left: auto; display: flex; gap: 6px; align-items: center; }
.ws-body { flex: 1; overflow: auto; padding: 18px 24px; }

.cal { display: grid; grid-template-columns: repeat(7, minmax(150px, 1fr)); gap: 12px; min-width: max-content; }
.cal-day__head { display: flex; align-items: baseline; gap: 6px; padding: 0 2px 10px; }
.cal-day__label { font-size: 12.5px; font-weight: 600; }
.cal-day__date { font-size: 12.5px; color: #bd97a5; }
.cal-day__body { display: flex; flex-direction: column; gap: 8px; min-height: 120px; border-radius: 10px; padding: 8px; }
.cal-day__empty { font-size: 12px; color: #cbb0bb; text-align: center; padding-top: 8px; }
.cal-ev { border-radius: 8px; padding: 8px 10px; border-left: 3px solid; }
.cal-ev__time { font-size: 11.5px; font-weight: 600; }
.cal-ev__klass { font-size: 12.5px; font-weight: 500; color: #3d2530; margin-top: 2px; }
.cal-ev__room { font-size: 11px; color: #a98c98; }
</style>
