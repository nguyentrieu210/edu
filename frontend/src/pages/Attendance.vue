<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Điểm danh</span>
      <span class="ws-head__sub">{{ sessionLabel }}</span>
    </header>

    <div class="att3">
      <!-- COL 1: Lớp -->
      <aside class="att-col att-col--cls">
        <div class="att-col__head">Lớp học</div>
        <div class="att-col__list sk-scroll">
          <button v-for="c in classes" :key="c.name" class="att-item" :class="{ 'att-item--on': c.name === selectedClass }" @click="selectClass(c.name)">
            <div class="att-item__t">{{ c.class_name || c.name }}</div>
            <div class="att-item__s">{{ c.teacher_name || c.course_name || '' }}</div>
          </button>
          <div v-if="!classes.length" class="att-col__empty">Chưa có lớp.</div>
        </div>
      </aside>

      <!-- COL 2: Buổi -->
      <aside class="att-col att-col--ses">
        <div class="att-col__head">Buổi học</div>
        <div v-if="!selectedClass" class="att-col__empty">← Chọn lớp</div>
        <div v-else-if="!sessions.length" class="att-col__empty">Lớp chưa có buổi.</div>
        <div v-else class="att-col__list sk-scroll">
          <button v-for="(s, i) in sessions" :key="s.name" class="att-item" :class="{ 'att-item--on': s.name === selectedSession }" @click="selectSession(s.name)">
            <div class="att-item__t">Buổi {{ i + 1 }} · {{ formatDate(s.session_date) }}</div>
            <div class="att-item__s"><SkBadge v-bind="sesMeta(s.session_status)" /> <span class="tnum">{{ formatTime(s.start_time) }}</span></div>
          </button>
        </div>
      </aside>

      <!-- COL 3: Điểm danh -->
      <section class="att-col att-col--rost">
        <div class="att-col__head att-col__head--row">
          <span>Điểm danh</span>
          <div v-if="curSession" class="att-rhead">
            <SkButton variant="secondary" size="sm" :disabled="!roster.length" @click="markAll('Present')">Có mặt tất cả</SkButton>
            <SkButton v-if="!['Completed', 'Cancelled', 'Locked'].includes(curSession.session_status)" size="sm" variant="ghost" left-icon="x" @click="sessAction('Cancelled')">Hủy buổi</SkButton>
            <SkButton v-else-if="curSession.session_status === 'Cancelled'" size="sm" variant="ghost" left-icon="rotate-ccw" @click="sessAction('Scheduled')">Khôi phục</SkButton>
          </div>
        </div>

        <div v-if="curSession" class="subbar">
          <span class="subbar__l">Chủ đề:</span>
          <InlineCell doctype="Class Session" :name="curSession.name" field="lesson_topic" v-model="curSession.lesson_topic" placeholder="Chưa có chủ đề" />
        </div>

        <div class="att-col__list sk-scroll">
          <SkState v-if="loadingRoster" state="loading" />
          <SkState v-else-if="!selectedSession" state="empty" title="Chưa chọn buổi" message="Chọn lớp rồi chọn buổi để điểm danh." />
          <SkState v-else-if="!roster.length" state="empty" title="Không có học viên" message="Buổi học này chưa có học viên Active." />
          <div v-else class="roster">
            <div v-for="r in roster" :key="r.program_enrollment" class="att-row">
              <SkAvatar :name="r.student_name" :src="r.student_image" :size="36" />
              <div class="att-row__main">
                <div class="att-row__name">{{ r.student_name }}</div>
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

        <div v-if="roster.length" class="foot">
          <span class="foot__c" style="color:#2f8a5d;">CM {{ counts.present }}</span>
          <span class="foot__c" style="color:#b07a1f;">Muộn {{ counts.late }}</span>
          <span class="foot__c" style="color:#c44a3f;">Vắng {{ counts.absent }}</span>
          <div class="foot__actions">
            <SkButton variant="secondary" :loading="saving" @click="save(false)">Lưu nháp</SkButton>
            <SkButton variant="solid" :loading="completing" @click="save(true)">Lưu & hoàn tất</SkButton>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

function markAll(status) { roster.value.forEach((r) => (r.status = status)) }

async function selectClass(name) {
  selectedClass.value = name
  selectedSession.value = ''
  roster.value = []
  sessions.value = (await call('get_class_sessions', { class_id: name })) || []
  const pending = sessions.value.find((s) => s.session_status !== 'Completed') || sessions.value[0]
  if (pending) selectSession(pending.name)
}

function selectSession(name) {
  selectedSession.value = name
  loadRoster()
}

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

async function loadRoster() {
  if (!selectedSession.value) return
  loadingRoster.value = true
  try {
    const res = await call('get_session_roster', { class_session: selectedSession.value })
    roster.value = (res?.rows || []).map((r) => ({
      ...r,
      student_name: r.student_name || names.value[r.student] || r.student,
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
    minutes_late: r.status === 'Late' ? (r.minutes_late || 0) : 0,
  }))
  if (complete) completing.value = true
  else saving.value = true
  try {
    await call('save_session_attendance', { class_session: selectedSession.value, rows })
    if (complete) {
      await call('complete_class_session', { class_session: selectedSession.value })
      toast.success('Đã hoàn tất buổi học', sessionLabel.value)
    } else {
      toast.success('Đã lưu điểm danh', `${rows.length} học viên`)
    }
    // refresh trạng thái buổi của lớp đang chọn
    const keep = selectedSession.value
    sessions.value = (await call('get_class_sessions', { class_id: selectedClass.value })) || []
    selectedSession.value = keep
    await loadRoster()
  } catch (e) {
    toast.error(complete ? 'Không hoàn tất được buổi' : 'Lưu thất bại', e?.messages?.[0] || e?.message || String(e))
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

.att3 { flex: 1; min-height: 0; display: grid; grid-template-columns: 240px 240px 1fr; }
.att-col { display: flex; flex-direction: column; min-height: 0; border-right: 1px solid #f4dde5; }
.att-col--rost { border-right: none; }
.att-col__head { height: 46px; flex: none; display: flex; align-items: center; padding: 0 16px; font-size: 12.5px; font-weight: 700; color: #8a5c6c; background: #fdf3f7; border-bottom: 1px solid #f4dde5; text-transform: uppercase; letter-spacing: 0.4px; }
.att-col__head--row { justify-content: space-between; }
.att-rhead { display: flex; gap: 6px; align-items: center; text-transform: none; }
.att-col__list { flex: 1; overflow-y: auto; }
.att-col__empty { padding: 18px 16px; color: #b69aa6; font-size: 13px; }

.att-item { display: block; width: 100%; text-align: left; border: none; background: transparent; cursor: pointer; padding: 10px 16px; border-bottom: 1px solid #f8eaf0; font-family: inherit; border-left: 3px solid transparent; }
.att-item:hover { background: #fdf6f9; }
.att-item--on { background: #fbd9e5; border-left-color: #d6557e; }
.att-item__t { font-size: 13px; font-weight: 600; color: #4a2230; }
.att-item__s { font-size: 11.5px; color: #a07c8a; margin-top: 3px; display: flex; align-items: center; gap: 6px; }

.subbar { flex: none; display: flex; align-items: center; gap: 8px; padding: 8px 18px; border-bottom: 1px solid #f6e3ea; background: #fffdfe; font-size: 13px; color: #3d2530; }
.subbar__l { font-size: 12px; font-weight: 600; color: #a07c8a; }

.roster { padding: 8px 18px 18px; }
.att-row { display: flex; align-items: center; gap: 12px; padding: 8px 4px; border-bottom: 1px solid #f6e3ea; }
.att-row__main { flex: 1; min-width: 0; }
.att-row__name { font-size: 14px; font-weight: 500; color: #3d2530; }
.att-late { width: 66px; height: 30px; border: 1px solid #ecd0da; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 12.5px; color: #3d2530; outline: none; font-family: inherit; flex: none; }
.att-late:focus { border-color: #d4567f; }

.seg { display: flex; background: #fbe6ee; border-radius: 8px; padding: 3px; gap: 2px; flex: none; }
.seg__btn { height: 30px; padding: 0 12px; border: none; border-radius: 6px; cursor: pointer; font-family: inherit; font-size: 12.5px; font-weight: 500; background: transparent; color: #a07c8a; transition: all 0.12s ease; }
.seg__btn--on { font-weight: 600; }

.foot { flex: none; height: 56px; border-top: 1px solid #f1dbe3; background: #fffafb; display: flex; align-items: center; gap: 16px; padding: 0 18px; }
.foot__c { font-size: 13px; font-weight: 600; }
.foot__actions { margin-left: auto; display: flex; gap: 10px; }
</style>
