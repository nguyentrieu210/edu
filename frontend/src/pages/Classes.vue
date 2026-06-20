<template>
  <div class="md">
    <!-- CONTEXT -->
    <section class="ctx">
      <div class="ctx__head">
        <span class="ctx__title">Lớp học</span>
        <div class="ctx__meta">
          <span class="ctx__count">{{ classes.length }} lớp</span>
          <SkButton size="sm" variant="solid" left-icon="plus" @click="openClass">Thêm lớp</SkButton>
        </div>
      </div>
      <div class="ctx__list sk-scroll">
        <SkState v-if="loading" state="loading" />
        <SkState v-else-if="!classes.length" state="empty" title="Chưa có lớp" message="Tạo lớp đầu tiên để bắt đầu." action-label="Thêm lớp" @action="openClass" />
        <button v-for="c in classes" :key="c.name" class="crow" :class="{ 'crow--active': c.name === selectedId }" @click="select(c.name)">
          <div class="crow__top">
            <span class="crow__id">{{ c.class_name || c.name }}</span>
            <SkBadge v-bind="clsMeta(c.status)" />
          </div>
          <div class="crow__sub">{{ c.course || '—' }} · {{ c.teacher || '—' }}</div>
          <div class="crow__bar">
            <div class="crow__track"><span :style="{ width: pct(c.progress) }" /></div>
            <span class="crow__pct tnum">{{ pct(c.progress) }}</span>
          </div>
        </button>
      </div>
    </section>

    <!-- DETAIL -->
    <main class="dtl">
      <SkState v-if="!selectedId && !loading" state="empty" title="Chọn một lớp" message="Chọn lớp ở danh sách bên trái để xem chi tiết." />

      <template v-else-if="selectedId">
        <header class="dtl__head">
          <div class="dtl__id">
            <span class="dtl__name">{{ cur.class_name || selectedId }}</span>
            <span class="dtl__slash">·</span>
            <span class="dtl__code">{{ cur.course || '—' }}</span>
            <SkBadge v-bind="clsMeta(cur.status)" />
          </div>
          <div class="dtl__actions">
            <SkButton variant="secondary" :loading="generatingSessions" @click="generateSessions">Sinh lịch</SkButton>
            <SkButton variant="secondary" left-icon="user-plus" @click="openEnrollment">Gán học viên</SkButton>
            <SkButton variant="solid" @click="$router.push('/attendance')">Mở buổi hôm nay</SkButton>
          </div>
        </header>

        <div class="dtl__tabs">
          <button v-for="t in TABS" :key="t.id" class="tab" :class="{ 'tab--active': tab === t.id }" @click="tab = t.id">{{ t.label }}</button>
        </div>

        <div class="dtl__body sk-scroll">
          <SkState v-if="detailLoading" state="loading" />
          <div v-else class="dtl__inner">
            <!-- OVERVIEW -->
            <div v-if="tab === 'overview'" class="stack">
              <div>
                <div class="block__title">Thông tin lớp</div>
                <div class="info">
                  <div class="info__c"><div class="info__l">Khóa học</div><div class="info__v">{{ cur.course || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Giáo viên chính</div><div class="info__v">{{ cur.teacher || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Giáo viên thay thế</div><div class="info__v">{{ cur.substitute_teacher || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Lịch học</div><div class="info__v">{{ schedule }}</div></div>
                  <div class="info__c"><div class="info__l">Phòng học</div><div class="info__v">{{ cur.classroom || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Sĩ số</div><div class="info__v tnum">{{ roster.length }} / {{ cur.max_capacity || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Khai giảng</div><div class="info__v">{{ formatDate(cur.start_date) }}</div></div>
                  <div class="info__c"><div class="info__l">Tổng số buổi</div><div class="info__v tnum">{{ cur.total_sessions || sessions.length }} buổi</div></div>
                  <div class="info__c"><div class="info__l">Học phí chuẩn</div><div class="info__v tnum">{{ formatVND(cur.standard_fee) }}</div></div>
                </div>
              </div>
              <div class="progcard">
                <div class="progcard__top"><span class="progcard__label">Tiến độ khóa học</span><span class="progcard__pct tnum">{{ pct(cur.progress) }}</span></div>
                <div class="progcard__bar"><span :style="{ width: pct(cur.progress) }" /></div>
              </div>

              <div class="flowgrid">
                <button class="flowcard" @click="tab = 'roster'">
                  <span class="flowcard__label">Danh sách học viên</span>
                  <strong>{{ roster.length }} / {{ cur.max_capacity || '—' }}</strong>
                  <small>Đã gán vào lớp</small>
                </button>
                <div class="flowcard">
                  <span class="flowcard__label">Giáo viên phụ trách</span>
                  <strong>{{ cur.teacher || 'Chưa gán' }}</strong>
                  <small>{{ cur.substitute_teacher ? `Dự phòng ${cur.substitute_teacher}` : 'Giáo viên chính' }}</small>
                </div>
                <button class="flowcard" @click="tab = 'sessions'">
                  <span class="flowcard__label">Lịch theo chương trình</span>
                  <strong>{{ sessions.length }} buổi</strong>
                  <small>{{ schedule }}</small>
                </button>
                <button class="flowcard" @click="$router.push('/attendance')">
                  <span class="flowcard__label">Điểm danh / Nhập điểm</span>
                  <strong>{{ completedSessions }} xong</strong>
                  <small>Cập nhật từng buổi</small>
                </button>
                <div class="flowcard">
                  <span class="flowcard__label">Tiến độ lớp</span>
                  <strong>{{ pct(cur.progress) }}</strong>
                  <small>{{ completedSessions }} / {{ sessions.length || cur.total_sessions || 0 }} buổi</small>
                </div>
                <button class="flowcard" @click="tab = 'roster'">
                  <span class="flowcard__label">Học phí lớp / học viên</span>
                  <strong>{{ formatVND(feeStats.outstanding) }}</strong>
                  <small>Còn nợ · đã thu {{ formatVND(feeStats.paid) }}</small>
                </button>
              </div>
            </div>

            <!-- ROSTER -->
            <div v-else-if="tab === 'roster'">
              <div class="block__head">
                <div>
                  <div class="block__title">Danh sách học viên · {{ roster.length }}</div>
                  <div class="block__hint">Gán học viên vào lớp sẽ tạo Program Enrollment, chốt học phí và sinh hóa đơn.</div>
                </div>
                <SkButton variant="solid" left-icon="user-plus" @click="openEnrollment">Gán học viên</SkButton>
              </div>
              <div class="grid3 fee-mini">
                <div><span>Tổng net fee</span><strong>{{ formatVND(feeStats.total) }}</strong></div>
                <div><span>Đã thu</span><strong>{{ formatVND(feeStats.paid) }}</strong></div>
                <div><span>Còn nợ</span><strong>{{ formatVND(feeStats.outstanding) }}</strong></div>
              </div>
              <div class="tblwrap">
                <table class="tbl">
                  <thead><tr><th>Học viên</th><th>Mã</th><th>Đăng ký</th><th style="text-align:right;">Net fee</th><th style="text-align:right;">Còn nợ</th><th style="text-align:right;">Chuyên cần</th><th style="text-align:right;">Điểm TB</th><th style="text-align:right;">Trạng thái</th></tr></thead>
                  <tbody>
                    <tr v-if="!roster.length"><td colspan="8" class="muted" style="padding:16px;">Lớp chưa có học viên.</td></tr>
                    <tr v-for="r in roster" :key="r.student">
                      <td><div class="cell-av"><SkAvatar :name="r.name" :size="32" /><span class="tbl__name">{{ r.name }}</span></div></td>
                      <td class="tbl__sub tnum">{{ r.student }}</td>
                      <td><SkBadge v-bind="enrMeta(r.enrollment_status)" /></td>
                      <td class="tbl__name tnum" style="text-align:right;">{{ formatVND(r.net_fee) }}</td>
                      <td class="tnum" style="text-align:right;" :style="{ color: Number(r.outstanding_amount) > 0 ? '#c43232' : '#2f8a5d' }">{{ formatVND(r.outstanding_amount) }}</td>
                      <td class="tbl__sub tnum" style="text-align:right;">{{ pct(r.attendance_rate) }}</td>
                      <td class="tbl__name tnum" style="text-align:right;">{{ score(r.average_score) }}</td>
                      <td style="text-align:right;"><SkBadge v-bind="healthMeta(r.health_status)" /></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- SESSIONS -->
            <div v-else-if="tab === 'sessions'">
              <div class="block__head">
                <div>
                  <div class="block__title">Buổi học · {{ sessions.length }}</div>
                  <div class="block__hint">Sinh lịch theo mẫu 2-4-6, 3-5-7 hoặc T7-CN từ ngày khai giảng.</div>
                </div>
                <SkButton variant="secondary" :loading="generatingSessions" @click="generateSessions">Sinh lịch</SkButton>
              </div>
              <div v-if="!sessions.length" class="muted">Chưa sinh lịch buổi học.</div>
              <div class="sess">
                <div v-for="(s, i) in sessions" :key="s.name" class="sess__row" :class="{ 'sess__row--today': isToday(s.session_date) }">
                  <div class="sess__no">Buổi {{ i + 1 }}</div>
                  <div class="sess__main">
                    <div class="sess__topic">{{ s.lesson_topic || 'Chưa có chủ đề' }}</div>
                    <div class="sess__date tnum">{{ formatDate(s.session_date) }} · {{ formatTime(s.start_time) }}</div>
                  </div>
                  <SkBadge v-bind="sesMeta(s.session_status)" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>

    <SkModal v-model="classOpen" title="Thêm lớp học" width="620px">
      <form class="form" @submit.prevent="saveClass">
        <div class="form-grid">
          <label class="fg fg--full">
            <span>Tên lớp</span>
            <input v-model.trim="classForm.class_name" class="field" required placeholder="N5-TP-001" />
          </label>
          <label class="fg">
            <span>Khóa học</span>
            <select v-model="classForm.course" class="field" required>
              <option value="" disabled>Chọn khóa học</option>
              <option v-for="course in courseOptions" :key="course.name" :value="course.name">
                {{ course.course_name || course.name }}
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Giáo viên</span>
            <select v-model="classForm.teacher" class="field">
              <option value="">Chưa gán</option>
              <option v-for="teacher in teacherOptions" :key="teacher.name" :value="teacher.name">
                {{ teacher.teacher_name || teacher.name }}
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Ngày khai giảng</span>
            <input v-model="classForm.start_date" class="field" type="date" />
          </label>
          <label class="fg">
            <span>Mẫu lịch</span>
            <select v-model="classForm.schedule_template" class="field">
              <option value=""></option>
              <option value="2-4-6">2-4-6</option>
              <option value="3-5-7">3-5-7</option>
              <option value="T7-CN">T7-CN</option>
              <option value="Custom">Custom</option>
            </select>
          </label>
          <label class="fg">
            <span>Giờ bắt đầu</span>
            <input v-model="classForm.start_time" class="field" type="time" />
          </label>
          <label class="fg">
            <span>Giờ kết thúc</span>
            <input v-model="classForm.end_time" class="field" type="time" />
          </label>
          <label class="fg">
            <span>Tổng số buổi</span>
            <input v-model.number="classForm.total_sessions" class="field" type="number" min="0" placeholder="30" />
          </label>
          <label class="fg">
            <span>Sĩ số tối đa</span>
            <input v-model.number="classForm.max_capacity" class="field" type="number" min="0" placeholder="18" />
          </label>
          <label class="fg">
            <span>Học phí chuẩn</span>
            <input v-model.number="classForm.standard_fee" class="field" type="number" min="0" step="1000" placeholder="4500000" />
          </label>
          <label class="fg">
            <span>Trạng thái</span>
            <select v-model="classForm.status" class="field">
              <option value="Upcoming">Upcoming</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Completed">Completed</option>
              <option value="Closed">Closed</option>
            </select>
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingClass" @click="classOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingClass" @click="saveClass">Lưu lớp</SkButton>
      </template>
    </SkModal>

    <SkModal v-model="enrollmentOpen" title="Gán học viên vào lớp" width="600px">
      <form class="form" @submit.prevent="saveEnrollment">
        <div class="form-grid">
          <label class="fg fg--full">
            <span>Học viên</span>
            <select v-model="enrollmentForm.student" class="field" required>
              <option value="">Chọn học viên</option>
              <option v-for="s in availableStudents" :key="s.name" :value="s.name">
                {{ s.full_name || s.name }} · {{ s.phone || s.email || s.name }}
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Ngày nhập học</span>
            <input v-model="enrollmentForm.enrollment_date" class="field" type="date" required />
          </label>
          <label class="fg">
            <span>Loại đăng ký</span>
            <select v-model="enrollmentForm.enrollment_type" class="field">
              <option value="Official">Official</option>
              <option value="Trial">Trial</option>
            </select>
          </label>
          <label class="fg">
            <span>Giá niêm yết</span>
            <input v-model.number="enrollmentForm.list_price" class="field" type="number" min="0" step="1000" />
          </label>
          <label class="fg">
            <span>Loại ưu đãi</span>
            <select v-model="enrollmentForm.discount_type" class="field">
              <option value=""></option>
              <option value="Percent">Percent</option>
              <option value="Amount">Amount</option>
            </select>
          </label>
          <label class="fg">
            <span>Giá trị ưu đãi</span>
            <input v-model.number="enrollmentForm.discount_value" class="field" type="number" min="0" step="1000" />
          </label>
          <label class="fg fg--full">
            <span>Lý do ưu đãi</span>
            <textarea v-model.trim="enrollmentForm.discount_reason" class="field field--area" placeholder="Ví dụ: ưu đãi học viên cũ, duyệt bởi..." />
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingEnrollment" @click="enrollmentOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingEnrollment" @click="saveEnrollment">Gán vào lớp</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call, db } from '../api'
import { formatVND, formatDate, formatTime } from '../utils/format'
import { statusMeta } from '../utils/labels'
import { toast } from '../utils/toast'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkModal from '../components/ui/SkModal.vue'
import SkState from '../components/ui/SkState.vue'

const TABS = [
  { id: 'overview', label: 'Tổng quan' },
  { id: 'roster', label: 'Học viên' },
  { id: 'sessions', label: 'Buổi học' },
]

const loading = ref(true)
const classes = ref([])
const selectedId = ref(null)
const tab = ref('overview')
const detailLoading = ref(false)
const cur = reactive({})
const roster = ref([])
const sessions = ref([])
const today = () => new Date().toISOString().slice(0, 10)
const classOpen = ref(false)
const savingClass = ref(false)
const enrollmentOpen = ref(false)
const savingEnrollment = ref(false)
const generatingSessions = ref(false)
const courseOptions = ref([])
const teacherOptions = ref([])
const studentOptions = ref([])
const classForm = ref(defaultClassForm())
const enrollmentForm = ref(defaultEnrollmentForm())

const clsMeta = (s) => statusMeta('Class', 'status', s)
const sesMeta = (s) => statusMeta('Class Session', 'session_status', s)
const healthMeta = (s) => statusMeta('Student', 'health_status', s)
const enrMeta = (s) => {
  const map = { Active: 'success', Pending: 'warning', Deferred: 'warning', Completed: 'neutral', Dropped: 'danger', Transferred: 'info', Rejected: 'danger' }
  return { label: s || '—', variant: map[s] || 'neutral' }
}
const pct = (v) => `${Math.round(Number(v) || 0)}%`
const score = (v) => (v == null || v === '' ? '—' : Number(v).toFixed(1))
const todayIso = new Date().toISOString().slice(0, 10)
const isToday = (d) => d === todayIso

const schedule = computed(() => {
  const t = cur.schedule_template ? cur.schedule_template + ' · ' : ''
  const h = cur.start_time ? `${formatTime(cur.start_time)}–${formatTime(cur.end_time)}` : ''
  return (t + h) || '—'
})
const completedSessions = computed(() => sessions.value.filter((s) => s.session_status === 'Completed').length)
const feeStats = computed(() => {
  const total = roster.value.reduce((sum, r) => sum + (Number(r.invoice_total || r.net_fee) || 0), 0)
  const paid = roster.value.reduce((sum, r) => sum + (Number(r.paid_amount) || 0), 0)
  const outstanding = roster.value.reduce((sum, r) => sum + (Number(r.outstanding_amount) || 0), 0)
  return { total, paid, outstanding }
})
const availableStudents = computed(() => {
  const assigned = new Set(roster.value.map((r) => r.student))
  return studentOptions.value.filter((s) => !assigned.has(s.name))
})

function defaultClassForm() {
  return {
    class_name: '',
    course: '',
    teacher: '',
    start_date: '',
    schedule_template: '',
    start_time: '',
    end_time: '',
    total_sessions: '',
    max_capacity: '',
    standard_fee: '',
    status: 'Upcoming',
  }
}

function defaultEnrollmentForm() {
  return {
    student: '',
    enrollment_date: today(),
    enrollment_type: 'Official',
    list_price: Number(cur.standard_fee) || '',
    discount_type: '',
    discount_value: 0,
    discount_reason: '',
  }
}

function cleanPayload(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== '' && value != null))
}

async function loadFormOptions() {
  try {
    const [courses, teachers, students] = await Promise.all([
      db.getList('Course', {
        fields: ['name', 'course_name', 'base_fee'],
        order_by: 'modified desc',
        limit_page_length: 100,
      }),
      db.getList('Teacher', {
        fields: ['name', 'teacher_name', 'status'],
        filters: { status: 'Active' },
        order_by: 'modified desc',
        limit_page_length: 100,
      }),
      db.getList('Student', {
        fields: ['name', 'full_name', 'phone', 'email', 'student_status'],
        order_by: 'modified desc',
        limit_page_length: 200,
      }),
    ])
    courseOptions.value = courses || []
    teacherOptions.value = teachers || []
    studentOptions.value = students || []
  } catch (e) {
    courseOptions.value = []
    teacherOptions.value = []
    studentOptions.value = []
  }
}

function openClass() {
  classForm.value = defaultClassForm()
  if (!courseOptions.value.length) loadFormOptions()
  classOpen.value = true
}

async function saveClass() {
  if (!classForm.value.class_name || !classForm.value.course) {
    toast.error('Thiếu thông tin lớp', 'Cần nhập tên lớp và chọn khóa học.')
    return
  }
  savingClass.value = true
  try {
    const created = await db.insert({ doctype: 'Class', ...cleanPayload(classForm.value) })
    toast.success('Đã thêm lớp')
    classOpen.value = false
    await load()
    if (created?.name) select(created.name)
  } catch (e) {
    toast.error('Không thêm được lớp', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingClass.value = false
  }
}

async function openEnrollment() {
  if (!selectedId.value) return
  if (!studentOptions.value.length) await loadFormOptions()
  enrollmentForm.value = defaultEnrollmentForm()
  try {
    const info = await call('get_class_enrollment_info', { class_id: selectedId.value })
    if (info?.list_price) enrollmentForm.value.list_price = info.list_price
  } catch (e) {
    /* keep class standard fee fallback */
  }
  enrollmentOpen.value = true
}

async function saveEnrollment() {
  if (!selectedId.value || !enrollmentForm.value.student) {
    toast.error('Thiếu học viên')
    return
  }
  savingEnrollment.value = true
  try {
    await call('create_enrollment', {
      ...cleanPayload(enrollmentForm.value),
      class_id: selectedId.value,
      submit: 1,
    })
    toast.success('Đã gán học viên vào lớp')
    enrollmentOpen.value = false
    tab.value = 'roster'
    classes.value = (await call('get_classes')) || classes.value
    await loadDetail(selectedId.value)
  } catch (e) {
    toast.error('Không gán được học viên', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingEnrollment.value = false
  }
}

async function generateSessions() {
  if (!selectedId.value) return
  generatingSessions.value = true
  try {
    const message = await call('generate_class_sessions', { class_id: selectedId.value })
    toast.success('Đã sinh lịch', message)
    tab.value = 'sessions'
    await loadDetail(selectedId.value)
  } catch (e) {
    toast.error('Không sinh được lịch', e?.messages?.[0] || e?.message || String(e))
  } finally {
    generatingSessions.value = false
  }
}

async function loadDetail(id) {
  detailLoading.value = true
  roster.value = []
  sessions.value = []
  try {
    const [rows, rost, sess] = await Promise.all([
      db.getList('Class', {
        filters: { name: id },
        fields: ['class_name', 'course', 'teacher', 'substitute_teacher', 'classroom', 'start_date',
          'schedule_template', 'start_time', 'end_time', 'total_sessions', 'max_capacity',
          'standard_fee', 'status', 'progress'],
        limit_page_length: 1,
      }),
      call('get_class_roster', { class_id: id }),
      call('get_class_sessions', { class_id: id }),
    ])
    Object.assign(cur, rows?.[0] || {})
    roster.value = rost || []
    sessions.value = sess || []
  } catch (e) {
    /* empty */
  } finally {
    detailLoading.value = false
  }
}

function select(id) {
  selectedId.value = id
  tab.value = 'overview'
  loadDetail(id)
}

async function load() {
  loading.value = true
  try {
    classes.value = (await call('get_classes')) || []
    if (classes.value.length) select(classes.value[0].name)
  } finally {
    loading.value = false
  }
}
onMounted(() => {
  load()
  loadFormOptions()
})
</script>

<style scoped>
.md { flex: 1; min-width: 0; display: flex; height: 100vh; }
.ctx { flex: none; width: 326px; display: flex; flex-direction: column; background: rgba(255, 252, 253, 0.82); border-right: 1px solid #f2d4df; }
.ctx__head { height: 56px; flex: none; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 0 18px; border-bottom: 1px solid #f4dde5; }
.ctx__title { font-size: 16px; font-weight: 600; color: #4a2230; }
.ctx__meta { display: flex; align-items: center; gap: 8px; }
.ctx__count { font-size: 11.5px; color: #a98c98; }
.ctx__list { flex: 1; overflow-y: auto; padding: 8px 0; }

.crow { display: block; width: 100%; text-align: left; border: none; border-bottom: 1px solid #f7e6ec; background: transparent; padding: 12px 16px 12px 13px; cursor: pointer; border-left: 3px solid transparent; font-family: inherit; }
.crow:hover { background: #fdf2f6; }
.crow--active { background: #fbd9e5; border-left-color: #d6557e; }
.crow__top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.crow__id { font-size: 13.5px; font-weight: 600; color: #3d2530; }
.crow__sub { font-size: 11.5px; color: #a98c98; margin-top: 4px; }
.crow__bar { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.crow__track { flex: 1; height: 5px; border-radius: 3px; background: #f6dde6; overflow: hidden; }
.crow__track > span { display: block; height: 100%; background: linear-gradient(90deg, #f7a8c4, #d6557e); border-radius: 3px; }
.crow__pct { font-size: 11px; color: #b8456a; font-weight: 600; }

.dtl { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; }
.dtl__head { height: 56px; flex: none; display: flex; align-items: center; gap: 11px; padding: 0 18px; border-bottom: 1px solid #f1dbe3; }
.dtl__id { min-width: 0; display: flex; align-items: center; gap: 9px; }
.dtl__name { font-size: 16px; font-weight: 600; color: #3d2530; }
.dtl__slash { font-size: 13px; color: #bd97a5; }
.dtl__code { font-size: 13px; color: #a98c98; }
.dtl__actions { margin-left: auto; display: flex; gap: 8px; }
.dtl__tabs { flex: none; display: flex; align-items: center; padding: 0 24px; border-bottom: 1px solid #f1dbe3; }
.tab { border: none; background: none; padding: 13px 2px 12px; margin-right: 28px; cursor: pointer; font-family: inherit; font-size: 13.5px; font-weight: 500; color: #7a5c68; border-bottom: 2px solid transparent; }
.tab--active { color: #b8456a; font-weight: 600; border-bottom-color: #d6557e; }
.dtl__body { flex: 1; overflow-y: auto; }
.dtl__inner { padding: 26px 30px 44px; max-width: 1080px; }

.stack { display: flex; flex-direction: column; gap: 28px; }
.grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.block__head { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-bottom: 14px; }
.block__title { font-size: 15px; font-weight: 600; color: #4a2230; margin-bottom: 14px; }
.block__head .block__title { margin-bottom: 0; }
.block__hint { font-size: 12px; color: #a98c98; margin-top: 3px; }
.info { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px 32px; }
.info__l { font-size: 11.5px; color: #a98c98; margin-bottom: 3px; }
.info__v { font-size: 14px; color: #3d2530; font-weight: 500; }
.muted { font-size: 13px; color: #a98c98; }

.progcard { border: 1px solid #f3d9e1; border-radius: 12px; padding: 16px 18px; background: linear-gradient(135deg, #fdeef4, #fbe0ea); }
.progcard__top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.progcard__label { font-size: 13px; color: #a8607b; font-weight: 500; }
.progcard__pct { font-size: 14px; color: #b8456a; font-weight: 700; }
.progcard__bar { height: 8px; border-radius: 5px; background: rgba(255, 255, 255, 0.6); overflow: hidden; }
.progcard__bar > span { display: block; height: 100%; background: linear-gradient(90deg, #f7a8c4, #d6557e); border-radius: 5px; }

.flowgrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.flowcard { min-height: 112px; border: 1px solid #f3d9e1; border-radius: 11px; background: #fff; padding: 14px 15px; display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between; text-align: left; font-family: inherit; color: inherit; }
button.flowcard { cursor: pointer; }
button.flowcard:hover { border-color: #ecbcce; background: #fff7fa; }
.flowcard__label { font-size: 11.5px; color: #a98c98; font-weight: 600; }
.flowcard strong { font-size: 18px; color: #3d2530; line-height: 1.2; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.flowcard small { font-size: 11.5px; color: #a98c98; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.fee-mini { margin-bottom: 14px; }
.fee-mini > div { border: 1px solid #f3d9e1; border-radius: 10px; background: #fff; padding: 12px 14px; }
.fee-mini span { display: block; font-size: 11.5px; color: #a98c98; margin-bottom: 4px; }
.fee-mini strong { font-size: 15px; color: #3d2530; }

.tblwrap { border: 1px solid #f3d9e1; border-radius: 11px; overflow: hidden; background: #fff; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl thead tr { background: #fdf2f6; }
.tbl th { text-align: left; font-size: 11.5px; font-weight: 600; color: #a07c8a; padding: 10px 16px; }
.tbl td { padding: 9px 16px; border-top: 1px solid #f6e3ea; }
.tbl tbody tr:hover { background: #fefafb; }
.tbl__name { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.tbl__sub { font-size: 13px; color: #7a5c68; }
.cell-av { display: flex; align-items: center; gap: 10px; }

.sess { display: flex; flex-direction: column; gap: 10px; }
.sess__row { display: flex; align-items: center; gap: 14px; border: 1px solid #f3d9e1; border-radius: 11px; padding: 13px 16px; background: #fff; }
.sess__row--today { background: linear-gradient(135deg, #fdeef4, #fbe0ea); border-color: #f0b9cd; }
.sess__no { flex: none; width: 62px; font-size: 13.5px; font-weight: 600; color: #3d2530; }
.sess__main { flex: 1; min-width: 0; }
.sess__topic { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.sess__date { font-size: 12px; color: #a98c98; margin-top: 2px; }

.form { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg--full { grid-column: 1 / -1; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field--area { height: auto; min-height: 74px; padding: 9px 11px; resize: vertical; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }

@media (max-width: 1180px) {
  .flowgrid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .info { grid-template-columns: repeat(2, 1fr); }
}
</style>
