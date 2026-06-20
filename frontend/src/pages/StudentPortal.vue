<template>
  <div class="ws sk-scroll">
    <SkState v-if="loading" state="loading" />
    <SkState v-else-if="error" state="denied" title="Không truy cập được cổng học viên" :message="error" />

    <div v-else class="phone sk-anim-pop">
      <div class="ph-head">
        <div class="ph-head__top">
          <SkAvatar :name="name" :src="p.student_image" :size="46" />
          <div>
            <div class="ph-head__hi">Xin chào,</div>
            <div class="ph-head__name font-display">{{ name }}</div>
          </div>
        </div>
        <div class="ph-card">
          <div class="ph-card__eyebrow">Tiến độ khóa học</div>
          <div class="ph-card__big">{{ p.progress || '—' }}</div>
          <div class="ph-card__sub">{{ p.health_status || 'Đang học' }}</div>
        </div>
      </div>

      <div class="ph-body">
        <div class="ph-stats">
          <button class="ph-stat" @click="activeTab = 'schedule'">
            <div class="ph-stat__v tnum" style="color:#b8456a;">{{ pct(p.attendance_rate) }}</div>
            <div class="ph-stat__l">Chuyên cần</div>
          </button>
          <button class="ph-stat" @click="activeTab = 'results'">
            <div class="ph-stat__v tnum" style="color:#3d2530;">{{ score(p.average_score) }}</div>
            <div class="ph-stat__l">Điểm TB</div>
          </button>
          <button class="ph-stat" @click="activeTab = 'homework'">
            <div class="ph-stat__v tnum" style="color:#c98a2e;">{{ pendingHomework }}</div>
            <div class="ph-stat__l">Cần làm</div>
          </button>
        </div>

        <section v-if="activeTab === 'home'" class="ph-screen">
          <div class="ph-section">Sắp tới</div>
          <button v-if="nextSession" class="ph-row ph-row--button" @click="activeTab = 'schedule'">
            <div>
              <div class="ph-row__title">{{ nextSession.class_name || nextSession.class_id }} · {{ nextSession.lesson_topic || 'Buổi học' }}</div>
              <div class="ph-row__sub">{{ formatDate(nextSession.session_date) }} · {{ formatTime(nextSession.start_time) }}</div>
            </div>
            <FeatherIcon name="chevron-right" class="ph-chevron" />
          </button>
          <div v-else class="ph-muted">Chưa có lịch học sắp tới.</div>

          <div class="ph-section">Bài tập cần làm</div>
          <div class="ph-list">
            <div v-if="!homeworkPreview.length" class="ph-muted">Không có bài tập đang chờ.</div>
            <button v-for="h in homeworkPreview" :key="h.name" class="ph-row ph-row--button" @click="openHomework(h)">
              <div>
                <div class="ph-row__title">{{ h.title }}</div>
                <div class="ph-row__sub">Hạn {{ formatDate(h.due_date) }} · {{ h.class_name || h.class_id }}</div>
              </div>
              <SkBadge v-bind="homeworkMeta(h)" />
            </button>
          </div>

          <button class="ph-fee" @click="openInvoice(nextInvoice)">
            <div>
              <div class="ph-fee__label">Học phí còn lại</div>
              <div class="ph-fee__amount tnum">{{ formatVND(outstanding) }}</div>
            </div>
            <span class="ph-fee__cta">Xem</span>
          </button>
        </section>

        <section v-else-if="activeTab === 'schedule'" class="ph-screen">
          <div class="ph-section">Lịch học</div>
          <div class="ph-list">
            <div v-if="!data.sessions.length" class="ph-muted">Chưa có lịch học sắp tới.</div>
            <div v-for="s in data.sessions" :key="s.name" class="ph-row">
              <div class="ph-date">
                <span>{{ dayOfMonth(s.session_date) }}</span>
                <small>{{ monthOf(s.session_date) }}</small>
              </div>
              <div class="ph-row__main">
                <div class="ph-row__title">{{ s.class_name || s.class_id }} · {{ s.lesson_topic || 'Buổi học' }}</div>
                <div class="ph-row__sub">{{ formatTime(s.start_time) }} - {{ formatTime(s.end_time) }}</div>
              </div>
              <SkBadge variant="info" :label="s.session_status || 'Scheduled'" />
            </div>
          </div>
        </section>

        <section v-else-if="activeTab === 'homework'" class="ph-screen">
          <div class="ph-section">Bài tập</div>
          <div class="ph-list">
            <div v-if="!data.homework.length" class="ph-muted">Chưa có bài tập nào.</div>
            <button v-for="h in data.homework" :key="h.name" class="ph-row ph-row--button" @click="openHomework(h)">
              <div>
                <div class="ph-row__title">{{ h.title }}</div>
                <div class="ph-row__sub">Hạn {{ formatDate(h.due_date) }} · {{ h.class_name || h.class_id }}</div>
              </div>
              <SkBadge v-bind="homeworkMeta(h)" />
            </button>
          </div>
        </section>

        <section v-else-if="activeTab === 'results'" class="ph-screen">
          <div class="ph-section">Kết quả học tập</div>
          <div class="ph-list">
            <div v-if="!data.recent_assessments.length" class="ph-muted">Chưa có điểm.</div>
            <div v-for="a in data.recent_assessments" :key="`${a.assessment_name}-${a.assessment_type}`" class="ph-row">
              <div>
                <div class="ph-row__title">{{ a.assessment_name || 'Đánh giá' }}</div>
                <div class="ph-row__sub">{{ a.assessment_type || '—' }}</div>
              </div>
              <div class="ph-score tnum">{{ normalized(a) }}</div>
            </div>
          </div>
        </section>

        <section v-else class="ph-screen">
          <div class="ph-section">Tài khoản</div>
          <div class="ph-profile">
            <div><span>Mã học viên</span><strong>{{ data.student }}</strong></div>
            <div><span>Tình trạng</span><strong>{{ p.health_status || '—' }}</strong></div>
            <div><span>Lớp đang học</span><strong>{{ activeEnrollment?.class_id || '—' }}</strong></div>
          </div>

          <div class="ph-section">Tài liệu</div>
          <div class="ph-list">
            <div v-if="!data.materials.length" class="ph-muted">Chưa có tài liệu công khai.</div>
            <button v-for="m in data.materials" :key="m.name" class="ph-row ph-row--button" @click="openMaterial(m)">
              <div>
                <div class="ph-row__title">{{ m.title }}</div>
                <div class="ph-row__sub">{{ m.material_type || 'Tài liệu' }} · {{ m.class_id || m.course || '—' }}</div>
              </div>
              <FeatherIcon name="external-link" class="ph-chevron" />
            </button>
          </div>

          <div class="ph-section">Hóa đơn</div>
          <div class="ph-list">
            <div v-if="!data.invoices.length" class="ph-muted">Chưa có hóa đơn.</div>
            <button v-for="i in data.invoices" :key="i.name" class="ph-row ph-row--button" @click="openInvoice(i)">
              <div>
                <div class="ph-row__title">{{ i.name }}</div>
                <div class="ph-row__sub">Hạn {{ formatDate(i.due_date) }}</div>
              </div>
              <div class="ph-invoice tnum">{{ formatVND(i.outstanding_amount) }}</div>
            </button>
          </div>
        </section>
      </div>

      <div class="ph-nav">
        <button
          v-for="n in nav"
          :key="n.id"
          class="ph-nav__item"
          :class="{ 'ph-nav__item--active': activeTab === n.id }"
          @click="activeTab = n.id"
        >
          <FeatherIcon :name="n.icon" style="width:20px;height:20px;" />
          <span>{{ n.label }}</span>
        </button>
      </div>
    </div>

    <SkModal v-model="homeworkOpen" title="Bài tập" width="520px">
      <div v-if="selectedHomework" class="modal-stack">
        <div>
          <div class="modal-title">{{ selectedHomework.title }}</div>
          <div class="modal-sub">Hạn {{ formatDate(selectedHomework.due_date) }} · {{ selectedHomework.class_name || selectedHomework.class_id }}</div>
        </div>
        <div v-if="selectedHomework.description" class="modal-box">{{ selectedHomework.description }}</div>
        <a v-if="selectedHomework.materials" class="modal-link" :href="selectedHomework.materials" target="_blank" rel="noreferrer">
          Mở tài liệu
        </a>
        <label class="fg">
          <span>Nội dung nộp / đường dẫn bài làm</span>
          <textarea v-model.trim="homeworkContent" class="field field--area" placeholder="Dán link Drive, ghi chú bài làm..." />
        </label>
        <div v-if="selectedHomework.submission" class="modal-box modal-box--ok">
          Đã nộp {{ formatDate(selectedHomework.submission.submission_date) }}
          <span v-if="selectedHomework.submission.grade">· Điểm {{ selectedHomework.submission.grade }}</span>
        </div>
      </div>
      <template #footer>
        <SkButton variant="secondary" :disabled="submittingHomework" @click="homeworkOpen = false">Đóng</SkButton>
        <SkButton variant="solid" :loading="submittingHomework" @click="submitHomework">Nộp bài</SkButton>
      </template>
    </SkModal>

    <SkModal v-model="invoiceOpen" title="Chi tiết hóa đơn" width="440px">
      <div v-if="selectedInvoice" class="modal-stack">
        <div>
          <div class="modal-title">{{ selectedInvoice.name }}</div>
          <div class="modal-sub">Hạn {{ formatDate(selectedInvoice.due_date) }}</div>
        </div>
        <div class="ph-profile">
          <div><span>Tổng tiền</span><strong>{{ formatVND(selectedInvoice.total_amount) }}</strong></div>
          <div><span>Còn lại</span><strong>{{ formatVND(selectedInvoice.outstanding_amount) }}</strong></div>
          <div><span>Trạng thái</span><strong>{{ selectedInvoice.status }}</strong></div>
        </div>
        <div class="modal-box">Vui lòng thanh toán theo hướng dẫn của trung tâm hoặc liên hệ giáo vụ để xác nhận giao dịch.</div>
      </div>
      <template #footer>
        <SkButton variant="solid" @click="invoiceOpen = false">Đã hiểu</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call } from '../api'
import { formatVND, formatDate, formatTime } from '../utils/format'
import { toast } from '../utils/toast'
import SkBadge from '../components/ui/SkBadge.vue'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkModal from '../components/ui/SkModal.vue'
import SkState from '../components/ui/SkState.vue'

const loading = ref(true)
const error = ref('')
const activeTab = ref('home')
const data = reactive({
  student: '',
  profile: {},
  enrollments: [],
  homework: [],
  invoices: [],
  recent_assessments: [],
  sessions: [],
  materials: [],
})

const homeworkOpen = ref(false)
const selectedHomework = ref(null)
const homeworkContent = ref('')
const submittingHomework = ref(false)

const invoiceOpen = ref(false)
const selectedInvoice = ref(null)

const p = computed(() => data.profile || {})
const name = computed(() => p.value.full_name || 'Học viên')
const outstanding = computed(() => (data.invoices || []).reduce((s, i) => s + (Number(i.outstanding_amount) || 0), 0))
const pendingHomework = computed(() => data.homework.filter((h) => !h.submission).length)
const homeworkPreview = computed(() => data.homework.filter((h) => !h.submission).slice(0, 3))
const nextSession = computed(() => data.sessions[0])
const nextInvoice = computed(() => data.invoices.find((i) => Number(i.outstanding_amount) > 0) || data.invoices[0] || null)
const activeEnrollment = computed(() => data.enrollments.find((e) => e.enrollment_status === 'Active') || data.enrollments[0])

const pct = (v) => `${Math.round(Number(v) || 0)}%`
const score = (v) => (v == null || v === '' ? '—' : Number(v).toFixed(1))
const normalized = (a) => {
  const max = Number(a.max_score) || 100
  return max ? `${Math.round((Number(a.score) / max) * 100)}%` : '—'
}
const homeworkMeta = (h) => h.submission ? { label: 'Đã nộp', variant: 'success' } : { label: 'Cần làm', variant: 'warning' }

const nav = [
  { id: 'home', icon: 'home', label: 'Trang chủ' },
  { id: 'schedule', icon: 'calendar', label: 'Lịch' },
  { id: 'homework', icon: 'file-text', label: 'Bài tập' },
  { id: 'results', icon: 'bar-chart-2', label: 'Kết quả' },
  { id: 'account', icon: 'user', label: 'Tài khoản' },
]

function dayOfMonth(date) {
  const d = formatDate(date)
  return d === '—' ? '--' : d.slice(0, 2)
}
function monthOf(date) {
  const d = formatDate(date)
  return d === '—' ? '--' : `T${Number(d.slice(3, 5))}`
}
function openHomework(homework) {
  selectedHomework.value = homework
  homeworkContent.value = homework.submission?.content || ''
  homeworkOpen.value = true
}
async function submitHomework() {
  if (!selectedHomework.value) return
  submittingHomework.value = true
  try {
    await call('submit_my_homework', { homework: selectedHomework.value.name, content: homeworkContent.value })
    toast.success('Đã nộp bài')
    homeworkOpen.value = false
    await load()
    activeTab.value = 'homework'
  } catch (e) {
    toast.error('Không nộp được bài', e?.messages?.[0] || e?.message || String(e))
  } finally {
    submittingHomework.value = false
  }
}
function openInvoice(invoice) {
  if (!invoice) return
  selectedInvoice.value = invoice
  invoiceOpen.value = true
}
function openMaterial(material) {
  if (material?.url) window.open(material.url, '_blank')
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    Object.assign(data, {
      student: '',
      profile: {},
      enrollments: [],
      homework: [],
      invoices: [],
      recent_assessments: [],
      sessions: [],
      materials: [],
    }, (await call('get_my_student_overview')) || {})
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.ws { flex: 1; min-width: 0; height: 100vh; overflow-y: auto; background: linear-gradient(140deg, #fce3ec, #f7d3e0); display: flex; justify-content: center; padding: 28px 16px; }
.phone { width: 420px; flex: none; border-radius: 34px; background: #fff; box-shadow: 0 24px 60px rgba(160, 60, 100, 0.28); overflow: hidden; border: 7px solid #2a1620; min-height: 720px; display: flex; flex-direction: column; }
.ph-head { background: linear-gradient(150deg, #e87aa3, #d4567f); padding: 22px 20px 24px; color: #fff; }
.ph-head__top { display: flex; align-items: center; gap: 12px; }
.ph-head__hi { font-size: 12px; opacity: 0.85; }
.ph-head__name { font-size: 18px; font-weight: 700; }
.ph-card { margin-top: 18px; background: rgba(255, 255, 255, 0.16); border-radius: 14px; padding: 14px 16px; backdrop-filter: blur(4px); }
.ph-card__eyebrow { font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }
.ph-card__big { font-size: 15px; font-weight: 600; margin-top: 5px; }
.ph-card__sub { font-size: 12.5px; opacity: 0.9; margin-top: 3px; }

.ph-body { flex: 1; min-height: 0; padding: 18px 18px 10px; overflow-y: auto; }
.ph-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 18px; }
.ph-stat { border: 1px solid #f3d9e1; border-radius: 12px; padding: 12px 10px; text-align: center; background: #fff; cursor: pointer; font-family: inherit; }
.ph-stat:hover { background: #fff7fa; border-color: #ecbcce; }
.ph-stat__v { font-size: 20px; font-weight: 700; }
.ph-stat__l { font-size: 10.5px; color: #a98c98; margin-top: 2px; }
.ph-screen { display: flex; flex-direction: column; gap: 10px; }
.ph-section { font-size: 13.5px; font-weight: 600; color: #4a2230; margin: 6px 0 1px; }
.ph-list { display: flex; flex-direction: column; gap: 8px; }
.ph-muted { font-size: 12.5px; color: #a98c98; padding: 4px 0 10px; }
.ph-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; border: 1px solid #f3d9e1; border-radius: 10px; padding: 11px 13px; background: #fff; width: 100%; text-align: left; font-family: inherit; }
.ph-row--button { cursor: pointer; }
.ph-row--button:hover { background: #fff7fa; border-color: #ecbcce; }
.ph-row__main { flex: 1; min-width: 0; }
.ph-row__title { font-size: 13px; font-weight: 600; color: #3d2530; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ph-row__sub { font-size: 11px; color: #a98c98; margin-top: 2px; }
.ph-chevron { flex: none; width: 16px; height: 16px; color: #bd97a5; }
.ph-date { width: 42px; height: 42px; border-radius: 11px; background: #fdf2f6; color: #b8456a; display: flex; flex-direction: column; align-items: center; justify-content: center; flex: none; }
.ph-date span { font-size: 15px; font-weight: 800; line-height: 1; }
.ph-date small { font-size: 10px; margin-top: 3px; }
.ph-score { font-size: 18px; font-weight: 800; color: #b8456a; }
.ph-invoice { font-size: 12.5px; font-weight: 700; color: #c43232; white-space: nowrap; }

.ph-fee { border: 1px solid #f3cdc9; background: #fdeeec; border-radius: 12px; padding: 13px 15px; display: flex; align-items: center; justify-content: space-between; margin-top: 8px; cursor: pointer; font-family: inherit; text-align: left; }
.ph-fee__label { font-size: 11.5px; color: #b06860; }
.ph-fee__amount { font-size: 17px; font-weight: 700; color: #c43232; margin-top: 2px; }
.ph-fee__cta { color: #b8456a; font-size: 12px; font-weight: 700; background: #fff; border-radius: 7px; padding: 6px 10px; }
.ph-profile { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; overflow: hidden; }
.ph-profile > div { display: flex; justify-content: space-between; gap: 12px; padding: 11px 13px; border-bottom: 1px solid #f7e6ec; }
.ph-profile > div:last-child { border-bottom: none; }
.ph-profile span { font-size: 12px; color: #a98c98; }
.ph-profile strong { font-size: 12.5px; color: #3d2530; text-align: right; }

.ph-nav { display: flex; border-top: 1px solid #f4dde5; padding: 8px 6px 10px; background: #fff; }
.ph-nav__item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; border: none; background: transparent; color: #bd97a5; cursor: pointer; font-family: inherit; padding: 5px 0; border-radius: 10px; }
.ph-nav__item span { font-size: 10px; }
.ph-nav__item--active { color: #d4567f; background: #fdf2f6; }

.modal-stack { display: flex; flex-direction: column; gap: 14px; }
.modal-title { font-size: 16px; font-weight: 700; color: #3d2530; }
.modal-sub { font-size: 12.5px; color: #a98c98; margin-top: 3px; }
.modal-box { border: 1px solid #f3d9e1; border-radius: 10px; background: #fff; padding: 12px 13px; color: #7a5c68; font-size: 13px; white-space: pre-wrap; }
.modal-box--ok { background: #e4f3ea; border-color: #c9e7d5; color: #2f8a5d; }
.modal-link { color: #b8456a; text-decoration: none; font-size: 13px; font-weight: 700; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; min-height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field--area { min-height: 88px; resize: vertical; padding: 9px 11px; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }
</style>
