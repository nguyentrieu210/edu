<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Tuyển sinh · CRM Pipeline</span>
      <div class="ws-head__actions">
        <SkSegmented v-model="view" :options="[{label:'Kanban',value:'kanban'},{label:'Danh sách',value:'list'}]" />
        <SkButton variant="solid" leftIcon="plus" @click="openLead">Thêm lead</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="error" title="Không tải được dữ liệu" :message="error" action-label="Thử lại" @action="load" />
      <SkState v-else-if="!leads.length" state="empty" title="Chưa có lead" message="Thêm lead đầu tiên để bắt đầu tuyển sinh." action-label="Thêm lead" @action="openLead" />

      <!-- Kanban -->
      <div v-else-if="view === 'kanban'" class="kanban">
        <div
          v-for="col in columns"
          :key="col.status"
          class="kan-col"
          :class="{ 'kan-col--over': dragOver === col.status }"
          @dragover.prevent="dragOver = col.status"
          @dragleave="onColLeave(col.status)"
          @drop="onDrop(col.status)"
        >
          <div class="kan-col__head">
            <span class="dot" :style="{ background: col.dot }" />
            <span class="kan-col__title">{{ col.label }}</span>
            <span class="kan-col__count">{{ col.cards.length }}</span>
          </div>
          <div class="kan-col__body">
            <div
              v-for="c in col.cards"
              :key="c.name"
              class="kan-card"
              :class="{ 'kan-card--drag': dragCard && dragCard.name === c.name }"
              draggable="true"
              @dragstart="onDragStart(c)"
              @dragend="onDragEnd"
              @click="openDetail(c)"
            >
              <div class="kan-card__top">
                <SkAvatar :name="c.lead_name" :src="c.lead_image" :size="30" />
                <span class="kan-card__name">{{ c.lead_name }}</span>
              </div>
              <div class="kan-card__interest">{{ c.occupation || c.email || c.phone || '—' }}</div>
              <div class="kan-card__foot">
                <span class="kan-card__source">{{ c.source || '—' }}</span>
                <span class="kan-card__date tnum">{{ formatDate(c.creation) }}</span>
              </div>
            </div>
            <div v-if="!col.cards.length" class="kan-col__empty">—</div>
          </div>
        </div>
      </div>

      <!-- List -->
      <div v-else class="card">
        <table class="tbl">
          <thead>
            <tr>
              <th>Họ tên</th><th>Điện thoại</th><th>Email</th><th>Nguồn</th><th>Trạng thái</th><th>Ngày tạo</th><th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in leads" :key="l.name">
              <td class="tbl__name" @click="openDetail(l)">
                <div class="tbl__id">
                  <SkAvatar :name="l.lead_name" :src="l.lead_image" :size="26" />
                  <span>{{ l.lead_name }}</span>
                </div>
              </td>

              <td class="tbl__edit" @click="startEdit(l, 'phone')">
                <input v-if="isEditing(l, 'phone')" ref="cellInput" v-model.trim="cellValue" class="cell-input tnum"
                  @blur="commitEdit(l, 'phone')" @keydown.enter.prevent="commitEdit(l, 'phone')" @keydown.esc="cancelEdit" />
                <span v-else class="tbl__sub tnum">{{ l.phone || '—' }}</span>
              </td>

              <td class="tbl__edit" @click="startEdit(l, 'email')">
                <input v-if="isEditing(l, 'email')" ref="cellInput" v-model.trim="cellValue" type="email" class="cell-input"
                  @blur="commitEdit(l, 'email')" @keydown.enter.prevent="commitEdit(l, 'email')" @keydown.esc="cancelEdit" />
                <span v-else class="tbl__sub">{{ l.email || '—' }}</span>
              </td>

              <td class="tbl__edit" @click="startEdit(l, 'source')">
                <select v-if="isEditing(l, 'source')" ref="cellInput" v-model="cellValue" class="cell-input"
                  @change="commitEdit(l, 'source')" @blur="commitEdit(l, 'source')">
                  <option v-for="s in SOURCES" :key="s" :value="s">{{ s }}</option>
                </select>
                <span v-else class="tbl__sub">{{ l.source || '—' }}</span>
              </td>

              <td>
                <select class="status-select" :value="l.status" @change="onListStatus(l, $event)">
                  <option v-for="s in ALL_STATUSES" :key="s" :value="s">{{ stageLabel(s) }}</option>
                </select>
              </td>

              <td class="tbl__sub tnum">{{ formatDate(l.creation) }}</td>
              <td class="tbl__act">
                <SkButton variant="ghost" size="sm" leftIcon="chevron-right" @click="openDetail(l)">Mở</SkButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add lead -->
    <SkModal v-model="leadOpen" title="Thêm lead tuyển sinh" width="580px">
      <form class="form" @submit.prevent="saveLead">
        <!-- Avatar -->
        <div class="avatar-row fg--full">
          <SkAvatar :name="leadForm.lead_name || 'Lead'" :src="leadForm.lead_image" :size="56" />
          <div class="avatar-row__btns">
            <SkButton type="button" variant="secondary" size="sm" :loading="avatarUploading" leftIcon="image" @click="avatarInput?.click()">
              {{ leadForm.lead_image ? 'Đổi ảnh' : 'Tải avatar' }}
            </SkButton>
            <input ref="avatarInput" type="file" accept="image/*" hidden @change="onAvatarPick" />
          </div>
        </div>

        <div class="form-grid">
          <!-- AI từ văn bản -->
          <div class="ai-parse-section fg--full">
            <div class="ai-parse-header">
              <span>Nhập nhanh bằng AI ✨</span>
              <button type="button" class="ai-toggle-btn" @click="showAiInput = !showAiInput">
                {{ showAiInput ? 'Thu gọn' : 'Nhập tin nhắn thô' }}
              </button>
            </div>
            <div v-if="showAiInput" class="ai-parse-body">
              <textarea
                v-model="aiRawText"
                class="field field--area"
                placeholder="Dán tin nhắn, ghi chú thô của học viên... Ví dụ: Nguyễn Văn An, sđt 0912345678, sinh ngày 12/03/1999, liên hệ qua Facebook..."
              />
              <SkButton type="button" variant="solid" :loading="parsing" :disabled="!aiRawText.trim()"
                @click="parseWithAi" style="margin-top: 8px; align-self: flex-start;">
                AI Phân tích &amp; Điền form
              </SkButton>
            </div>
          </div>

          <!-- AI từ tài liệu (ảnh/PDF) -->
          <div class="ai-parse-section fg--full">
            <div class="ai-parse-header">
              <span>Tải tài liệu &amp; AI đọc 📄</span>
              <button type="button" class="ai-toggle-btn" :disabled="docBusy" @click="docInput?.click()">
                {{ docBusy ? 'Đang xử lý…' : 'Tải ảnh/PDF' }}
              </button>
              <input ref="docInput" type="file" accept="image/*,application/pdf" hidden @change="onDocPick" />
            </div>
            <div v-if="docFiles.length" class="doc-chips">
              <span v-for="(d, i) in docFiles" :key="i" class="doc-chip">
                <FeatherIcon name="paperclip" style="width:11px;height:11px;" /> {{ d.file_name }}
              </span>
            </div>
          </div>

          <label class="fg fg--full">
            <span>Họ tên</span>
            <input v-model.trim="leadForm.lead_name" class="field" required placeholder="Nguyễn Văn An" />
          </label>
          <label class="fg">
            <span>Điện thoại</span>
            <input v-model.trim="leadForm.phone" class="field" placeholder="09..." />
          </label>
          <label class="fg">
            <span>Email</span>
            <input v-model.trim="leadForm.email" class="field" type="email" placeholder="email@example.com" />
          </label>
          <label class="fg">
            <span>Nguồn</span>
            <select v-model="leadForm.source" class="field">
              <option v-for="s in SOURCES" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
          <label class="fg">
            <span>Giới tính</span>
            <select v-model="leadForm.gender" class="field">
              <option value=""></option>
              <option value="Nam">Nam</option>
              <option value="Nữ">Nữ</option>
              <option value="Khác">Khác</option>
            </select>
          </label>
          <label class="fg">
            <span>Ngày sinh</span>
            <input v-model="leadForm.date_of_birth" class="field" type="date" />
          </label>
          <label class="fg">
            <span>Nghề nghiệp</span>
            <input v-model.trim="leadForm.occupation" class="field" placeholder="Sinh viên, nhân viên..." />
          </label>
          <label class="fg">
            <span>Người giám hộ</span>
            <input v-model.trim="leadForm.guardian_name" class="field" />
          </label>
          <label class="fg">
            <span>SĐT người giám hộ</span>
            <input v-model.trim="leadForm.guardian_phone" class="field" />
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingLead" @click="leadOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingLead" @click="saveLead">Lưu lead</SkButton>
      </template>
    </SkModal>

    <!-- Stage transition (kanban/list) -->
    <LeadStageModal v-model="stageOpen" :lead="stageLead" :to-status="stageTarget" @done="onStageDone" />

    <!-- Detail drawer -->
    <LeadDetailDrawer v-model="detailOpen" :lead="selectedLead" @changed="onDrawerChanged" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call, db, crm, uploadFile } from '../api'
import { formatDate } from '../utils/format'
import { toast } from '../utils/toast'
import { STAGES, stageLabel } from '../components/admissions/stages'
import SkButton from '../components/ui/SkButton.vue'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkModal from '../components/ui/SkModal.vue'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkState from '../components/ui/SkState.vue'
import LeadStageModal from '../components/admissions/LeadStageModal.vue'
import LeadDetailDrawer from '../components/admissions/LeadDetailDrawer.vue'

const loading = ref(true)
const error = ref('')
const leads = ref([])
const view = ref('kanban')

const SOURCES = ['Website', 'Facebook', 'Hotline', 'Word of Mouth', 'Other']
const COLS = [...STAGES, { status: 'Lost', dot: '#c98a9a' }]
const ALL_STATUSES = COLS.map((c) => c.status)

const columns = computed(() =>
  COLS.map((c) => ({
    ...c,
    label: stageLabel(c.status),
    cards: leads.value.filter((l) => l.status === c.status),
  })),
)

/* ---------- Detail drawer ---------- */
const detailOpen = ref(false)
const selectedLead = ref(null)
function openDetail(lead) {
  if (dragCard.value) return
  selectedLead.value = lead
  detailOpen.value = true
}
async function onDrawerChanged() {
  const keep = selectedLead.value?.name
  await load()
  if (keep) selectedLead.value = leads.value.find((l) => l.name === keep) || selectedLead.value
}

/* ---------- Stage transitions ---------- */
const stageOpen = ref(false)
const stageLead = ref(null)
const stageTarget = ref('')
function openStageFor(lead, status) {
  stageLead.value = lead
  stageTarget.value = status
  stageOpen.value = true
}
async function onStageDone() {
  await load()
}

/* ---------- Drag & drop (kanban) ---------- */
const dragCard = ref(null)
const dragOver = ref('')
function onDragStart(card) {
  dragCard.value = card
}
function onDragEnd() {
  dragCard.value = null
  dragOver.value = ''
}
function onColLeave(status) {
  if (dragOver.value === status) dragOver.value = ''
}
async function onDrop(toStatus) {
  const card = dragCard.value
  dragOver.value = ''
  dragCard.value = null
  if (!card || card.status === toStatus) return
  if (toStatus === 'New') {
    await plainSetStatus(card, 'New')
  } else {
    openStageFor(card, toStatus)
  }
}

/* ---------- List inline editing ---------- */
const editing = ref({ name: '', field: '' })
const cellValue = ref('')
const cellInput = ref(null)
function isEditing(lead, field) {
  return editing.value.name === lead.name && editing.value.field === field
}
async function startEdit(lead, field) {
  if (isEditing(lead, field)) return
  editing.value = { name: lead.name, field }
  cellValue.value = lead[field] || ''
  await nextTick()
  const el = Array.isArray(cellInput.value) ? cellInput.value[0] : cellInput.value
  el?.focus?.()
}
function cancelEdit() {
  editing.value = { name: '', field: '' }
}
async function commitEdit(lead, field) {
  if (!isEditing(lead, field)) return
  const val = cellValue.value
  editing.value = { name: '', field: '' }
  if (val === (lead[field] || '')) return
  try {
    await db.setValue('Student Lead', lead.name, field, val)
    lead[field] = val
    toast.success('Đã lưu')
  } catch (e) {
    toast.error('Không lưu được', e?.messages?.[0] || e?.message || String(e))
  }
}

function onListStatus(lead, ev) {
  const to = ev.target.value
  ev.target.value = lead.status // giữ hiển thị cho tới khi backend xác nhận
  if (to === lead.status) return
  if (to === 'New') {
    plainSetStatus(lead, 'New')
  } else {
    openStageFor(lead, to)
  }
}

async function plainSetStatus(lead, status) {
  try {
    await db.setValue('Student Lead', lead.name, 'status', status)
    toast.success(`Đã chuyển sang ${stageLabel(status)}`)
    await load()
  } catch (e) {
    toast.error('Không đổi được trạng thái', e?.messages?.[0] || e?.message || String(e))
  }
}

/* ---------- Add lead ---------- */
const leadOpen = ref(false)
const savingLead = ref(false)
const leadForm = ref(defaultLeadForm())
const showAiInput = ref(false)
const aiRawText = ref('')
const parsing = ref(false)
const avatarInput = ref(null)
const avatarUploading = ref(false)
const docInput = ref(null)
const docBusy = ref(false)
const docFiles = ref([])

function defaultLeadForm() {
  return {
    lead_name: '', phone: '', email: '', source: 'Website', date_of_birth: '',
    gender: '', occupation: '', guardian_name: '', guardian_phone: '', lead_image: '',
  }
}

function openLead() {
  leadForm.value = defaultLeadForm()
  showAiInput.value = false
  aiRawText.value = ''
  docFiles.value = []
  leadOpen.value = true
}

async function onAvatarPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  avatarUploading.value = true
  try {
    const res = await uploadFile(file, { isPrivate: false })
    leadForm.value.lead_image = res.file_url
    toast.success('Đã tải avatar')
  } catch (err) {
    toast.error('Tải avatar thất bại', err?.message || String(err))
  } finally {
    avatarUploading.value = false
  }
}

function applyParsed(parsed) {
  for (const k of ['lead_name', 'phone', 'email', 'source', 'date_of_birth', 'gender', 'occupation', 'guardian_name', 'guardian_phone']) {
    if (parsed[k]) leadForm.value[k] = parsed[k]
  }
}

async function onDocPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  docBusy.value = true
  try {
    const res = await uploadFile(file, { isPrivate: true })
    docFiles.value.push({ file_url: res.file_url, file_name: res.file_name || file.name })
    toast.info('Đã tải tài liệu, đang để AI đọc…')
    const parsed = await crm.parseDocument(res.file_url)
    applyParsed(parsed)
    toast.success('AI đã đọc tài liệu & điền form!')
  } catch (err) {
    toast.error('Đọc tài liệu thất bại', err?.message || String(err))
  } finally {
    docBusy.value = false
  }
}

async function parseWithAi() {
  if (!aiRawText.value.trim()) return
  parsing.value = true
  try {
    const systemPrompt = `Bạn là trợ lý AI của IKE Ohashi. Hãy phân tích thông tin của học viên mới từ văn bản thô của người dùng và trích xuất thành một đối tượng JSON chính xác có cấu trúc sau:
{
  "lead_name": "Họ và tên",
  "phone": "Số điện thoại",
  "email": "Địa chỉ email",
  "source": "Chọn một trong các nguồn: Website, Facebook, Hotline, Word of Mouth, Other",
  "date_of_birth": "Ngày sinh định dạng YYYY-MM-DD",
  "gender": "Chọn một trong: Nam, Nữ, Khác",
  "occupation": "Nghề nghiệp",
  "guardian_name": "Tên người giám hộ",
  "guardian_phone": "Số điện thoại người giám hộ"
}

Nếu trường thông tin nào không tìm thấy trong văn bản, hãy đặt giá trị là chuỗi rỗng "". Chỉ trả về đúng định dạng JSON thô, không thêm dấu nháy ngược markdown (\`\`\`) hay bất kỳ văn bản giải thích nào khác.`

    const payload = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: aiRawText.value.trim() },
    ]
    const response = await call('ai_chat', { messages: payload, temperature: 0.2, max_tokens: 1024 })

    let parsedData = {}
    try {
      let cleaned = response.trim()
      if (cleaned.startsWith('```')) {
        cleaned = cleaned.replace(/^```json\s*/, '').replace(/^```\s*/, '').replace(/\s*```$/, '')
      }
      parsedData = JSON.parse(cleaned)
    } catch {
      throw new Error('AI trả về kết quả không đúng định dạng JSON.')
    }

    applyParsed(parsedData)
    toast.success('Đã điền form tự động bằng AI!')
    showAiInput.value = false
    aiRawText.value = ''
  } catch (e) {
    toast.error('AI phân tích thất bại', e?.message || String(e))
  } finally {
    parsing.value = false
  }
}

function cleanPayload(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== '' && value != null))
}

async function saveLead() {
  if (!leadForm.value.lead_name) {
    toast.error('Thiếu họ tên lead')
    return
  }
  savingLead.value = true
  try {
    const res = await db.insert({ doctype: 'Student Lead', ...cleanPayload(leadForm.value) })
    // Gắn các tài liệu đã tải vào lead vừa tạo.
    for (const d of docFiles.value) {
      try { await crm.attachFile(d.file_url, res.name) } catch { /* bỏ qua lỗi đính kèm lẻ */ }
    }
    toast.success('Đã thêm lead')
    leadOpen.value = false
    await load()
  } catch (e) {
    toast.error('Không thêm được lead', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingLead.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    leads.value = (await call('get_leads')) || []
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
.ws-head__actions { margin-left: auto; min-width: 0; display: flex; gap: 8px; align-items: center; }
.ws-body { flex: 1; min-height: 0; overflow: auto; padding: 20px 24px; }

.kanban { display: grid; grid-template-columns: repeat(6, minmax(170px, 1fr)); gap: 14px; align-items: stretch; min-width: 0; height: 100%; min-height: 0; }
.kan-col { min-width: 0; display: flex; flex-direction: column; min-height: 0; border-radius: 10px; transition: background 0.12s ease, box-shadow 0.12s ease; }
.kan-col--over { background: #fdf0f5; box-shadow: inset 0 0 0 2px #ecbcce; }
.kan-col__head { display: flex; align-items: center; gap: 8px; padding: 6px 6px 10px; }
.kan-col__title { min-width: 0; font-size: 13px; font-weight: 600; color: #4a2230; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.kan-col__count { font-size: 11px; color: #bd97a5; }
.kan-col__body { flex: 1; min-height: 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 0 4px 6px; }
.kan-col__empty { font-size: 12px; color: #cbb0bb; text-align: center; padding: 10px 0; }
.dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }

.kan-card { background: #fff; border: 1px solid #f3d9e1; border-radius: 10px; padding: 12px 13px; cursor: grab; box-shadow: 0 1px 2px rgba(180, 80, 120, 0.06); }
.kan-card:hover { border-color: #ecbcce; box-shadow: 0 3px 10px rgba(180, 80, 120, 0.12); }
.kan-card--drag { opacity: 0.45; }
.kan-card__top { display: flex; align-items: center; gap: 9px; }
.kan-card__name { min-width: 0; font-size: 13px; font-weight: 600; color: #3d2530; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.kan-card__interest { font-size: 11.5px; color: #a98c98; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.kan-card__foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 9px; }
.kan-card__source { font-size: 10.5px; color: #9b7a86; background: #fbeef3; border-radius: 5px; padding: 2px 7px; }
.kan-card__date { flex: none; font-size: 11px; color: #bd97a5; }

.card { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl thead tr { background: #fdf2f6; }
.tbl th { text-align: left; font-size: 11.5px; font-weight: 600; color: #a07c8a; padding: 10px 16px; }
.tbl td { padding: 9px 16px; border-top: 1px solid #f6e3ea; vertical-align: middle; }
.tbl tbody tr:hover { background: #fefafb; }
.tbl__name { cursor: pointer; }
.tbl__id { display: flex; align-items: center; gap: 9px; font-size: 13.5px; font-weight: 500; color: #3d2530; }
.tbl__sub { font-size: 13px; color: #7a5c68; }
.tbl__edit { cursor: text; }
.tbl__edit:hover { background: #fdf2f6; }
.tbl__act { text-align: right; }
.cell-input { width: 100%; height: 30px; border: 1px solid #d4567f; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 13px; color: #3d2530; outline: none; font-family: inherit; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.1); }
.status-select { height: 30px; border: 1px solid #ecd0da; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 12.5px; color: #3d2530; outline: none; font-family: inherit; cursor: pointer; }
.status-select:focus { border-color: #d4567f; }

.form { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg--full { grid-column: 1 / -1; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }

.avatar-row { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.avatar-row__btns { display: flex; flex-direction: column; gap: 6px; }

.ai-parse-section { margin-bottom: 6px; padding: 12px; background: #fdf2f6; border: 1px dashed #ecd0da; border-radius: 9px; }
.ai-parse-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.ai-parse-header > span { font-size: 12px; font-weight: 700; color: #b8456a; }
.ai-toggle-btn { border: none; background: none; color: #d4567f; font-size: 11.5px; font-weight: 600; cursor: pointer; padding: 2px 6px; border-radius: 5px; }
.ai-toggle-btn:hover:not(:disabled) { background: #fbeef3; }
.ai-toggle-btn:disabled { color: #c9aab5; cursor: default; }
.ai-parse-body { margin-top: 8px; display: flex; flex-direction: column; }
.field--area { min-height: 70px; resize: vertical; padding: 8px 11px; font-size: 12.5px; }
.doc-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.doc-chip { display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; color: #7a5c68; background: #fff; border: 1px solid #f0d3dd; border-radius: 6px; padding: 3px 8px; }

@media (max-width: 1280px) {
  .kanban { grid-template-columns: repeat(6, minmax(200px, 1fr)); min-width: 1240px; height: auto; align-items: flex-start; }
  .kan-col__body { overflow: visible; }
}

@media (max-width: 760px) {
  .ws-head { height: auto; min-height: 56px; align-items: flex-start; flex-direction: column; padding: 12px 16px; }
  .ws-head__actions { width: 100%; margin-left: 0; justify-content: space-between; }
  .ws-body { padding: 16px; }
}
</style>
