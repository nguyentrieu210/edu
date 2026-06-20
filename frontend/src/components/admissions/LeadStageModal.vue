<template>
  <SkModal
    :model-value="modelValue"
    :title="`Chuyển sang: ${stageLabel(toStatus)}`"
    width="540px"
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
      <!-- Consulting: lịch hẹn tư vấn + ghi chú -->
      <div v-if="toStatus === 'Consulting'" class="form-grid">
        <label class="fg">
          <span>Ngày hẹn tư vấn *</span>
          <input v-model="f.appointment_date" class="field" type="date" required />
        </label>
        <label class="fg">
          <span>Giờ hẹn</span>
          <input v-model="f.appointment_time" class="field" type="time" />
        </label>
        <label class="fg fg--full">
          <span>Mục đích</span>
          <input v-model.trim="f.purpose" class="field" placeholder="Tư vấn lộ trình..." />
        </label>
        <label class="fg fg--full">
          <span>Ghi chú tư vấn</span>
          <textarea v-model="f.notes" class="field field--area" placeholder="Nội dung trao đổi, nhu cầu của học viên..." />
        </label>
        <label class="fg">
          <span>Lần liên hệ kế tiếp</span>
          <input v-model="f.next_follow_up" class="field" type="date" />
        </label>
      </div>

      <!-- Testing: lịch hẹn test + kết quả test đầu vào -->
      <div v-else-if="toStatus === 'Testing'" class="form-grid">
        <p class="hint fg--full">Lên lịch test và/hoặc ghi kết quả test đầu vào.</p>
        <label class="fg">
          <span>Ngày hẹn test</span>
          <input v-model="f.appointment_date" class="field" type="date" />
        </label>
        <label class="fg">
          <span>Giờ hẹn</span>
          <input v-model="f.appointment_time" class="field" type="time" />
        </label>
        <div class="divider fg--full"><span>Kết quả test (nếu đã có)</span></div>
        <label class="fg">
          <span>Ngày test</span>
          <input v-model="f.test_date" class="field" type="date" />
        </label>
        <label class="fg">
          <span>Điểm</span>
          <input v-model="f.score" class="field" type="number" step="0.1" placeholder="VD: 7.5" />
        </label>
        <label class="fg fg--full">
          <span>Khóa học gợi ý</span>
          <select v-model="f.recommended_course" class="field">
            <option value="">—</option>
            <option v-for="c in courses" :key="c.name" :value="c.name">{{ c.course_name }}</option>
          </select>
        </label>
      </div>

      <!-- Trial: chọn lớp ghi danh học thử -->
      <div v-else-if="toStatus === 'Trial'" class="form-grid">
        <p class="hint fg--full">⚠️ Bước này sẽ tạo <b>hồ sơ học viên</b> và ghi danh học thử (Trial) vào lớp đã chọn.</p>
        <label class="fg fg--full">
          <span>Lớp học thử *</span>
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
        <label class="fg">
          <span>Ngày buổi học thử</span>
          <input v-model="f.appointment_date" class="field" type="date" />
        </label>
        <label class="fg fg--full">
          <span>Ghi chú</span>
          <textarea v-model="f.notes" class="field field--area" placeholder="Ghi chú buổi học thử..." />
        </label>
      </div>

      <!-- Enrolled: xác nhận chuyển đổi -->
      <div v-else-if="toStatus === 'Enrolled'" class="form-grid">
        <p class="hint fg--full">
          Xác nhận nhập học chính thức. Hệ thống sẽ tạo (hoặc tái dùng) hồ sơ <b>học viên</b>
          và người giám hộ từ thông tin lead.
        </p>
      </div>

      <!-- Lost: lý do thất bại -->
      <div v-else-if="toStatus === 'Lost'" class="form-grid">
        <label class="fg fg--full">
          <span>Lý do thất bại *</span>
          <textarea v-model.trim="f.lost_reason" class="field field--area" required placeholder="Vì sao lead không tiếp tục?" />
        </label>
      </div>
    </form>

    <template #footer>
      <SkButton variant="secondary" :disabled="saving" @click="emit('update:modelValue', false)">Hủy</SkButton>
      <SkButton variant="solid" :loading="saving" @click="submit">Xác nhận</SkButton>
    </template>
  </SkModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { call, crm } from '../../api'
import { toast } from '../../utils/toast'
import { stageLabel, todayStr } from './stages'
import SkModal from '../ui/SkModal.vue'
import SkButton from '../ui/SkButton.vue'
import SkAvatar from '../ui/SkAvatar.vue'

const props = defineProps({
  modelValue: Boolean,
  lead: { type: Object, default: null },
  toStatus: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'done'])

const saving = ref(false)
const courses = ref([])
const classes = ref([])
const f = ref({})

function blankForm() {
  return {
    appointment_date: todayStr(),
    appointment_time: '',
    purpose: '',
    notes: '',
    next_follow_up: '',
    test_date: todayStr(),
    score: '',
    recommended_course: '',
    class_id: '',
    enrollment_date: todayStr(),
    lost_reason: '',
  }
}

watch(
  () => props.modelValue,
  async (open) => {
    if (!open) return
    f.value = blankForm()
    if (props.toStatus === 'Testing' && !courses.value.length) {
      try { courses.value = (await call('get_courses')) || [] } catch { /* bỏ qua */ }
    }
    if (props.toStatus === 'Trial' && !classes.value.length) {
      try { classes.value = (await call('get_classes')) || [] } catch { /* bỏ qua */ }
    }
  },
)

function buildPayload() {
  const v = f.value
  if (props.toStatus === 'Consulting') {
    return {
      appointment_date: v.appointment_date,
      appointment_time: v.appointment_time || undefined,
      purpose: v.purpose || undefined,
      notes: v.notes || undefined,
      next_follow_up: v.next_follow_up || undefined,
    }
  }
  if (props.toStatus === 'Testing') {
    return {
      appointment_date: v.appointment_date || undefined,
      appointment_time: v.appointment_time || undefined,
      test_date: v.test_date || undefined,
      score: v.score === '' ? undefined : v.score,
      recommended_course: v.recommended_course || undefined,
    }
  }
  if (props.toStatus === 'Trial') {
    return {
      class_id: v.class_id,
      enrollment_date: v.enrollment_date || undefined,
      appointment_date: v.appointment_date || undefined,
      notes: v.notes || undefined,
    }
  }
  if (props.toStatus === 'Lost') {
    return { lost_reason: v.lost_reason }
  }
  return {}
}

function validate() {
  if (props.toStatus === 'Consulting' && !f.value.appointment_date) {
    toast.error('Cần ngày hẹn tư vấn'); return false
  }
  if (props.toStatus === 'Trial' && !f.value.class_id) {
    toast.error('Cần chọn lớp học thử'); return false
  }
  if (props.toStatus === 'Lost' && !f.value.lost_reason) {
    toast.error('Cần nhập lý do thất bại'); return false
  }
  return true
}

async function submit() {
  if (!props.lead || !validate()) return
  saving.value = true
  try {
    const res = await crm.advanceStage(props.lead.name, props.toStatus, buildPayload())
    toast.success(`Đã chuyển "${props.lead.lead_name}" sang ${stageLabel(props.toStatus)}`)
    emit('update:modelValue', false)
    emit('done', res)
  } catch (e) {
    toast.error('Không chuyển được trạng thái', e?.messages?.[0] || e?.message || String(e))
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

.form { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg--full { grid-column: 1 / -1; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; min-height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }
.field--area { min-height: 72px; resize: vertical; padding: 8px 11px; }
.hint { grid-column: 1 / -1; margin: 0; font-size: 12.5px; color: #9b7a86; background: #fdf2f6; border: 1px dashed #ecd0da; border-radius: 9px; padding: 10px 12px; }
.divider { display: flex; align-items: center; margin: 2px 0; }
.divider span { font-size: 11px; font-weight: 700; color: #b8456a; text-transform: uppercase; letter-spacing: 0.04em; }
</style>
