<template>
  <div class="ws">
    <header class="ws-head">
      <div>
        <div class="ws-head__title">Xin chào, {{ userName }}</div>
      </div>
      <span class="ws-head__date">· {{ todayLabel }}</span>
      <div class="ws-head__actions">
        <SkButton variant="secondary" @click="$router.push('/students')">Đăng ký học viên</SkButton>
        <SkButton variant="solid" @click="$router.push('/classes')">Tạo lớp</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" pad="0" />
      <SkState v-else-if="error" state="error" title="Không tải được dữ liệu" :message="error" action-label="Thử lại" @action="load" />

      <template v-else>
        <!-- tiles -->
        <div class="grid-4">
          <SkStatTile label="Học viên đang học" :value="t.active_students"
            :note="`+${t.new_this_month || 0} tháng này`" note-color="#2f8a5d" />
          <SkStatTile label="Lớp đang vận hành" :value="t.ongoing_classes"
            :note="`${t.upcoming_classes || 0} sắp khai giảng`" />
          <SkStatTile label="Chuyên cần trung bình" :value="`${t.avg_attendance || 0}%`" note="Học viên đang học" />
          <SkStatTile label="Công nợ" :value="formatVND(t.outstanding)" accent value-color="#b8456a"
            :note="`${t.overdue_count || 0} hóa đơn quá hạn`" note-color="#c44a3f" />
        </div>

        <!-- today + alerts -->
        <div class="grid-2a">
          <div class="card">
            <div class="card__head">Lịch hôm nay</div>
            <div v-if="!data.sessions_today.length" class="card__empty">Hôm nay không có buổi học.</div>
            <div v-for="s in data.sessions_today" :key="s.name" class="row-session">
              <span class="row-session__time tnum">{{ formatTime(s.start_time) }}</span>
              <span class="dot" :style="{ background: dotFor(s.class_id) }" />
              <div class="row-session__main">
                <div class="row-session__title">{{ s.class_name || s.class_id }} · {{ s.lesson_topic || '—' }}</div>
                <div class="row-session__sub">{{ s.teacher_name || s.teacher || '—' }} · {{ s.classroom_name || s.classroom || '—' }}</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card__head">Cảnh báo cần xử lý</div>
            <div v-if="!data.alerts.length" class="card__empty">Không có cảnh báo.</div>
            <div v-for="(a, i) in data.alerts" :key="i" class="row-alert">
              <span class="dot mt" :style="{ background: a.level === 'danger' ? '#c44a3f' : '#c98a2e' }" />
              <div>
                <div class="row-alert__title">{{ a.title }}</div>
                <div class="row-alert__detail">{{ a.detail }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- progress + activity -->
        <div class="grid-2b">
          <div class="card card--pad">
            <div class="card__title">Tiến độ các lớp</div>
            <div v-if="!data.class_progress.length" class="card__empty" style="padding:0;">Chưa có lớp.</div>
            <div v-for="(p, i) in data.class_progress" :key="i" class="prog">
              <span class="prog__name">{{ p.name }}</span>
              <div class="prog__bar"><span :style="{ width: pct(p.pct) }" /></div>
              <span class="prog__pct tnum">{{ pct(p.pct) }}</span>
            </div>
          </div>

          <div class="card card--pad">
            <div class="card__title">Hoạt động gần đây</div>
            <div v-if="!data.activity.length" class="card__empty" style="padding:0;">Chưa có hoạt động.</div>
            <div v-for="(h, i) in data.activity" :key="i" class="act">
              <span class="dot mt" :style="{ background: h.dot }" />
              <div>
                <div class="act__text">{{ h.text }}</div>
                <div class="act__time">{{ formatRelative(h.time) }}</div>
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
import { formatVND, formatTime, formatRelative } from '../utils/format'
import SkButton from '../components/ui/SkButton.vue'
import SkStatTile from '../components/ui/SkStatTile.vue'
import SkState from '../components/ui/SkState.vue'

const loading = ref(true)
const error = ref('')
const data = reactive({ tiles: {}, sessions_today: [], class_progress: [], alerts: [], activity: [] })
const t = computed(() => data.tiles || {})

const boot = typeof window !== 'undefined' ? window.frappe?.boot : null
const userId = boot?.user?.name || ''
const userName = boot?.user_info?.[userId]?.fullname || boot?.user?.full_name || 'Giáo vụ'

const todayLabel = computed(() => {
  const d = new Date()
  const days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy']
  const p = (n) => String(n).padStart(2, '0')
  return `${days[d.getDay()]}, ${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()}`
})

const DOTS = ['#d6557e', '#9b6fc4', '#3f9b6e', '#e07a8f', '#4a6fb5']
function dotFor(key) {
  let h = 0
  for (const c of String(key || '')) h = (h * 31 + c.charCodeAt(0)) % 997
  return DOTS[h % DOTS.length]
}
const pct = (v) => `${Math.round(Number(v) || 0)}%`

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await call('get_dashboard_overview')
    Object.assign(data, res || {})
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
.ws-head__date { font-size: 12.5px; color: #a98c98; }
.ws-head__actions { margin-left: auto; display: flex; gap: 8px; }
.ws-body { flex: 1; overflow-y: auto; padding: 24px 30px 44px; }

.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
.grid-2a { display: grid; grid-template-columns: 1.4fr 1fr; gap: 18px; margin-bottom: 18px; }
.grid-2b { display: grid; grid-template-columns: 1fr 1.2fr; gap: 18px; }

.card { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; overflow: hidden; }
.card--pad { padding: 16px 18px; }
.card__head { padding: 14px 18px; border-bottom: 1px solid #f6e3ea; font-size: 14px; font-weight: 600; color: #4a2230; }
.card__title { font-size: 14px; font-weight: 600; color: #4a2230; margin-bottom: 14px; }
.card__empty { padding: 16px 18px; font-size: 13px; color: #a98c98; }

.row-session { display: flex; align-items: center; gap: 13px; padding: 12px 18px; border-bottom: 1px solid #f8eaef; }
.row-session__time { font-size: 13px; font-weight: 600; color: #b8456a; width: 46px; }
.row-session__main { flex: 1; min-width: 0; }
.row-session__title { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.row-session__sub { font-size: 11.5px; color: #a98c98; }

.dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.dot.mt { width: 8px; height: 8px; margin-top: 5px; }

.row-alert { display: flex; align-items: flex-start; gap: 11px; padding: 11px 18px; border-bottom: 1px solid #f8eaef; }
.row-alert__title { font-size: 13px; font-weight: 600; color: #3d2530; }
.row-alert__detail { font-size: 11.5px; color: #a98c98; margin-top: 1px; }

.prog { display: flex; align-items: center; gap: 12px; margin-bottom: 11px; }
.prog__name { font-size: 12.5px; color: #7a5c68; width: 90px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prog__bar { flex: 1; height: 7px; border-radius: 4px; background: #f6dde6; overflow: hidden; }
.prog__bar > span { display: block; height: 100%; background: linear-gradient(90deg, #f7a8c4, #d6557e); border-radius: 4px; }
.prog__pct { font-size: 12px; color: #b8456a; font-weight: 600; width: 40px; text-align: right; }

.act { display: flex; gap: 12px; margin-bottom: 13px; }
.act__text { font-size: 13px; color: #3d2530; }
.act__time { font-size: 11px; color: #bd97a5; margin-top: 1px; }
</style>
