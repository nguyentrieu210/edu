<template>
  <span class="pill" :class="variantClass">{{ meta.label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { statusMeta } from '../../utils/labels'

// StatusBadge tự tra nhãn + variant từ (doctype, field, value) — spec §24.2.
// Page KHÔNG truyền chuỗi đã dịch sẵn; chỉ truyền giá trị enum thô.
const props = defineProps({
  doctype: { type: String, required: true },
  field: { type: String, required: true },
  value: { type: String, default: '' },
})

const meta = computed(() => statusMeta(props.doctype, props.field, props.value))

const VARIANT_CLASS = {
  success: 'pill-sage',
  info: 'pill-info',
  warning: 'pill-amber',
  danger: 'pill-rose',
  neutral: 'pill-faint',
}

const variantClass = computed(() => VARIANT_CLASS[meta.value.variant] || 'pill-faint')
</script>
