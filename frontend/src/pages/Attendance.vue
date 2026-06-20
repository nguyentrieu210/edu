<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Điểm danh</span>
      <span class="ws-head__sub">{{ sessionLabel }}</span>
    </header>

    <!-- toolbar -->
    <div class="toolbar">
      <select v-model="selectedClass" class="field field--sel" @change="onClassChange">
        <option value="" disabled>Chọn lớp…</option>
        <option v-for="c in classes" :key="c.name" :value="c.name">{{ c.class_name || c.name }}</option>
      </select>
      <select v-model="selectedSession" class="field field--sel" :disabled="!sessions.length" @change="loadRoster">
        <option value="" disabled>Chọn buổi…</option>
        <option v-for="(s, i) in sessions" :key="s.name" :value="s.name">Buổi {{ i + 1 }} · {{ formatDate(s.session_date) }}</option>
      </select>
      <SkButton variant="secondary" size="sm" :disabled="!roster.length" @click="markAll('Present')">Có mặt tất cả</SkButton>
      <template v-if="curSession">
        <SkBadge v-bind="sesMeta(curSession.session_status)" />
        <SkButton v-if="!['Completed', 'Cancelled', 'Locked'].includes(curSession.session_status)" size="sm" variant="ghost" left-icon="x" @click="sessAction('Cancelled')">Hủy buổi</SkButton>
        <SkButton v-else-if="curSession.session_status === 'Cancelled'" size="sm" variant="ghost" left-icon="rotate-ccw" @click="sessAction('Scheduled')">Khôi phục</SkButton>
      </template>
      <span class="toolbar__hint">{{ roster.length ? `${roster.length} học viên` : 'Chọn lớp và buổi để điểm danh' }}</span>
    </div>

    <div v-if="curSession" class="subbar">
      <span class="subbar__l">Chủ đề buổi:</span>
      <InlineCell doctype="Class Session" :name="curSession.name" field="lesson_topic" v-model="curSession.lesson_topic" placeholder="Chưa có chủ đề" />
    </div>

    <!-- body -->
    <div class="ws-body sk-scroll">
      <SkState v-if="loadingRoster" state="loading" />
      <SkState v-else-if="!selectedSession" state="empty" title="Chưa chọn buổi học" message="Chọn lớp và buổi học ở thanh trên để bắt đầu điểm danh." />
      <SkState v-else-if="!roster.length" state="empty" title="Lớp chưa có học viên Active" message="Buổi học này không có học viên cần điểm danh." />

      <div v-else class="roster">
        <div v-for="r in roster" :key="r.program_enrollment" class="att-row">
          <SkAvatar :name="r.student_name" :src="r.student_image" :size="38" />
          <div class="att-row__main">
            <div class="att-row__name">{{ r.student_name }}</div>
            <div class="att-row__code tnum">{{ r.student }}</div>
          </div>
          <input v-if="r.status === 'Late'" v-model.number="r.minutes_late" type="number" min="0" class="att-late" placeholder="phút" title="Số phút đi muộn" />
          <div class="seg">
            <button v-for="o in OPTS" :key="o.value" class="seg__btn" :class="{ 'seg__btn--on': r.status === o.value }"
              :style="r.status === o.value ? { color: o.color, background: '#fff', boxShadow: '0 1px 3px rgba(180,80,120,0.18)' } : {}"
              @click="r.status = o.value">{{ o.label }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- footer -->
    <div v-if="roster.length" class="foot">
      <span class="foot__total">Tổng <b>{{ roster.length }}</b> học viên</span>
      <span class="foot__c" style="color:#2f8a5d;">Có mặt {{ counts.present }}</span>
      <span class="foot__c" style="color:#b07a1f;">Muộn {{ counts.late }}</span>
      <span class="foot__c" style="color:#c44a3f;">Vắng {{ counts.absent }}</span>
      <div class="foot__actions">
        <SkButton variant="secondary" :loading="saving" @click="save(false)">Lưu nháp</SkButton>
        <SkButton variant="solid" size="lg" :loading="completing" @click="save(true)">Lưu & hoàn tất buổi</SkButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '../api'
import { formatDate, formatTime } from '../utils/format'
import { statusMeta } from '../utils/labels'
import { toast } from '../utils/toast'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkState from '../components/ui/SkState.vue'
import InlineCell from '../components/common/InlineCell.vue'

const OPTS = [
  { value: 'Present', label: 'Có mặt', color: '#2f8a5d' },
  { value: 'Late', label: 'Muộn', color: '#b07a1f' },
  { value: 'Absent without Permission', label: 'Vắng', color: '#c44a3f' },
]

const classes = ref([])
const sessions = ref([])
const selectedClass = ref('')
const selectedSession = ref('')
const roster = ref([])
const names = ref({})
const loadingRoster = ref(false)
const saving = ref(false)
const completing = ref(false)

const sesMeta = (s) => statusMeta('Class Session', 'session_status', s)
const curSession = computed(() => sessions.value.find((x) => x.name === selectedSession.value) || null)

async function sessAction(status) {
  if (!curSession.value) return
  try {
    await call('set_session_status', { class_session: curSession.value.name, status })
    curSession.value.session_status = status
    toast.success(status === 'Cancelled' ? 'Đã hủy buổi' : 'Đã khôi phục buổi')
  } catch (e) {
    toast.error('Không đổi được trạng thái buổi', e?.messages?.[0] || e?.message || String(e))
  }
}

const sessionLabel = computed(() => {
  const s = sessions.value.find((x) => x.name === selectedSession.value)
  if (!s) return ''
  const cls = classes.value.find((c) => c.name === selectedClass.value)
  return `${cls?.class_name || selectedClass.value} · ${formatDate(s.session_date)} · ${formatTime(s.start_time)}`
})

const counts = computed(() => ({
  present: roster.value.filter((r) => r.status === 'Present').length,
  late: roster.value.filter((r) => r.status === 'Late').length,
  absent: roster.value.filter((r) => r.status.startsWith('Absent')).length,
}))

function markAll(status) {
  roster.value.forEach((r) => (r.status = status))
}

async function onClassChange() {
  selectedSession.value = ''
  roster.value = []
  sessions.value = []
  if (!selectedClass.value) return
  sessions.value = (await call('get_class_sessions', { class_id: selectedClass.value })) || []
  // tự chọn buổi gần hôm nay nhất chưa hoàn thành
  const pending = sessions.value.find((s) => s.session_status !== 'Completed')
  if (pending) { selectedSession.value = pending.name; loadRoster() }
}

async function loadRoster() {
  if (!selectedSession.value) return
  loadingRoster.value = true
  try {
    const res = await call('get_session_roster', { class_session: selectedSession.value })
    roster.value = (res?.rows || []).map((r) => ({
      ...r,
      student_name: names.value[r.student] || r.student,
      status: r.status || 'Present',
    }))
  } finally {
    loadingRoster.value = false
  }
}

async function save(complete) {
  const rows = roster.value.map((r) => ({
    program_enrollment: r.program_enrollment,
    status: r.status,
    attendance_type: r.attendance_type || 'Regular',
    minutes_late: r.minutes_late || 0,
  }))
  if (complete) completing.value = true
  else saving.value = true
  try {
    await call('save_session_attendance', { class_session: selectedSession.value, rows })
    if (complete) {
      await call('complete_class_session', { class_session: selectedSession.value })
      toast.success('Đã hoàn tất buổi học', sessionLabel.value)
      // refresh sessions status
      await onClassChange()
    } else {
      toast.success('Đã lưu điểm danh', `${rows.length} học viên`)
    }
  } catch (e) {
    toast.error(complete ? 'Không hoàn tất được buổi' : 'Lưu thất bại', e?.message || String(e))
  } finally {
    saving.value = false
    completing.value = false
  }
}

async function load() {
  const [cls, studs] = await Promise.all([call('get_classes'), call('get_students')])
  classes.value = cls || []
  const map = {}
  for (const s of studs || []) map[s.name] = s.full_name
  names.value = map
}
onMounted(load)
</script>

<style scoped>
.ws { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; height: 100vh; }
.ws-head { height: 56px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 24px; border-bottom: 1px solid #f1dbe3; }
.ws-head__title { font-size: 16px; font-weight: 600; color: #3d2530; }
.ws-head__sub { font-size: 13px; color: #a98c98; }

.toolbar { height: 52px; flex: none; display: flex; align-items: center; gap: 10px; padding: 0 24px; border-bottom: 1px solid #f4dde5; background: #fffafb; }
.field--sel { width: auto; min-width: 180px; appearance: none; height: 34px; }
.toolbar__hint { margin-left: auto; font-size: 12.5px; color: #a98c98; }

.subbar { flex: none; display: flex; align-items: center; gap: 8px; padding: 8px 24px; border-bottom: 1px solid #f6e3ea; background: #fffdfe; font-size: 13px; color: #3d2530; }
.subbar__l { font-size: 12px; font-weight: 600; color: #a07c8a; }
.att-late { width: 70px; height: 30px; border: 1px solid #ecd0da; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 12.5px; color: #3d2530; outline: none; font-family: inherit; flex: none; }
.att-late:focus { border-color: #d4567f; }

.ws-body { flex: 1; overflow-y: auto; }
.roster { padding: 14px 24px 24px; }
.att-row { display: flex; align-items: center; gap: 14px; padding: 9px 4px; border-bottom: 1px solid #f6e3ea; }
.att-row__main { flex: 1; min-width: 0; }
.att-row__name { font-size: 14px; font-weight: 500; color: #3d2530; }
.att-row__code { font-size: 11.5px; color: #a98c98; }

.seg { display: flex; background: #fbe6ee; border-radius: 8px; padding: 3px; gap: 2px; flex: none; }
.seg__btn { height: 30px; padding: 0 14px; border: none; border-radius: 6px; cursor: pointer; font-family: inherit; font-size: 12.5px; font-weight: 500; background: transparent; color: #a07c8a; transition: all 0.12s ease; }
.seg__btn--on { font-weight: 600; }

.foot { flex: none; height: 60px; border-top: 1px solid #f1dbe3; background: #fffafb; display: flex; align-items: center; gap: 18px; padding: 0 24px; }
.foot__total { font-size: 13px; color: #7a5c68; }
.foot__total b { color: #3d2530; }
.foot__c { font-size: 13px; font-weight: 600; }
.foot__actions { margin-left: auto; display: flex; gap: 10px; }
</style>
