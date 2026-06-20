<template>
  <teleport to="body">
    <!-- Chat panel -->
    <transition name="fade">
      <div v-if="isOpen" class="aib-panel">
        <div class="ai-head">
          <div class="ai-logo">
            <FeatherIcon name="zap" style="width:16px;height:16px;color:#fff;" />
          </div>
          <span class="ai-title">Trợ lý AI</span>
          <button class="ai-x" aria-label="Đóng" @click="close">
            <FeatherIcon name="x" style="width:18px;height:18px;" />
          </button>
        </div>

        <div ref="scrollRef" class="ai-body sk-scroll">
          <div class="ai-ctx">Ngữ cảnh: <b>{{ contextLabel }}</b></div>

          <template v-for="(m, i) in messages" :key="i">
            <div v-if="m.role === 'user'" class="ai-msg ai-msg--user">{{ m.content }}</div>
            <div v-else class="ai-msg ai-msg--bot" v-html="format(m.content)" />
          </template>

          <div v-if="loading" class="ai-msg ai-msg--bot ai-typing">
            <span class="ai-dot" /><span class="ai-dot" /><span class="ai-dot" />
          </div>

          <div v-if="!messages.length" class="ai-chips">
            <button v-for="c in chips" :key="c" class="ai-chip" @click="quick(c)">{{ c }}</button>
          </div>

          <div class="ai-note">AI không tự thay đổi dữ liệu — mọi đề xuất cần bạn xác nhận.</div>
        </div>

        <div class="ai-foot">
          <div class="ai-inputwrap">
            <input v-model="input" class="ai-input" placeholder="Hỏi về học viên, lớp, công nợ…" @keydown.enter="send" />
            <button class="ai-send" :disabled="!input.trim() || loading" @click="send">
              <FeatherIcon name="send" style="width:15px;height:15px;" />
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Floating bubble -->
    <button class="aib-fab" :class="{ 'aib-fab--open': isOpen }" :aria-label="isOpen ? 'Đóng trợ lý AI' : 'Mở trợ lý AI'" @click="toggle">
      <FeatherIcon :name="isOpen ? 'x' : 'message-circle'" style="width:24px;height:24px;color:#fff;" />
    </button>
  </teleport>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call } from '../api'

const isOpen = ref(false)
const loading = ref(false)
const input = ref('')
const messages = ref([])
const scrollRef = ref(null)
const contextLabel = ref('Tổng quan hệ thống')

const chips = [
  'Hôm nay có bao nhiêu học viên?',
  'Lớp nào đang thiếu sĩ số?',
  'Tổng công nợ hiện tại',
]

const systemPrompt = `Bạn là trợ lý AI của IKE Ohashi — hệ thống ERP giáo dục tiếng Nhật.
Giúp giáo vụ về: học viên, lớp học, điểm danh, học phí, CRM tuyển sinh.
Trả lời ngắn gọn, thân thiện, chuyên nghiệp bằng tiếng Việt. Không bịa số liệu.`

function open(ctx) {
  if (ctx) contextLabel.value = ctx
  isOpen.value = true
  scrollBottom()
}
function close() { isOpen.value = false }
function toggle() { isOpen.value ? close() : open() }
defineExpose({ open, close, toggle })

function format(t) {
  if (!t) return ''
  return String(t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

async function scrollBottom() {
  await nextTick()
  if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
}

function quick(c) { input.value = c; send() }

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await scrollBottom()
  try {
    const payload = [
      { role: 'system', content: systemPrompt },
      ...messages.value.slice(-20).map((m) => ({ role: m.role, content: m.content })),
    ]
    const reply = await call('ai_chat', { messages: payload, temperature: 0.7, max_tokens: 1024 })
    messages.value.push({ role: 'assistant', content: reply || 'Xin lỗi, hiện chưa trả lời được.' })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: 'Lỗi gọi AI: ' + (e?.message || e) })
  } finally {
    loading.value = false
    await scrollBottom()
  }
}
</script>

<style scoped>
/* Floating action button — góc dưới bên phải */
.aib-fab {
  position: fixed; right: 22px; bottom: 22px; z-index: 70;
  width: 56px; height: 56px; border-radius: 50%; border: none; cursor: pointer;
  background: linear-gradient(135deg, #e87aa3, #d4567f);
  box-shadow: 0 8px 22px rgba(214, 85, 126, 0.45);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.aib-fab:hover { transform: translateY(-2px) scale(1.04); box-shadow: 0 12px 28px rgba(214, 85, 126, 0.5); }
.aib-fab--open { background: linear-gradient(135deg, #d4567f, #b8456a); }

/* Chat popup neo góc dưới phải, ngay trên FAB */
.aib-panel {
  position: fixed; right: 22px; bottom: 88px; z-index: 70;
  width: 380px; max-width: calc(100vw - 36px);
  height: 560px; max-height: calc(100vh - 120px);
  display: flex; flex-direction: column;
  background: #fffdfe; border: 1px solid #f1dbe3; border-radius: 16px;
  box-shadow: 0 18px 48px rgba(160, 60, 100, 0.28); overflow: hidden;
  animation: skpop 0.2s ease;
}
.ai-head { height: 54px; flex: none; display: flex; align-items: center; gap: 10px; padding: 0 16px; border-bottom: 1px solid #f1dbe3; }
.ai-logo { width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, #f7a8c4, #d6557e); display: flex; align-items: center; justify-content: center; }
.ai-title { font-size: 15px; font-weight: 600; color: #3d2530; }
.ai-x { margin-left: auto; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border: none; background: none; border-radius: 7px; cursor: pointer; color: #b07e90; }
.ai-x:hover { background: #fbe6ee; }
.ai-body { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.ai-ctx { font-size: 11.5px; color: #a98c98; background: #fdf2f6; border-radius: 8px; padding: 9px 12px; }
.ai-ctx b { color: #b8456a; }
.ai-msg { max-width: 90%; padding: 11px 14px; font-size: 13px; line-height: 1.55; }
.ai-msg--user { align-self: flex-end; background: linear-gradient(135deg, #e87aa3, #d4567f); color: #fff; border-radius: 14px 14px 4px 14px; }
.ai-msg--bot { align-self: flex-start; background: #fbeef3; color: #3d2530; border-radius: 14px 14px 14px 4px; }
.ai-typing { display: flex; gap: 4px; align-items: center; }
.ai-dot { width: 6px; height: 6px; border-radius: 50%; background: #d6557e; opacity: 0.5; animation: skshimmer 1s infinite; }
.ai-dot:nth-child(2) { animation-delay: 0.15s; }
.ai-dot:nth-child(3) { animation-delay: 0.3s; }
.ai-chips { display: flex; flex-direction: column; gap: 8px; }
.ai-chip { text-align: left; border: 1px solid #f1d2de; background: #fff; border-radius: 9px; padding: 9px 12px; font-family: inherit; font-size: 12.5px; color: #7a5c68; cursor: pointer; }
.ai-chip:hover { background: #fdf2f6; }
.ai-note { font-size: 11px; color: #bd97a5; text-align: center; margin-top: auto; }
.ai-foot { flex: none; padding: 12px 14px; border-top: 1px solid #f1dbe3; }
.ai-inputwrap { display: flex; align-items: center; gap: 8px; height: 42px; padding: 0 6px 0 14px; border-radius: 12px; background: #fdf2f6; border: 1px solid #f1d2de; }
.ai-input { flex: 1; border: none; background: none; outline: none; font-family: inherit; font-size: 13px; color: #3d2530; }
.ai-input::placeholder { color: #bd8d9c; }
.ai-send { width: 30px; height: 30px; border: none; border-radius: 8px; background: linear-gradient(135deg, #e87aa3, #d4567f); color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.ai-send:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 480px) {
  .aib-panel { right: 12px; left: 12px; width: auto; bottom: 84px; }
  .aib-fab { right: 16px; bottom: 16px; }
}
</style>
