<template>
  <SkDrawer
    :model-value="modelValue"
    title="Chi tiết lead"
    width="480px"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <div v-if="lead" class="ld">
      <!-- Header -->
      <div class="ld__head">
        <SkAvatar :name="lead.lead_name" :src="lead.lead_image" :size="52" />
        <div class="ld__id">
          <div class="ld__name">{{ lead.lead_name }}</div>
          <SkBadge v-bind="statusMeta('Student Lead', 'status', curStatus)" />
        </div>
      </div>

      <!-- Liên hệ (sửa nhanh) -->
      <div class="ld__contact">
        <label class="qe">
          <span>SĐT</span>
          <input v-model.trim="edit.phone" class="qe__field" placeholder="—" @blur="saveField('phone')" @keydown.enter.prevent="saveField('phone')" />
        </label>
        <label class="qe">
          <span>Email</span>
          <input v-model.trim="edit.email" class="qe__field" type="email" placeholder="—" @blur="saveField('email')" @keydown.enter.prevent="saveField('email')" />
        </label>
        <div class="qe qe--ro">
          <span>Nguồn</span>
          <div class="qe__ro">{{ lead.source || '—' }}</div>
        </div>
        <div class="qe qe--ro">
          <span>Nghề nghiệp</span>
          <div class="qe__ro">{{ lead.occupation || '—' }}</div>
        </div>
      </div>

      <!-- Hành động chuyển stage -->
      <section class="ld__sec">
        <h4 class="ld__h">Hành động kế tiếp</h4>
        <div class="ld__actions">
          <SkButton
            v-for="s in stageActions"
            :key="s"
            :variant="s === suggested ? 'solid' : 'secondary'"
            size="sm"
            @click="openStage(s)"
          >
            <template v-if="s === suggested">→ </template>{{ stageLabel(s) }}
          </SkButton>
          <SkButton v-if="curStatus !== 'Lost'" variant="ghost" size="sm" @click="openStage('Lost')">Thất bại</SkButton>
        </div>
      </section>

      <!-- Trợ lý AI -->
      <section class="ld__sec">
        <h4 class="ld__h">Trợ lý AI ✨</h4>
        <div class="ld__ai-btns">
          <button v-for="a in AI_ACTIONS" :key="a.kind" class="ai-chip" :disabled="aiBusy" @click="runAi(a.kind)">
            <FeatherIcon :name="a.icon" style="width:13px;height:13px;" /> {{ a.label }}
          </button>
        </div>
        <div v-if="aiBusy || aiOut" class="ld__ai-out">
          <div v-if="aiBusy" class="ld__ai-loading">AI đang soạn…</div>
          <p v-else class="ld__ai-text">{{ aiOut }}</p>
        </div>
      </section>

      <!-- Dòng thời gian nghiệp vụ -->
      <section class="ld__sec">
        <h4 class="ld__h">Lịch sử ({{ timeline.length }})</h4>
        <div v-if="loadingTl" class="ld__tl-loading">Đang tải…</div>
        <LeadTimeline v-else :items="timeline" />
      </section>
    </div>

    <LeadStageModal v-model="stageOpen" :lead="lead" :to-status="stageTarget" @done="onStageDone" />
  </SkDrawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call, crm, db } from '../../api'
import { toast } from '../../utils/toast'
import { statusMeta } from '../../utils/labels'
import { STAGE_ORDER, stageLabel, nextStage } from './stages'
import SkDrawer from '../ui/SkDrawer.vue'
import SkAvatar from '../ui/SkAvatar.vue'
import SkBadge from '../ui/SkBadge.vue'
import SkButton from '../ui/SkButton.vue'
import LeadTimeline from './LeadTimeline.vue'
import LeadStageModal from './LeadStageModal.vue'

const props = defineProps({
  modelValue: Boolean,
  lead: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'changed'])

const timeline = ref([])
const loadingTl = ref(false)
const curStatus = ref('New')
const edit = ref({ phone: '', email: '' })

const stageOpen = ref(false)
const stageTarget = ref('')

const aiBusy = ref(false)
const aiOut = ref('')

const AI_ACTIONS = [
  { kind: 'next', label: 'Hành động kế tiếp', icon: 'compass' },
  { kind: 'script', label: 'Kịch bản tư vấn', icon: 'message-square' },
  { kind: 'summary', label: 'Tóm tắt & chấm điểm', icon: 'award' },
  { kind: 'course', label: 'Gợi ý khóa học', icon: 'book-open' },
]

const suggested = computed(() => nextStage(curStatus.value))
// Các stage có thể chuyển tới (bỏ 'New' và chính trạng thái hiện tại).
const stageActions = computed(() =>
  STAGE_ORDER.filter((s) => s !== 'New' && s !== curStatus.value),
)

watch(
  () => [props.modelValue, props.lead?.name],
  async ([open]) => {
    if (!open || !props.lead) return
    curStatus.value = props.lead.status
    edit.value = { phone: props.lead.phone || '', email: props.lead.email || '' }
    aiOut.value = ''
    await loadTimeline()
  },
  { immediate: true },
)

async function loadTimeline() {
  loadingTl.value = true
  try {
    timeline.value = (await crm.timeline(props.lead.name)) || []
  } catch (e) {
    timeline.value = []
    toast.error('Không tải được lịch sử', e?.message || String(e))
  } finally {
    loadingTl.value = false
  }
}

async function saveField(field) {
  const val = edit.value[field]
  if (val === (props.lead[field] || '')) return
  try {
    await db.setValue('Student Lead', props.lead.name, field, val)
    props.lead[field] = val
    toast.success('Đã lưu')
    emit('changed')
  } catch (e) {
    edit.value[field] = props.lead[field] || ''
    toast.error('Không lưu được', e?.messages?.[0] || e?.message || String(e))
  }
}

function openStage(status) {
  stageTarget.value = status
  stageOpen.value = true
}

async function onStageDone(res) {
  curStatus.value = res?.status || curStatus.value
  if (props.lead && res?.status) props.lead.status = res.status
  emit('changed')
  await loadTimeline()
}

function leadContext() {
  const l = props.lead
  const lines = [
    `Tên: ${l.lead_name}`,
    `Trạng thái: ${stageLabel(curStatus.value)}`,
    l.occupation && `Nghề nghiệp: ${l.occupation}`,
    l.source && `Nguồn: ${l.source}`,
    l.date_of_birth && `Ngày sinh: ${l.date_of_birth}`,
  ].filter(Boolean)
  if (timeline.value.length) {
    lines.push('Lịch sử:')
    for (const it of timeline.value.slice(0, 8)) {
      lines.push(`- [${it.date || ''}] ${it.title}${it.detail ? ': ' + it.detail : ''}`)
    }
  }
  return lines.join('\n')
}

const PROMPTS = {
  next: 'Đề xuất 2-3 hành động kế tiếp cụ thể, ngắn gọn mà chuyên viên tuyển sinh nên làm với lead này.',
  script: 'Soạn một kịch bản gọi điện/tin nhắn tư vấn ngắn gọn, thân thiện, phù hợp để liên hệ lead này.',
  summary: 'Tóm tắt ngắn gọn hồ sơ lead và chấm điểm mức độ tiềm năng (Cao/Trung bình/Thấp) kèm lý do.',
  course: 'Dựa trên điểm test đầu vào (nếu có trong lịch sử), gợi ý khóa học tiếng Nhật phù hợp và lý do. Nếu chưa có điểm test, hãy nói rõ cần test đầu vào trước.',
}

async function runAi(kind) {
  aiBusy.value = true
  aiOut.value = ''
  try {
    const messages = [
      {
        role: 'system',
        content:
          'Bạn là chuyên viên tư vấn tuyển sinh của IKE Ohashi (trung tâm tiếng Nhật). ' +
          'Trả lời ngắn gọn, thực tế bằng tiếng Việt, không lan man.',
      },
      { role: 'user', content: `${PROMPTS[kind]}\n\nThông tin lead:\n${leadContext()}` },
    ]
    aiOut.value = await call('ai_chat', { messages, temperature: 0.5, max_tokens: 700 })
  } catch (e) {
    toast.error('AI thất bại', e?.message || String(e))
  } finally {
    aiBusy.value = false
  }
}
</script>

<style scoped>
.ld { display: flex; flex-direction: column; gap: 20px; }
.ld__head { display: flex; align-items: center; gap: 14px; }
.ld__id { display: flex; flex-direction: column; gap: 7px; min-width: 0; }
.ld__name { font-size: 17px; font-weight: 700; color: #3d2530; }

.ld__contact { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qe { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.qe > span { font-size: 10.5px; font-weight: 600; color: #a07c8a; text-transform: uppercase; letter-spacing: 0.03em; }
.qe__field { width: 100%; height: 32px; border: 1px solid #f0d7e0; border-radius: 8px; background: #fff; padding: 0 9px; font-size: 13px; color: #3d2530; outline: none; font-family: inherit; }
.qe__field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.1); }
.qe__ro { height: 32px; display: flex; align-items: center; font-size: 13px; color: #7a5c68; }

.ld__sec { display: flex; flex-direction: column; gap: 10px; }
.ld__h { margin: 0; font-size: 12px; font-weight: 700; color: #b8456a; text-transform: uppercase; letter-spacing: 0.04em; }
.ld__actions { display: flex; flex-wrap: wrap; gap: 7px; }

.ld__ai-btns { display: flex; flex-wrap: wrap; gap: 7px; }
.ai-chip { display: inline-flex; align-items: center; gap: 5px; border: 1px solid #ecd0da; background: #fff; color: #b8456a; font-size: 12px; font-weight: 600; padding: 6px 10px; border-radius: 8px; cursor: pointer; font-family: inherit; }
.ai-chip:hover:not(:disabled) { background: #fbeef3; border-color: #ecbcce; }
.ai-chip:disabled { opacity: 0.5; cursor: default; }
.ld__ai-out { background: #fdf2f6; border: 1px solid #f3d9e1; border-radius: 10px; padding: 12px 13px; }
.ld__ai-loading { font-size: 12.5px; color: #b8456a; }
.ld__ai-text { margin: 0; font-size: 13px; color: #4a2230; white-space: pre-wrap; word-break: break-word; line-height: 1.55; }

.ld__tl-loading { font-size: 12.5px; color: #bd97a5; }
</style>
