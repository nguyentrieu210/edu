<template>
  <div class="ai">
    <div class="ai__btns">
      <button v-for="a in actions" :key="a.label" class="ai-chip" :disabled="busy" @click="run(a)">
        <FeatherIcon v-if="a.icon" :name="a.icon" style="width:13px;height:13px;" /> {{ a.label }}
      </button>
    </div>
    <div v-if="busy || out" class="ai__out">
      <div v-if="busy" class="ai__loading">AI đang soạn…</div>
      <p v-else class="ai__text">{{ out }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call } from '../../api'
import { toast } from '../../utils/toast'
import branding from '../../config/branding'

const props = defineProps({
  // [{ label, icon?, prompt }]
  actions: { type: Array, default: () => [] },
  systemPrompt: { type: String, default: `Bạn là trợ lý của ${branding.brandName} Education. Trả lời ngắn gọn, thực tế bằng tiếng Việt.` },
  context: { type: String, default: '' }, // dữ liệu nền do trang cung cấp
  temperature: { type: Number, default: 0.5 },
  maxTokens: { type: Number, default: 700 },
})

const busy = ref(false)
const out = ref('')

async function run(a) {
  busy.value = true
  out.value = ''
  try {
    const messages = [
      { role: 'system', content: props.systemPrompt },
      { role: 'user', content: `${a.prompt}\n\nDữ liệu:\n${props.context}` },
    ]
    out.value = await call('ai_chat', { messages, temperature: props.temperature, max_tokens: props.maxTokens })
  } catch (e) {
    toast.error('AI thất bại', e?.message || String(e))
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.ai { display: flex; flex-direction: column; gap: 10px; }
.ai__btns { display: flex; flex-wrap: wrap; gap: 7px; }
.ai-chip { display: inline-flex; align-items: center; gap: 5px; border: 1px solid #ecd0da; background: #fff; color: #b8456a; font-size: 12px; font-weight: 600; padding: 6px 10px; border-radius: 8px; cursor: pointer; font-family: inherit; }
.ai-chip:hover:not(:disabled) { background: #fbeef3; border-color: #ecbcce; }
.ai-chip:disabled { opacity: 0.5; cursor: default; }
.ai__out { background: #fdf2f6; border: 1px solid #f3d9e1; border-radius: 10px; padding: 12px 13px; }
.ai__loading { font-size: 12.5px; color: #b8456a; }
.ai__text { margin: 0; font-size: 13px; color: #4a2230; white-space: pre-wrap; word-break: break-word; line-height: 1.55; }
</style>
