<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Lịch hẹn</span>
      <div class="ws-head__actions">
        <SkSegmented v-model="view" :options="[{label:'Danh sách',value:'list'},{label:'Lịch tuần',value:'calendar'}]" />
        <SkButton variant="solid" left-icon="plus" @click="openAdd">Đặt lịch hẹn</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="error" title="Không tải được lịch hẹn" :message="error" action-label="Thử lại" @action="load" />

      <template v-else>
        <!-- Stats -->
        <div class="stats">
          <div class="stat"><span class="stat__v">{{ appts.length }}</span><span class="stat__l">Tổng lịch hẹn</span></div>
          <div class="stat"><span class="stat__v" style="color:#4a6fb5;">{{ counts.Scheduled }}</span><span class="stat__l">Đã lên lịch</span></div>
          <div class="stat"><span class="stat__v" style="color:#3f9b6e;">{{ counts.Completed }}</span><span class="stat__l">Hoàn thành</span></div>
          <div class="stat"><span class="stat__v" style="color:#c43232;">{{ counts.Cancelled }}</span><span class="stat__l">Đã hủy</span></div>
          <div class="stat stat--today"><span class="stat__v">{{ todayCount }}</span><span class="stat__l">Hôm nay (chờ)</span></div>
        </div>

        <!-- LIST VIEW -->
        <template v-if="view === 'list'">
          <div class="toolbar">
            <div class="search">
              <FeatherIcon name="search" style="width:15px;height:15px;color:#bd8d9c;" />
              <input v-model="q" placeholder="Tìm theo tên, SĐT lead..." />
            </div>
            <SkSegmented v-model="statusFilter" :options="STATUS_FILTERS" />
            <label class="period-wrap" title="Lọc theo ngày hẹn">
              <span class="period-cap">Ngày hẹn</span>
              <select v-model="period" class="period-sel">
                <option v-for="p in PERIODS" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </label>
          </div>

          <SkState v-if="!filtered.length" state="empty" title="Không có lịch hẹn" message="Đặt lịch hẹn mới hoặc chuyển lead qua các bước ở trang Tuyển sinh." />
          <div v-else class="card">
            <table class="tbl">
              <thead>
                <tr><th>Lead</th><th>Mục đích</th><th>Ngày</th><th>Giờ</th><th>Trạng thái</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="a in filtered" :key="a.name" :class="{ 'tbl__row--today': isToday(a.appointment_date) }">
                  <td>
                    <div class="tbl__id">
                      <SkAvatar :name="a.lead_name" :src="a.lead_image" :size="30" />
                      <div class="tbl__idmeta">
                        <span class="tbl__name">{{ a.lead_name }}</span>
                        <span class="tbl__sub tnum">{{ a.lead_phone || '—' }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="tbl__sub">{{ a.purpose || '—' }}</td>
                  <td class="tbl__sub tnum">
                    {{ formatDate(a.appointment_date) }}
                    <span v-if="isToday(a.appointment_date)" class="today-tag">Hôm nay</span>
                  </td>
                  <td class="tbl__sub tnum">{{ a.appointment_time ? formatTime(a.appointment_time) : '—' }}</td>
                  <td><SkBadge v-bind="meta(a.status)" /></td>
                  <td class="tbl__act">
                    <template v-if="a.status === 'Scheduled'">
                      <SkButton variant="ghost" size="sm" left-icon="check-circle" @click="openResult(a)">Ghi kết quả</SkButton>
                      <SkButton variant="ghost" size="sm" left-icon="x" :loading="busy === a.name" @click="setStatus(a, 'Cancelled')">Hủy</SkButton>
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- CALENDAR VIEW -->
        <template v-else>
          <div class="cal">
            <div class="cal__nav">
              <SkButton variant="secondary" size="sm" left-icon="chevron-left" @click="shiftWeek(-1)">Tuần trước</SkButton>
              <span class="cal__label">{{ weekLabel }}</span>
              <SkButton variant="secondary" size="sm" @click="shiftWeek(1)">Tuần sau →</SkButton>
            </div>
            <div class="cal__grid">
              <div
                v-for="d in calendarDays"
                :key="d.date"
                class="cal__day"
                :class="{ 'cal__day--today': d.date === todayStr(), 'cal__day--sel': d.date === selectedDate }"
                @click="selectedDate = d.date"
              >
                <div class="cal__dow">{{ d.dow }}</div>
                <div class="cal__dnum">{{ d.day }}</div>
                <div class="cal__dots">
                  <span
                    v-for="a in d.appts.slice(0, 4)"
                    :key="a.name"
                    class="cal__dot"
                    :style="{ background: dotColor(a.status) }"
                  />
                  <span v-if="d.appts.length" class="cal__cnt">{{ d.appts.length }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="card daypanel">
            <div class="daypanel__head">{{ selectedDate ? formatDate(selectedDate) : 'Chọn một ngày' }} · {{ dayAppts.length }} lịch hẹn</div>
            <div v-if="!dayAppts.length" class="daypanel__empty">Không có lịch hẹn trong ngày này.</div>
            <div v-for="a in dayAppts" :key="a.name" class="dayrow">
              <SkAvatar :name="a.lead_name" :src="a.lead_image" :size="32" />
              <div class="dayrow__main">
                <div class="dayrow__name">{{ a.lead_name }} <span class="dayrow__time tnum">{{ a.appointment_time ? formatTime(a.appointment_time) : '' }}</span></div>
                <div class="dayrow__sub">{{ a.purpose || '—' }}</div>
              </div>
              <SkBadge v-bind="meta(a.status)" />
              <div v-if="a.status === 'Scheduled'" class="dayrow__act">
                <SkButton variant="ghost" size="sm" @click="openResult(a)">Ghi kết quả</SkButton>
                <SkButton variant="ghost" size="sm" :loading="busy === a.name" @click="setStatus(a, 'Cancelled')">Hủy</SkButton>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>

    <!-- Ghi kết quả buổi hẹn (tự chuyển bước) -->
    <LeadStageModal v-model="outcomeOpen" :lead="outcomeLead" :appointment="outcomeAppt" @done="onResultDone" />

    <!-- Add appointment -->
    <SkModal v-model="showAdd" title="Đặt lịch hẹn mới" width="480px">
      <form class="form" @submit.prevent="addAppointment">
        <label class="fg">
          <span>Lead / Khách hàng *</span>
          <select v-model="newApt.lead" class="field" required>
            <option value="">— Chọn lead —</option>
            <option v-for="l in leadsList" :key="l.name" :value="l.name">
              {{ l.lead_name }}<template v-if="l.phone"> ({{ l.phone }})</template>
            </option>
          </select>
        </label>
        <div class="form-grid">
          <label class="fg">
            <span>Ngày hẹn *</span>
            <input v-model="newApt.appointment_date" class="field" type="date" required />
          </label>
          <label class="fg">
            <span>Giờ hẹn</span>
            <input v-model="newApt.appointment_time" class="field" type="time" />
          </label>
        </div>
        <label class="fg">
          <span>Mục đích</span>
          <input v-model.trim="newApt.purpose" class="field" placeholder="VD: Tư vấn khóa học, Test đầu vào..." />
        </label>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="saving" @click="showAdd = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="saving" @click="addAppointment">Đặt lịch hẹn</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call, db } from '../api'
import { formatDate, formatTime } from '../utils/format'
import { statusMeta } from '../utils/labels'
import { PERIODS, inPeriod } from '../utils/period'
import { toast } from '../utils/toast'
import SkBadge from '../components/ui/SkBadge.vue'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkState from '../components/ui/SkState.vue'
import SkModal from '../components/ui/SkModal.vue'
import LeadStageModal from '../components/admissions/LeadStageModal.vue'

const loading = ref(true)
const error = ref('')
const appts = ref([])
const view = ref('list')
const statusFilter = ref('')
const q = ref('')
const period = ref('all')
const busy = ref('')

const STATUS_FILTERS = [
  { label: 'Tất cả', value: '' },
  { label: 'Đã lên lịch', value: 'Scheduled' },
  { label: 'Hoàn thành', value: 'Completed' },
  { label: 'Đã hủy', value: 'Cancelled' },
]

const meta = (s) => statusMeta('Student Appointment', 'status', s)
const pad = (n) => String(n).padStart(2, '0')
const ymd = (d) => { const x = new Date(d); return `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}` }
const todayStr = () => ymd(new Date())
const isToday = (d) => String(d || '').slice(0, 10) === todayStr()
const dotColor = (s) => ({ Completed: '#3f9b6e', Cancelled: '#c43232', Rescheduled: '#c98a2e' }[s] || '#4a6fb5')

const counts = computed(() => {
  const c = { Scheduled: 0, Completed: 0, Cancelled: 0, Rescheduled: 0 }
  for (const a of appts.value) if (c[a.status] != null) c[a.status]++
  return c
})
const todayCount = computed(() => appts.value.filter((a) => isToday(a.appointment_date) && a.status === 'Scheduled').length)

const filtered = computed(() => {
  let list = appts.value
  if (statusFilter.value) list = list.filter((a) => a.status === statusFilter.value)
  const s = q.value.trim().toLowerCase()
  if (s) list = list.filter((a) => [a.lead_name, a.lead_phone, a.purpose].some((v) => String(v || '').toLowerCase().includes(s)))
  if (period.value !== 'all') list = list.filter((a) => inPeriod(a.appointment_date, period.value))
  return list
})

/* ---- Calendar tuần ---- */
function mondayOf(d) { const x = new Date(d); const off = (x.getDay() + 6) % 7; x.setDate(x.getDate() - off); x.setHours(0, 0, 0, 0); return x }
const weekStart = ref(mondayOf(new Date()))
const selectedDate = ref(todayStr())
const DOW = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

const calendarDays = computed(() =>
  Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart.value); d.setDate(d.getDate() + i)
    const key = ymd(d)
    return { date: key, dow: DOW[i], day: d.getDate(), appts: appts.value.filter((a) => String(a.appointment_date || '').slice(0, 10) === key) }
  }),
)
const weekLabel = computed(() => {
  const end = new Date(weekStart.value); end.setDate(end.getDate() + 6)
  return `${formatDate(weekStart.value)} – ${formatDate(end)}`
})
const dayAppts = computed(() => appts.value.filter((a) => String(a.appointment_date || '').slice(0, 10) === selectedDate.value))
function shiftWeek(n) { const x = new Date(weekStart.value); x.setDate(x.getDate() + n * 7); weekStart.value = x }

/* ---- Đổi trạng thái ---- */
async function setStatus(appt, status) {
  busy.value = appt.name
  try {
    await db.setValue('Student Appointment', appt.name, 'status', status)
    appt.status = status
    toast.success(status === 'Completed' ? 'Đã hoàn thành lịch hẹn' : 'Đã hủy lịch hẹn')
  } catch (e) {
    toast.error('Không cập nhật được', e?.messages?.[0] || e?.message || String(e))
  } finally {
    busy.value = ''
  }
}

/* ---- Ghi kết quả buổi hẹn -> mở outcome modal ---- */
const outcomeOpen = ref(false)
const outcomeLead = ref(null)
const outcomeAppt = ref('')
function openResult(a) {
  outcomeLead.value = {
    name: a.lead,
    lead_name: a.lead_name,
    lead_image: a.lead_image,
    phone: a.lead_phone,
    status: a.lead_status || 'Consulting',
  }
  outcomeAppt.value = a.name
  outcomeOpen.value = true
}
async function onResultDone() {
  await load()
}

/* ---- Đặt lịch hẹn ---- */
const showAdd = ref(false)
const saving = ref(false)
const leadsList = ref([])
const newApt = ref({ lead: '', appointment_date: todayStr(), appointment_time: '', purpose: '' })

async function openAdd() {
  newApt.value = { lead: '', appointment_date: selectedDate.value || todayStr(), appointment_time: '', purpose: '' }
  showAdd.value = true
  // Luôn lấy lại danh sách lead để lead vừa tạo cũng chọn được.
  try { leadsList.value = (await call('get_leads')) || [] } catch { /* bỏ qua */ }
}
async function addAppointment() {
  if (!newApt.value.lead) { toast.error('Cần chọn lead'); return }
  if (!newApt.value.appointment_date) { toast.error('Cần ngày hẹn'); return }
  saving.value = true
  try {
    const payload = { doctype: 'Student Appointment', lead: newApt.value.lead, appointment_date: newApt.value.appointment_date }
    if (newApt.value.appointment_time) payload.appointment_time = newApt.value.appointment_time
    if (newApt.value.purpose) payload.purpose = newApt.value.purpose
    await db.insert(payload)
    toast.success('Đã đặt lịch hẹn')
    showAdd.value = false
    await load()
  } catch (e) {
    toast.error('Không đặt được lịch hẹn', e?.messages?.[0] || e?.message || String(e))
  } finally {
    saving.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    appts.value = (await call('get_all_appointments')) || []
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.ws { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; height: 100vh; overflow: hidden; }
.ws-head { height: 56px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 24px; border-bottom: 1px solid #f1dbe3; }
.ws-head__title { font-size: 16px; font-weight: 600; color: #3d2530; }
.ws-head__actions { margin-left: auto; display: flex; gap: 10px; align-items: center; }
.ws-body { flex: 1; min-height: 0; overflow: auto; padding: 20px 24px; }

.stats { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
.stat { background: #fff; border: 1px solid #f3d9e1; border-radius: 11px; padding: 13px 15px; display: flex; flex-direction: column; gap: 3px; }
.stat--today { background: #fbeef3; border-color: #ecbcce; }
.stat__v { font-size: 22px; font-weight: 700; color: #3d2530; }
.stat__l { font-size: 11.5px; color: #a07c8a; }

.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.search { flex: 1; min-width: 200px; display: flex; align-items: center; gap: 8px; height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 12px; }
.search input { border: none; outline: none; background: none; font-size: 13.5px; color: #3d2530; width: 100%; font-family: inherit; }
.period-wrap { display: inline-flex; align-items: center; gap: 6px; }
.period-cap { font-size: 11.5px; font-weight: 600; color: #a07c8a; white-space: nowrap; }
.period-sel { height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 10px; font-size: 12.5px; color: #7a5c68; font-family: inherit; cursor: pointer; outline: none; }
.period-sel:focus { border-color: #d4567f; }

.card { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl thead tr { background: #fdf2f6; }
.tbl th { text-align: left; font-size: 11.5px; font-weight: 600; color: #a07c8a; padding: 10px 16px; }
.tbl td { padding: 10px 16px; border-top: 1px solid #f6e3ea; vertical-align: middle; }
.tbl tbody tr:hover { background: #fefafb; }
.tbl__row--today { background: #fffaf3; }
.tbl__id { display: flex; align-items: center; gap: 10px; }
.tbl__idmeta { display: flex; flex-direction: column; min-width: 0; }
.tbl__name { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.tbl__sub { font-size: 13px; color: #7a5c68; }
.today-tag { margin-left: 6px; font-size: 10px; font-weight: 600; color: #c98a2e; background: #fdf3e3; border-radius: 5px; padding: 1px 6px; }
.tbl__act { text-align: right; white-space: nowrap; }

.cal { margin-bottom: 16px; }
.cal__nav { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 12px; }
.cal__label { font-size: 13px; font-weight: 600; color: #4a2230; }
.cal__grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
.cal__day { background: #fff; border: 1px solid #f3d9e1; border-radius: 10px; padding: 10px; min-height: 92px; cursor: pointer; display: flex; flex-direction: column; gap: 4px; transition: border-color 0.12s ease; }
.cal__day:hover { border-color: #ecbcce; }
.cal__day--today { background: #fffaf3; }
.cal__day--sel { border-color: #d4567f; box-shadow: 0 0 0 2px rgba(212, 86, 127, 0.18); }
.cal__dow { font-size: 10.5px; font-weight: 600; color: #a07c8a; text-transform: uppercase; }
.cal__dnum { font-size: 16px; font-weight: 700; color: #3d2530; }
.cal__dots { display: flex; flex-wrap: wrap; align-items: center; gap: 3px; margin-top: auto; }
.cal__dot { width: 7px; height: 7px; border-radius: 50%; }
.cal__cnt { font-size: 10px; color: #bd97a5; margin-left: 2px; }

.daypanel { padding: 4px 0; }
.daypanel__head { font-size: 12.5px; font-weight: 600; color: #4a2230; padding: 12px 16px; border-bottom: 1px solid #f6e3ea; }
.daypanel__empty { font-size: 13px; color: #bd97a5; padding: 16px; text-align: center; }
.dayrow { display: flex; align-items: center; gap: 11px; padding: 11px 16px; border-bottom: 1px solid #f6e3ea; }
.dayrow:last-child { border-bottom: none; }
.dayrow__main { flex: 1; min-width: 0; }
.dayrow__name { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.dayrow__time { font-size: 12px; color: #b8456a; margin-left: 6px; }
.dayrow__sub { font-size: 12px; color: #a98c98; }
.dayrow__act { display: flex; gap: 4px; white-space: nowrap; }

.form { margin: 0; display: flex; flex-direction: column; gap: 14px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }

@media (max-width: 900px) {
  .stats { grid-template-columns: repeat(2, 1fr); }
  .cal__grid { grid-template-columns: repeat(7, minmax(72px, 1fr)); overflow-x: auto; }
}
</style>
