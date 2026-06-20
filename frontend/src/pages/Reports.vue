<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Báo cáo</span>
      <span class="ws-head__sub">{{ monthLabel }}</span>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="error" title="Không tải được báo cáo" :message="error" action-label="Thử lại" @action="load" />

      <template v-else>
        <div class="grid-3">
          <SkStatTile label="Doanh thu đã thu" :value="formatVND(r.revenue_month)" value-color="#2f8a5d" note="Tháng này" />
          <SkStatTile label="Công nợ" :value="formatVND(r.outstanding)" value-color="#c44a3f" :note="`${r.overdue_count || 0} hóa đơn quá hạn`" />
          <SkStatTile label="Chuyên cần trung bình" :value="`${r.avg_attendance || 0}%`" note="Toàn trung tâm" />
        </div>

        <div class="grid-2">
          <div class="card card--pad">
            <div class="card__title">Chuyên cần theo lớp</div>
            <div v-if="!r.attendance_by_class.length" class="empty">Chưa có dữ liệu.</div>
            <div v-for="(c, i) in r.attendance_by_class" :key="i" class="bar-row">
              <span class="bar-row__name">{{ c.name }}</span>
              <div class="bar-row__track"><span :style="{ width: c.pct + '%' }" /></div>
              <span class="bar-row__pct tnum">{{ c.pct }}%</span>
            </div>
          </div>

          <div class="card card--pad">
            <div class="card__title">Doanh thu 6 tháng</div>
            <div v-if="!r.revenue_6m.length" class="empty">Chưa có dữ liệu.</div>
            <div v-else class="chart">
              <div v-for="(b, i) in r.revenue_6m" :key="i" class="chart-col">
                <div class="chart-bar" :style="{ height: barHeight(b.value) }" :title="formatVND(b.value)" />
                <span class="chart-label">{{ b.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '../api'
import { formatVND } from '../utils/format'
import SkStatTile from '../components/ui/SkStatTile.vue'
import SkState from '../components/ui/SkState.vue'

const loading = ref(true)
const error = ref('')
const r = reactive({ revenue_month: 0, outstanding: 0, overdue_count: 0, avg_attendance: 0, attendance_by_class: [], revenue_6m: [] })

const monthLabel = computed(() => {
  const d = new Date()
  return `Tháng ${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
})

const maxRev = computed(() => Math.max(1, ...r.revenue_6m.map((b) => Number(b.value) || 0)))
const barHeight = (v) => `${Math.max(4, Math.round(((Number(v) || 0) / maxRev.value) * 100))}%`

async function load() {
  loading.value = true
  error.value = ''
  try {
    Object.assign(r, (await call('get_reports_overview')) || {})
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
.ws-body { flex: 1; overflow-y: auto; padding: 24px 30px 44px; }

.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 22px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.card { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; }
.card--pad { padding: 16px 18px; }
.card__title { font-size: 14px; font-weight: 600; color: #4a2230; margin-bottom: 16px; }
.empty { font-size: 13px; color: #a98c98; }

.bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.bar-row__name { font-size: 12.5px; color: #7a5c68; width: 90px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-row__track { flex: 1; height: 8px; border-radius: 4px; background: #f6dde6; overflow: hidden; }
.bar-row__track > span { display: block; height: 100%; background: linear-gradient(90deg, #86c9a4, #3f9b6e); border-radius: 4px; }
.bar-row__pct { font-size: 12px; color: #2f8a5d; font-weight: 600; width: 40px; text-align: right; }

.chart { display: flex; align-items: flex-end; gap: 14px; height: 150px; padding-top: 8px; }
.chart-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 7px; height: 100%; justify-content: flex-end; }
.chart-bar { width: 100%; max-width: 34px; background: linear-gradient(180deg, #f7a8c4, #d6557e); border-radius: 6px 6px 0 0; }
.chart-label { font-size: 11px; color: #a98c98; }
</style>
