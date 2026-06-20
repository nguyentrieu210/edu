<template>
  <SkModal
    :model-value="modelValue"
    :title="`Ghi nhận kết quả · ${STEP_LABEL[currentStep]}`"
    width="560px"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <div v-if="lead" class="stage-lead">
      <SkAvatar :name="lead.lead_name" :src="lead.lead_image" :size="34" />
      <div class="stage-lead__meta">
        <span class="stage-lead__name">{{ lead.lead_name }}</span>
        <span class="stage-lead__sub">{{ lead.phone || lead.email || '—' }}</span>
      </div>
    </div>

    <form class="form" @submit.prevent="submit">
      <!-- ===== Thông tin bước hiện tại ===== -->
      <div class="sec">
        <div class="sec__title">{{ currentStep === 'Testing' ? 'Kết quả test đầu vào' : (currentStep === 'Trial' ? 'Nhận xét buổi học thử' : 'Nội dung tư vấn') }}</div>
        <div class="form-grid">
          <!-- Tư vấn / Học thử -->
          <template v-if="currentStep !== 'Testing'">
            <label class="fg">
              <span>Ngày liên hệ</span>
              <input v-model="f.contact_date" class="field" type="date" />
            </label>
            <label class="fg">
              <span>Kết quả đánh giá</span>
              <select v-model="f.result" class="field">
                <option v-for="r in RESULT_OPTIONS" :key="r" :value="r">{{ r || '— Chọn mức —' }}</option>
              </select>
            </label>
            <label class="fg fg--full">
              <span>{{ currentStep === 'Trial' ? 'Nhận xét buổi học thử' : 'Nội dung trao đổi' }}</span>
              <textarea v-model="f.notes" class="field field--area" placeholder="Nhu cầu, mức độ quan tâm, trao đổi..." />
            </label>
          </template>

          <!-- Test đầu vào -->
          <template v-else>
            <label class="fg">
              <span>Ngày test</span>
              <input v-model="f.test_date" class="field" type="date" />
            </label>
            <label class="fg">
              <span>Điểm *</span>
              <input v-model="f.score" class="field" type="number" step="0.1" placeholder="VD: 7.5" required />
            </label>
            <label class="fg">
              <span>Trình độ đánh giá</span>
              <select v-model="f.level" class="field">
                <option v-for="lv in LEVEL_OPTIONS" :key="lv" :value="lv">{{ lv || '— Chọn trình độ —' }}</option>
              </select>
            </label>
            <label class="fg">
              <span>Khóa học đề xuất</span>
              <select v-model="f.recommended_course" class="field">
                <option value="">—</option>
                <option v-for="c in courses" :key="c.name" :value="c.name">{{ c.course_name }}</option>
              </select>
            </label>
            <label class="fg fg--full">
              <span>Nhận xét đánh giá</span>
              <textarea v-model="f.test_notes" class="field field--area" placeholder="Nhận xét chi tiết về bài test..." />
            </label>
          </template>
        </div>
      </div>

      <!-- ===== Bước tiếp theo (định tuyến) ===== -->
      <div class="sec">
        <div class="sec__title">Bước tiếp theo</div>
        <div class="decisions">
          <button
            v-for="d in decisions"
            :key="d.value"
            type="button"
            class="decision"
            :class="{ 'decision--on': f.next_action === d.value }"
            @click="f.next_action = d.value"
          >{{ d.label }}</button>
        </div>

        <!-- Field lộ theo quyết định -->
        <div v-if="needsClass" class="form-grid reveal">
          <label class="fg fg--full">
            <span>Lớp {{ f.next_action === 'Trial' ? 'học thử' : 'nhập học' }} *</span>
            <select v-model="f.class_id" class="field" required>
              <option value="">— Chọn lớp —</option>
              <option v-for="c in classes" :key="c.name" :value="c.name">
                {{ c.class_name }}<template v-if="c.course"> · {{ c.course }}</template>
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Ngày ghi danh</span>
            <input v-model="f.enrollment_date" class="field" type="date" />
          </label>
          <p v-if="f.next_action === 'Enrolled'" class="hint fg--full">Sẽ tạo hồ sơ học viên + ghi danh chính thức (sinh học phí).</p>
          <p v-else class="hint fg--full">Sẽ tạo hồ sơ học viên + ghi danh học thử (chưa sinh học phí).</p>
        </div>

        <div v-else-if="needsTestAppt" class="form-grid reveal">
          <label class="fg">
            <span>Ngày hẹn test</span>
            <input v-model="f.appointment_date" class="field" type="date" />
          </label>
          <label class="fg">
            <span>Giờ hẹn</span>
            <input v-model="f.appointment_time" class="field" type="time" />
          </label>
        </div>

        <div v-else-if="needsFollowup" class="form-grid reveal">
          <label class="fg">
            <span>Ngày theo dõi tiếp</span>
            <input v-model="f.next_follow_up" class="field" type="date" />
          </label>
        </div>

        <div v-else-if="needsLost" class="form-grid reveal">
          <label class="fg fg--full">
            <span>Lý do *</span>
            <textarea v-model.trim="f.lost_reason" class="field field--area" required placeholder="Vì sao lead không tiếp tục?" />
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <SkButton variant="secondary" :disabled="saving" @click="emit('update:modelValue', false)">Hủy</SkButton>
      <SkButton variant="solid" :loading="saving" @click="submit">Lưu &amp; chuyển bước</SkButton>
    </template>
  </SkModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { call, crm } from '../../api'
import { toast } from '../../utils/toast'
import { todayStr } from './stages'
import SkModal from '../ui/SkModal.vue'
import SkButton from '../ui/SkButton.vue'
import SkAvatar from '../ui/SkAvatar.vue'

const props = defineProps({
  modelValue: Boolean,
  lead: { type: Object, default: null },
  presetAction: { type: String, default: '' }, // từ kéo-thả (cột đích)
  appointment: { type: String, default: '' },  // tên Student Appointment cần đánh dấu Completed
})
const emit = defineEmits(['update:modelValue', 'done'])

const STEP_LABEL = { Consulting: 'Tư vấn', Testing: 'Test đầu vào', Trial: 'Học thử' }
const RESULT_OPTIONS = ['', 'Tiềm năng cao', 'Tiềm năng trung bình', 'Cần theo dõi thêm', 'Tiềm năng thấp', 'Không quan tâm']
const LEVEL_OPTIONS = ['', 'Mất gốc', 'N5', 'N4', 'N3', 'N2', 'N1']

const DECISIONS = {
  Consulting: [
    { value: 'Testing', label: 'Cần test đầu vào' },
    { value: 'Trial', label: 'Đồng ý học thử' },
    { value: 'Enrolled', label: 'Đồng ý nhập học luôn' },
    { value: 'Consulting', label: 'Cần theo dõi thêm' },
    { value: 'Lost', label: 'Không quan tâm' },
  ],
  Testing: [
    { value: 'Trial', label: 'Đồng ý học thử' },
    { value: 'Enrolled', label: 'Đồng ý nhập học luôn' },
    { value: 'Consulting', label: 'Cần tư vấn thêm' },
    { value: 'Lost', label: 'Không đạt / không quan tâm' },
  ],
  Trial: [
    { value: 'Enrolled', label: 'Đồng ý nhập học' },
    { value: 'Stay', label: 'Cần thêm thời gian học thử' },
    { value: 'Lost', label: 'Không tiếp tục' },
  ],
}

const saving = ref(false)
const courses = ref([])
const classes = ref([])
const f = ref({})

const currentStep = computed(() => {
  const s = props.lead?.status
  if (s === 'Testing') return 'Testing'
  if (s === 'Trial') return 'Trial'
  return 'Consulting'
})
const decisions = computed(() => DECISIONS[currentStep.value] || DECISIONS.Consulting)
const needsClass = computed(() => ['Trial', 'Enrolled'].includes(f.value.next_action))
const needsTestAppt = computed(() => f.value.next_action === 'Testing')
const needsFollowup = computed(() => f.value.next_action === 'Consulting')
const needsLost = computed(() => f.value.next_action === 'Lost')

function blankForm() {
  const preset = decisions.value.some((d) => d.value === props.presetAction) ? props.presetAction : ''
  return {
    next_action: preset,
    contact_date: todayStr(), result: '', notes: '', next_follow_up: '',
    test_date: todayStr(), score: '', level: '', recommended_course: '', test_notes: '',
    class_id: '', enrollment_date: todayStr(),
    appointment_date: todayStr(), appointment_time: '',
    lost_reason: '',
  }
}

watch(
  () => props.modelValue,
  async (open) => {
    if (!open) return
    f.value = blankForm()
    if (currentStep.value === 'Testing' && !courses.value.length) {
      try { courses.value = (await call('get_courses')) || [] } catch { /* bỏ qua */ }
    }
  },
)

// Nạp danh sách lớp khi quyết định cần chọn lớp
watch(needsClass, async (need) => {
  if (need && !classes.value.length) {
    try { classes.value = (await call('get_classes')) || [] } catch { /* bỏ qua */ }
  }
})

function buildPayload() {
  const v = f.value
  const p = { current_step: currentStep.value, next_action: v.next_action }
  if (props.appointment) p.appointment = props.appointment

  if (currentStep.value === 'Testing') {
    p.test_date = v.test_date || undefined
    p.score = v.score === '' ? undefined : v.score
    p.level = v.level || undefined
    p.recommended_course = v.recommended_course || undefined
    p.test_notes = v.test_notes || undefined
  } else {
    p.contact_date = v.contact_date || undefined
    p.notes = v.notes || undefined
    p.result = v.result || undefined
  }

  if (needsClass.value) {
    p.class_id = v.class_id
    p.enrollment_date = v.enrollment_date || undefined
  } else if (needsTestAppt.value) {
    p.appointment_date = v.appointment_date || undefined
    p.appointment_time = v.appointment_time || undefined
  } else if (needsFollowup.value) {
    p.next_follow_up = v.next_follow_up || undefined
  } else if (needsLost.value) {
    p.lost_reason = v.lost_reason
  }
  return p
}

function validate() {
  if (!f.value.next_action) { toast.error('Chọn bước tiếp theo'); return false }
  if (currentStep.value === 'Testing' && f.value.score === '') { toast.error('Cần nhập điểm test'); return false }
  if (needsClass.value && !f.value.class_id) { toast.error('Cần chọn lớp'); return false }
  if (needsLost.value && !f.value.lost_reason) { toast.error('Cần nhập lý do'); return false }
  return true
}

async function submit() {
  if (!props.lead || !validate()) return
  saving.value = true
  try {
    const res = await crm.recordOutcome(props.lead.name, buildPayload())
    toast.success('Đã ghi nhận & chuyển bước')
    emit('update:modelValue', false)
    emit('done', res)
  } catch (e) {
    toast.error('Không lưu được', e?.messages?.[0] || e?.message || String(e))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.stage-lead { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid #f4dde5; }
.stage-lead__meta { display: flex; flex-direction: column; min-width: 0; }
.stage-lead__name { font-size: 14px; font-weight: 600; color: #3d2530; }
.stage-lead__sub { font-size: 12px; color: #a98c98; }

.form { margin: 0; display: flex; flex-direction: column; gap: 18px; }
.sec__title { font-size: 11.5px; font-weight: 700; color: #b8456a; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 10px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.reveal { margin-top: 12px; padding: 12px; background: #fdf2f6; border: 1px dashed #ecd0da; border-radius: 9px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg--full { grid-column: 1 / -1; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; min-height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }
.field--area { min-height: 70px; resize: vertical; padding: 8px 11px; }
.hint { grid-column: 1 / -1; margin: 0; font-size: 12px; color: #9b7a86; }

.decisions { display: flex; flex-wrap: wrap; gap: 8px; }
.decision { border: 1px solid #ecd0da; background: #fff; color: #7a5c68; font-size: 12.5px; font-weight: 600; padding: 8px 13px; border-radius: 9px; cursor: pointer; font-family: inherit; transition: all 0.12s ease; }
.decision:hover { border-color: #ecbcce; background: #fdf2f6; }
.decision--on { border-color: #d4567f; background: #d4567f; color: #fff; box-shadow: 0 3px 9px rgba(212, 86, 127, 0.28); }
</style>
