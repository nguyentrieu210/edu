<template>
  <span>
    <SkButton size="sm" variant="secondary" left-icon="file-text" @click="open = true">Excel</SkButton>

    <SkModal v-model="open" :title="`Excel · ${label}`" width="460px">
      <div class="xl">
        <div class="xl__row">
          <div class="xl__info">
            <div class="xl__t">Tải form mẫu</div>
            <div class="xl__d">File .xlsx có sẵn cột để điền và nhập lại.</div>
          </div>
          <SkButton size="sm" variant="secondary" left-icon="download" @click="dl(templateMethod)">Tải mẫu</SkButton>
        </div>

        <div class="xl__row">
          <div class="xl__info">
            <div class="xl__t">Xuất danh sách</div>
            <div class="xl__d">Tải toàn bộ {{ label }} hiện có ra Excel.</div>
          </div>
          <SkButton size="sm" variant="secondary" left-icon="upload" @click="dl(exportMethod)">Xuất</SkButton>
        </div>

        <div class="xl__row xl__row--import">
          <div class="xl__info">
            <div class="xl__t">Nhập từ Excel</div>
            <div class="xl__d">Chọn file .xlsx theo đúng form mẫu để tạo hàng loạt.</div>
          </div>
          <SkButton size="sm" variant="solid" :loading="importing" left-icon="file-plus" @click="fileInput?.click()">
            Chọn file
          </SkButton>
          <input ref="fileInput" type="file" accept=".xlsx" hidden @change="onPick" />
        </div>

        <div v-if="result" class="xl__result" :class="{ 'xl__result--err': result.errors.length }">
          <div class="xl__rsum">
            Đã nhập <b>{{ result.created }}</b>/{{ result.total }} dòng.
            <span v-if="result.errors.length">{{ result.errors.length }} dòng lỗi:</span>
          </div>
          <ul v-if="result.errors.length" class="xl__errs">
            <li v-for="(e, i) in result.errors.slice(0, 15)" :key="i">{{ e }}</li>
            <li v-if="result.errors.length > 15">… và {{ result.errors.length - 15 }} dòng khác</li>
          </ul>
        </div>
      </div>
    </SkModal>
  </span>
</template>

<script setup>
import { ref } from 'vue'
import { call, uploadFile, downloadViaUrl } from '../api'
import { toast } from '../utils/toast'
import SkButton from './ui/SkButton.vue'
import SkModal from './ui/SkModal.vue'

const props = defineProps({
  label: { type: String, default: 'bản ghi' },
  exportMethod: { type: String, required: true },
  templateMethod: { type: String, required: true },
  importMethod: { type: String, required: true },
})
const emit = defineEmits(['imported'])

const open = ref(false)
const importing = ref(false)
const result = ref(null)
const fileInput = ref(null)

function dl(method) {
  try {
    downloadViaUrl(method)
  } catch (e) {
    toast.error('Không tải được file', e?.message || String(e))
  }
}

async function onPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  importing.value = true
  result.value = null
  try {
    const up = await uploadFile(file, { isPrivate: true })
    const res = await call(props.importMethod, { file_url: up.file_url })
    result.value = res
    if (res.created) {
      toast.success(`Đã nhập ${res.created}/${res.total} dòng`)
      emit('imported')
    } else {
      toast.info('Không có dòng nào được nhập')
    }
  } catch (err) {
    toast.error('Nhập Excel thất bại', err?.messages?.[0] || err?.message || String(err))
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.xl { display: flex; flex-direction: column; gap: 4px; }
.xl__row { display: flex; align-items: center; gap: 12px; padding: 13px 2px; border-bottom: 1px solid #f4dde5; }
.xl__row:last-of-type { border-bottom: none; }
.xl__row--import { flex-wrap: wrap; }
.xl__info { flex: 1; min-width: 0; }
.xl__t { font-size: 13px; font-weight: 600; color: #3d2530; }
.xl__d { font-size: 11.5px; color: #a98c98; margin-top: 2px; }
.xl__result { margin-top: 8px; background: #f0f9f3; border: 1px solid #c9e8d4; border-radius: 9px; padding: 10px 12px; }
.xl__result--err { background: #fdf2f6; border-color: #f3cdd6; }
.xl__rsum { font-size: 12.5px; color: #3d2530; }
.xl__errs { margin: 6px 0 0; padding-left: 18px; font-size: 11.5px; color: #b8456a; display: flex; flex-direction: column; gap: 2px; }
</style>
