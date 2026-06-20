<template>
  <div class="ws">
    <header class="tp-head">
      <SkAvatar :name="teacherName" :size="34" />
      <div>
        <div class="tp-head__name">{{ teacherName }}</div>
        <div class="tp-head__sub">Giáo viên · {{ todayLabel }}</div>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="denied" title="Không truy cập được cổng giáo viên" :message="error" />

      <div v-else class="tp-wrap">
        <div class="tp-section">Lịch dạy hôm nay</div>
        <div class="tp-today">
          <div v-if="!data.sessions_today.length" class="card pad muted">Hôm nay bạn không có buổi dạy.</div>
          <div v-for="s in data.sessions_today" :key="s.name" class="tp-row">
            <div class="tp-row__time tnum">{{ formatTime(s.start_time) }}</div>
            <div class="tp-row__main">
              <div class="tp-row__title">{{ s.class_name || s.class_id }} · {{ s.lesson_topic || '—' }}</div>
              <div class="tp-row__sub">{{ labelStatus(s.session_status) }}</div>
            </div>
            <SkButton variant="solid" @click="$router.push('/attendance')">Mở buổi học</SkButton>
          </div>
        </div>

        <div class="grid-2">
          <div class="card">
            <div class="card__head">Cần hoàn tất</div>
            <div v-if="!todo.length" class="card__empty">Không có buổi nào cần hoàn tất.</div>
            <div v-for="s in todo" :key="s.name" class="tp-todo">
              <div class="tp-todo__title">{{ s.class_name || s.class_id }} · {{ s.lesson_topic || 'Buổi học' }}</div>
              <div class="tp-todo__detail">{{ labelStatus(s.session_status) }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card__head">Lớp phụ trách</div>
            <div v-if="!data.classes.length" class="card__empty">Chưa được phân công lớp.</div>
            <div v-for="c in data.classes" :key="c.name" class="tp-cls">
              <div class="tp-cls__main">
                <div class="tp-cls__name">{{ c.class_name || c.name }}</div>
                <div class="tp-cls__bar"><span :style="{ width: pct(c.progress) }" /></div>
              </div>
              <SkBadge v-bind="clsMeta(c.status)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '../api'
import { formatTime } from '../utils/format'
import { statusMeta } from '../utils/labels'
import SkButton from '../components/ui/SkButton.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkState from '../components/ui/SkState.vue'

const loading = ref(true)
const error = ref('')
const data = reactive({ teacher: '', classes: [], sessions_today: [] })

const teacherName = computed(() => data.teacher || 'Giáo viên')
const todo = computed(() => data.sessions_today.filter((s) => s.session_status !== 'Completed'))

const todayLabel = computed(() => {
  const d = new Date()
  const days = ['CN', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy']
  const p = (n) => String(n).padStart(2, '0')
  return `Hôm nay, ${days[d.getDay()]} ${p(d.getDate())}/${p(d.getMonth() + 1)}`
})

const labelStatus = (s) => statusMeta('Class Session', 'session_status', s).label
const clsMeta = (s) => statusMeta('Class', 'status', s)
const pct = (v) => `${Math.round(Number(v) || 0)}%`

async function load() {
  loading.value = true
  error.value = ''
  try {
    Object.assign(data, (await call('get_my_teacher_overview')) || {})
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.ws { flex: 1; min-width: 0; display: flex; flex-direction: column; height: 100vh; background: linear-gradient(140deg, #fff7fa, #fdedf3); }
.tp-head { height: 56px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 28px; border-bottom: 1px solid #f1dbe3; background: rgba(255, 253, 254, 0.7); }
.tp-head__name { font-size: 15px; font-weight: 600; color: #3d2530; }
.tp-head__sub { font-size: 11.5px; color: #a98c98; }
.ws-body { flex: 1; overflow-y: auto; padding: 24px 28px 44px; }
.tp-wrap { max-width: 920px; }
.tp-section { font-size: 15px; font-weight: 600; color: #4a2230; margin-bottom: 13px; }
.tp-today { display: flex; flex-direction: column; gap: 11px; margin-bottom: 28px; }
.tp-row { display: flex; align-items: center; gap: 16px; border: 1px solid #f3d9e1; border-radius: 12px; padding: 15px 18px; background: #fff; }
.tp-row__time { flex: none; width: 64px; font-size: 14px; font-weight: 700; color: #b8456a; }
.tp-row__main { flex: 1; min-width: 0; }
.tp-row__title { font-size: 14px; font-weight: 600; color: #3d2530; }
.tp-row__sub { font-size: 12.5px; color: #a98c98; margin-top: 2px; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.card { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; overflow: hidden; }
.card.pad { padding: 14px 18px; }
.card.muted { color: #a98c98; font-size: 13px; }
.card__head { padding: 13px 18px; border-bottom: 1px solid #f6e3ea; font-size: 13.5px; font-weight: 600; color: #4a2230; }
.card__empty { padding: 14px 18px; font-size: 12.5px; color: #a98c98; }
.tp-todo { padding: 11px 18px; border-bottom: 1px solid #f8eaef; }
.tp-todo__title { font-size: 13px; font-weight: 500; color: #3d2530; }
.tp-todo__detail { font-size: 11.5px; color: #c0708a; margin-top: 1px; }
.tp-cls { display: flex; align-items: center; gap: 12px; padding: 11px 18px; border-bottom: 1px solid #f8eaef; }
.tp-cls__main { flex: 1; min-width: 0; }
.tp-cls__name { font-size: 13px; font-weight: 500; color: #3d2530; }
.tp-cls__bar { height: 5px; border-radius: 3px; background: #f6dde6; overflow: hidden; margin-top: 6px; }
.tp-cls__bar > span { display: block; height: 100%; background: linear-gradient(90deg, #f7a8c4, #d6557e); }
</style>
