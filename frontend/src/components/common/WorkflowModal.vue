<template>
  <SkModal :model-value="modelValue" :title="title" width="520px" @update:model-value="(v) => emit('update:modelValue', v)">
    <div v-if="subtitle" class="wf-sub">{{ subtitle }}</div>

    <!-- Chọn hành động (nếu nhiều) -->
    <div v-if="actions.length > 1" class="wf-acts">
      <button
        v-for="a in actions"
        :key="a.value"
        type="button"
        class="wf-act"
        :class="{ 'wf-act--on': current === a.value }"
        @click="select(a.value)"
      >{{ a.label }}</button>
    </div>

    <p v-if="activeAction?.hint" class="wf-hint">{{ activeAction.hint }}</p>

    <!-- Field của hành động đang chọn -->
    <form v-if="activeAction" class="wf-form" @submit.prevent="confirm">
      <label v-for="f in (activeAction.fields || [])" :key="f.key" class="wf-fg" :class="{ 'wf-fg--full': f.full || f.type === 'textarea' }">
        <span>{{ f.label }}<template v-if="f.required"> *</template></span>
        <select v-if="f.type === 'select'" v-model="form[f.key]" class="wf-field">
          <option value="">{{ f.placeholder || '— Chọn —' }}</option>
          <option v-for="o in normOpts(f.options)" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
        <textarea v-else-if="f.type === 'textarea'" v-model="form[f.key]" class="wf-field wf-field--area" :placeholder="f.placeholder" />
        <input v-else v-model="form[f.key]" :type="f.type === 'number' ? 'number' : (f.type === 'date' ? 'date' : 'text')" class="wf-field" :placeholder="f.placeholder" :step="f.step" />
      </label>
    </form>

    <template #footer>
      <SkButton variant="secondary" :disabled="saving" @click="emit('update:modelValue', false)">Hủy</SkButton>
      <SkButton variant="solid" :loading="saving" :disabled="!activeAction" @click="confirm">{{ activeAction?.confirmLabel || 'Xác nhận' }}</SkButton>
    </template>
  </SkModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { toast } from '../../utils/toast'
import SkModal from '../ui/SkModal.vue'
import SkButton from '../ui/SkButton.vue'

const props = defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'Thao tác' },
  subtitle: { type: String, default: '' },
  // [{ value, label, hint?, confirmLabel?, fields?: [{key,label,type,options,required,placeholder,full,step,default}], run: async(form)=>result }]
  actions: { type: Array, default: () => [] },
  preset: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'done'])

const current = ref('')
const form = ref({})
const saving = ref(false)

const activeAction = computed(() => props.actions.find((a) => a.value === current.value) || null)
const normOpts = (opts = []) => opts.map((o) => (typeof o === 'object' ? o : { value: o, label: o || '—' }))

function resetForm(action) {
  const f = {}
  for (const fld of action?.fields || []) f[fld.key] = fld.default ?? ''
  form.value = f
}
function select(val) {
  current.value = val
  resetForm(props.actions.find((a) => a.value === val))
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    const initial = props.actions.find((a) => a.value === props.preset) ? props.preset : (props.actions.length === 1 ? props.actions[0].value : '')
    current.value = initial
    resetForm(props.actions.find((a) => a.value === initial))
  },
)

async function confirm() {
  const action = activeAction.value
  if (!action) { toast.error('Chọn một thao tác'); return }
  for (const f of action.fields || []) {
    if (f.required && !form.value[f.key]) { toast.error(`Cần nhập: ${f.label}`); return }
  }
  saving.value = true
  try {
    const res = await action.run({ ...form.value })
    toast.success(action.successMsg || 'Đã thực hiện')
    emit('update:modelValue', false)
    emit('done', { action: action.value, result: res })
  } catch (e) {
    toast.error('Thao tác thất bại', e?.messages?.[0] || e?.message || String(e))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.wf-sub { font-size: 13px; color: #7a5c68; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #f4dde5; }
.wf-acts { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.wf-act { border: 1px solid #ecd0da; background: #fff; color: #7a5c68; font-size: 12.5px; font-weight: 600; padding: 8px 13px; border-radius: 9px; cursor: pointer; font-family: inherit; transition: all 0.12s ease; }
.wf-act:hover { border-color: #ecbcce; background: #fdf2f6; }
.wf-act--on { border-color: #d4567f; background: #d4567f; color: #fff; box-shadow: 0 3px 9px rgba(212, 86, 127, 0.28); }
.wf-hint { margin: 0 0 12px; font-size: 12.5px; color: #9b7a86; background: #fdf2f6; border: 1px dashed #ecd0da; border-radius: 9px; padding: 10px 12px; }
.wf-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.wf-fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.wf-fg--full { grid-column: 1 / -1; }
.wf-fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.wf-field { width: 100%; min-height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.wf-field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }
.wf-field--area { min-height: 70px; resize: vertical; padding: 8px 11px; }
</style>
