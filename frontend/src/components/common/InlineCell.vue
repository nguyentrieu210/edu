<template>
  <span class="ic" :class="{ 'ic--editing': editing }">
    <template v-if="editing">
      <select
        v-if="type === 'select'"
        ref="inputEl"
        v-model="draft"
        class="ic__field"
        @change="commit"
        @blur="commit"
        @keydown.esc="cancel"
      >
        <option v-for="o in normOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
      <input
        v-else
        ref="inputEl"
        v-model="draft"
        :type="type === 'number' ? 'number' : (type === 'date' ? 'date' : 'text')"
        class="ic__field"
        @blur="commit"
        @keydown.enter.prevent="commit"
        @keydown.esc="cancel"
      />
      <span v-if="saving" class="ic__spin sk-spin" />
    </template>
    <span v-else class="ic__view" :title="'Bấm để sửa'" @click="start">
      <span class="ic__text" :class="{ 'ic__text--empty': isEmpty }">{{ shownText }}</span>
      <FeatherIcon name="edit-2" class="ic__pen" />
    </span>
  </span>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { db } from '../../api'
import { toast } from '../../utils/toast'

const props = defineProps({
  doctype: { type: String, required: true },
  name: { type: String, required: true },
  field: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' }, // text | select | date | number
  options: { type: Array, default: () => [] }, // ['A'] hoặc [{value,label}]
  display: { type: String, default: '' }, // text hiển thị tùy biến (vd nhãn VN)
  placeholder: { type: String, default: '—' },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const editing = ref(false)
const saving = ref(false)
const draft = ref('')
const inputEl = ref(null)

const normOptions = computed(() =>
  props.options.map((o) => (typeof o === 'object' ? o : { value: o, label: o || '—' })),
)
const isEmpty = computed(() => props.modelValue === '' || props.modelValue == null)
const shownText = computed(() => (isEmpty.value ? props.placeholder : (props.display || String(props.modelValue))))

async function start() {
  draft.value = props.modelValue ?? ''
  editing.value = true
  await nextTick()
  inputEl.value?.focus?.()
}
function cancel() {
  editing.value = false
}
async function commit() {
  if (!editing.value) return
  const val = draft.value
  if (val === (props.modelValue ?? '')) { editing.value = false; return }
  saving.value = true
  try {
    await db.setValue(props.doctype, props.name, props.field, val)
    emit('update:modelValue', val)
    emit('saved', val)
    toast.success('Đã lưu')
    editing.value = false
  } catch (e) {
    toast.error('Không lưu được', e?.messages?.[0] || e?.message || String(e))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.ic { display: inline-flex; align-items: center; min-width: 0; max-width: 100%; }
.ic__view { display: inline-flex; align-items: center; gap: 5px; min-width: 0; cursor: text; border-radius: 6px; padding: 1px 4px; margin: -1px -4px; }
.ic__view:hover { background: #fdf2f6; }
.ic__text { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ic__text--empty { color: #c9aab5; }
.ic__pen { width: 11px; height: 11px; color: #d4567f; opacity: 0; flex: none; }
.ic__view:hover .ic__pen { opacity: 0.8; }
.ic__field { width: 100%; min-width: 80px; height: 28px; border: 1px solid #d4567f; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 13px; color: #3d2530; outline: none; font-family: inherit; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.1); }
.ic__spin { width: 13px; height: 13px; border: 2px solid rgba(184, 69, 106, 0.3); border-top-color: #b8456a; border-radius: 50%; margin-left: 6px; flex: none; }
</style>
