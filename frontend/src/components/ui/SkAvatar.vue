<template>
  <span class="av sk-av-wrap" :class="{ 'sk-av-wrap--edit': editable }" :style="wrapStyle" @click="onClick">
    <img v-if="src" class="sk-av sk-av--img" :src="src" :style="style" :alt="name" />
    <span v-else class="sk-av" :style="style">{{ initials }}</span>

    <span v-if="editable" class="sk-av__overlay">
      <span v-if="uploading" class="sk-spin sk-av__spin" />
      <FeatherIcon v-else name="camera" :style="{ width: iconSize, height: iconSize }" />
    </span>
    <input v-if="editable" ref="fileInput" type="file" accept="image/*" hidden @click.stop @change="onPick" />
  </span>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { uploadFile, db } from '../../api'
import { toast } from '../../utils/toast'

const GRADIENTS = [
  'linear-gradient(135deg,#f7a8c4,#d6557e)',
  'linear-gradient(135deg,#f6b8a0,#e07a8f)',
  'linear-gradient(135deg,#c9a6e0,#9b6fc4)',
  'linear-gradient(135deg,#f5a3b8,#cf5b86)',
  'linear-gradient(135deg,#f0b27a,#d97b6a)',
]

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 38 },
  src: { type: String, default: '' },
  // Bật chế độ bấm-để-tải-ảnh. Cần đủ doctype + docname + field.
  editable: { type: Boolean, default: false },
  uploadDoctype: { type: String, default: '' },
  uploadName: { type: String, default: '' },
  uploadField: { type: String, default: '' },
})
const emit = defineEmits(['update:src'])

const fileInput = ref(null)
const uploading = ref(false)

const initials = computed(() => {
  const n = (props.name || '?').trim()
  if (!n) return '?'
  const p = n.split(/\s+/)
  return ((p[0]?.[0] || '') + (p.length > 1 ? p[p.length - 1][0] : '')).toUpperCase()
})

const style = computed(() => {
  let h = 0
  for (const c of (props.name || '')) h = (h * 31 + c.charCodeAt(0)) % 997
  const g = GRADIENTS[h % GRADIENTS.length]
  return {
    width: `${props.size}px`,
    height: `${props.size}px`,
    background: props.src ? '#f3d9e1' : g,
    fontSize: `${Math.round(props.size * 0.38)}px`,
  }
})
const wrapStyle = computed(() => ({ width: `${props.size}px`, height: `${props.size}px` }))
const iconSize = computed(() => `${Math.max(12, Math.round(props.size * 0.38))}px`)

function onClick(e) {
  if (!props.editable) return
  e.stopPropagation() // không lan ra hàng/card (mở chi tiết)
  if (uploading.value) return
  fileInput.value?.click()
}

async function onPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!props.uploadDoctype || !props.uploadName || !props.uploadField) {
    toast.error('Thiếu thông tin để lưu ảnh')
    return
  }
  uploading.value = true
  try {
    // 1) Upload kèm doctype/docname/fieldname để Frappe GẮN file vào hồ sơ (không mồ côi).
    const res = await uploadFile(file, {
      isPrivate: false,
      doctype: props.uploadDoctype,
      docname: props.uploadName,
      fieldname: props.uploadField,
    })
    // 2) upload_file CHỈ đính kèm chứ không tự set giá trị field -> phải setValue.
    await db.setValue(props.uploadDoctype, props.uploadName, props.uploadField, res.file_url)
    emit('update:src', res.file_url)
    toast.success('Đã cập nhật ảnh')
  } catch (err) {
    toast.error('Tải ảnh thất bại', err?.messages?.[0] || err?.message || String(err))
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.sk-av-wrap { flex: none; display: inline-flex; position: relative; }
.sk-av {
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; color: #fff; font-weight: 600; line-height: 1;
}
.sk-av--img { object-fit: cover; }

.sk-av-wrap--edit { cursor: pointer; }
.sk-av__overlay {
  position: absolute; inset: 0; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; background: rgba(60, 20, 35, 0.42);
  opacity: 0; transition: opacity 0.14s ease;
}
.sk-av-wrap--edit:hover .sk-av__overlay { opacity: 1; }
.sk-av__spin { width: 40%; height: 40%; border: 2px solid rgba(255,255,255,0.5); border-top-color: #fff; border-radius: 50%; }
</style>
