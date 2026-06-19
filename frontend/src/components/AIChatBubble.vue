<template>
  <!-- AI Chat Bubble -->
  <div class="ai-chat-wrapper">

    <!-- Chat Window -->
    <transition name="chat-window">
      <div
        v-if="isOpen"
        class="chat-window"
      >
        <!-- Header -->
        <div class="chat-header">
          <div class="chat-header-left">
            <div class="ai-avatar-sm">
              <svg viewBox="0 0 24 24" fill="none" class="ai-icon-sm">
                <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.9"/>
                <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div>
              <p class="chat-title">Trợ lý AI</p>
              <div class="online-indicator">
                <span class="online-dot"></span>
                <span class="online-text">Gemini 2.5 Flash</span>
              </div>
            </div>
          </div>
          <div class="chat-header-actions">
            <button @click="clearChat" class="header-btn" title="Xóa cuộc trò chuyện">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
            <button @click="isOpen = false" class="header-btn" title="Đóng">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div class="chat-messages" ref="messagesRef">
          <!-- Welcome -->
          <div v-if="messages.length === 0" class="welcome-screen">
            <div class="welcome-avatar">
              <svg viewBox="0 0 24 24" fill="none" class="welcome-icon">
                <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.9"/>
                <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <h3 class="welcome-title">Xin chào! 👋</h3>
            <p class="welcome-desc">Tôi là trợ lý AI của IKE Ohashi. Tôi có thể giúp bạn với quản lý học viên, tài chính, lịch lớp và nhiều hơn nữa.</p>
            <div class="quick-chips">
              <button
                v-for="chip in quickChips"
                :key="chip"
                @click="sendQuickChip(chip)"
                class="quick-chip"
              >{{ chip }}</button>
            </div>
          </div>

          <!-- Message list -->
          <div
            v-for="(msg, idx) in displayMessages"
            :key="idx"
            :class="['message-row', msg.role === 'user' ? 'user-row' : 'ai-row']"
          >
            <div v-if="msg.role === 'model'" class="ai-bubble-avatar">
              <svg viewBox="0 0 24 24" fill="none" class="bubble-ai-icon">
                <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor"/>
                <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div :class="['message-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
              <div class="bubble-text whitespace-pre-line">{{ msg.parts[0].text }}</div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isLoading" class="message-row ai-row">
            <div class="ai-bubble-avatar">
              <svg viewBox="0 0 24 24" fill="none" class="bubble-ai-icon">
                <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor"/>
                <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="ai-bubble typing-bubble">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input-area">
          <div class="input-container">
            <textarea
              v-model="inputText"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact="() => {}"
              placeholder="Nhắn tin với trợ lý AI..."
              class="chat-textarea"
              :disabled="isLoading"
              rows="1"
              ref="textareaRef"
              @input="autoResize"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="!inputText.trim() || isLoading"
              class="send-btn"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="send-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </div>
          <p class="powered-by">Powered by Gemini 2.5 Flash · Enter để gửi · Shift+Enter xuống dòng</p>
        </div>
      </div>
    </transition>

    <!-- Floating Bubble Button -->
    <button
      @click="isOpen = !isOpen"
      class="bubble-btn"
      :class="{ 'bubble-active': isOpen }"
      title="Trợ lý AI"
    >
      <transition name="icon-swap" mode="out-in">
        <span v-if="!isOpen" key="open" class="bubble-icon-wrap">
          <!-- AI sparkle icon -->
          <svg viewBox="0 0 28 28" fill="none" class="bubble-svg">
            <circle cx="14" cy="14" r="14" fill="url(#aiGrad)"/>
            <defs>
              <radialGradient id="aiGrad" cx="30%" cy="30%">
                <stop offset="0%" stop-color="#FF4D6D"/>
                <stop offset="100%" stop-color="#E4002B"/>
              </radialGradient>
            </defs>
            <!-- Sparkle star -->
            <path d="M14 6 L15.2 11.8 L21 13 L15.2 14.2 L14 20 L12.8 14.2 L7 13 L12.8 11.8 Z" fill="white" opacity="0.95"/>
            <circle cx="19" cy="8" r="1.2" fill="white" opacity="0.7"/>
            <circle cx="9" cy="19" r="0.8" fill="white" opacity="0.5"/>
          </svg>
          <!-- Unread badge -->
          <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }}</span>
        </span>
        <span v-else key="close" class="bubble-icon-wrap">
          <svg viewBox="0 0 28 28" fill="none" class="bubble-svg">
            <circle cx="14" cy="14" r="14" fill="#1e293b"/>
            <path d="M9 9l10 10M19 9l-10 10" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </span>
      </transition>
    </button>

  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { call } from '../api'

const isOpen = ref(false)
const isLoading = ref(false)
const inputText = ref('')
const messages = ref([])  // { role: 'user'|'assistant', content: string }
const messagesRef = ref(null)
const textareaRef = ref(null)
const unreadCount = ref(0)

const quickChips = [
  'Hôm nay có bao nhiêu học viên?',
  'Tổng doanh thu tháng này',
  'Lớp học nào đang diễn ra?',
  'Hỗ trợ tôi soạn email',
]

const systemPrompt = `Bạn là trợ lý AI của IKE Ohashi - hệ thống ERP giáo dục. 
Bạn giúp đội ngũ quản lý với: quản lý học viên, lịch lớp, tài chính (hóa đơn, phiếu thu), 
nhân sự giáo viên, CRM khách hàng tiềm năng và lịch hẹn tư vấn.
Trả lời ngắn gọn, thân thiện, chuyên nghiệp bằng tiếng Việt.
Nếu cần số liệu cụ thể từ hệ thống, hãy hướng dẫn người dùng kiểm tra trên các module tương ứng.`

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const autoResize = () => {
  const ta = textareaRef.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'
}

const escapeHtml = (value) => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

const formatMessage = (text) => {
  if (!text) return ''
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code style="background:#f1f5f9;padding:1px 4px;border-radius:3px;font-family:monospace;font-size:0.85em">$1</code>')
    .replace(/\n/g, '<br/>')
}

// For rendering: map role 'assistant' -> 'model' display, keep parts[] compatible
const displayMessages = computed(() =>
  messages.value.map(m => ({
    role: m.role === 'assistant' ? 'model' : m.role,
    parts: [{ text: m.content }]
  }))
)

const sendQuickChip = (chip) => {
  inputText.value = chip
  sendMessage()
}

const clearChat = () => {
  messages.value = []
  unreadCount.value = 0
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  isLoading.value = true
  await scrollToBottom()

  try {
    // Build messages for Groq (OpenAI format)
    const chatMessages = [
      { role: 'system', content: systemPrompt },
      ...messages.value.slice(-20).map(m => ({
        role: m.role,
        content: m.content
      }))
    ]

    const aiText = await call('ai_chat', {
      messages: JSON.stringify(chatMessages),
      temperature: 0.7,
      max_tokens: 1024,
    })

    if (!aiText) throw new Error('Phản hồi rỗng từ AI')

    messages.value.push({ role: 'assistant', content: aiText })
    if (!isOpen.value) unreadCount.value++

  } catch (err) {
    console.error('[AI Chat Error]', err)
    messages.value.push({
      role: 'assistant',
      content: `❌ Lỗi: ${err.message}`
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// Reset unread when opening
watch(isOpen, (val) => {
  if (val) unreadCount.value = 0
})

// Cho phép mở chat từ bên ngoài (nút "AI Assistant" ở sidebar)
defineExpose({
  open: () => { isOpen.value = true },
  close: () => { isOpen.value = false },
})

</script>

<style scoped>
/* ── Wrapper ─────────────────────────────── */
.ai-chat-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  font-family: 'Inter', sans-serif;
}

/* ── Floating Bubble ─────────────────────── */
.bubble-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(228, 0, 43, 0.35), 0 2px 8px rgba(0,0,0,0.15);
  transition: all 0.25s cubic-bezier(.34,1.56,.64,1);
  position: relative;
}
.bubble-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 28px rgba(228, 0, 43, 0.45), 0 4px 12px rgba(0,0,0,0.2);
}
.bubble-btn:active { transform: scale(0.96); }
.bubble-btn.bubble-active {
  box-shadow: 0 4px 16px rgba(30,41,59,0.4);
}
.bubble-icon-wrap {
  position: relative;
  display: flex;
}
.bubble-svg {
  width: 52px;
  height: 52px;
}
.unread-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid white;
}

/* ── Icon swap transition ────────────────── */
.icon-swap-enter-active, .icon-swap-leave-active {
  transition: all 0.2s ease;
}
.icon-swap-enter-from { opacity: 0; transform: scale(0.6) rotate(-30deg); }
.icon-swap-leave-to { opacity: 0; transform: scale(0.6) rotate(30deg); }

/* ── Chat Window ─────────────────────────── */
.chat-window {
  width: 360px;
  height: 520px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18), 0 4px 16px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(226,232,240,0.8);
}

/* ── Chat Window transition ──────────────── */
.chat-window-enter-active {
  transition: all 0.3s cubic-bezier(.34,1.56,.64,1);
}
.chat-window-leave-active {
  transition: all 0.2s ease;
}
.chat-window-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}
.chat-window-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.97);
}

/* ── Header ──────────────────────────────── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(135deg, #b3001e, #E4002B);
  flex-shrink: 0;
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-avatar-sm {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ai-icon-sm {
  width: 18px;
  height: 18px;
  color: white;
}
.chat-title {
  font-size: 14px;
  font-weight: 700;
  color: white;
  margin: 0;
  line-height: 1.2;
}
.online-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 1px;
}
.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #86efac;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.online-text {
  font-size: 10px;
  color: rgba(255,255,255,0.8);
  font-weight: 500;
}
.chat-header-actions {
  display: flex;
  gap: 4px;
}
.header-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  color: white;
}
.header-btn:hover { background: rgba(255,255,255,0.25); }
.btn-icon { width: 14px; height: 14px; }

/* ── Messages ────────────────────────────── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 2px; }

/* ── Welcome screen ──────────────────────── */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 16px;
  gap: 10px;
}
.welcome-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #E4002B, #FF4D6D);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(228,0,43,0.3);
}
.welcome-icon {
  width: 28px;
  height: 28px;
  color: white;
}
.welcome-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.welcome-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}
.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-top: 4px;
}
.quick-chip {
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
  font-weight: 500;
}
.quick-chip:hover {
  background: #FBE0E5;
  border-color: #fca5a5;
  color: #E4002B;
}

/* ── Message Rows ────────────────────────── */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}
.user-row { flex-direction: row-reverse; }
.ai-row { flex-direction: row; }

.ai-bubble-avatar {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #E4002B, #FF4D6D);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.bubble-ai-icon {
  width: 12px;
  height: 12px;
  color: white;
}

.message-bubble {
  max-width: 76%;
  padding: 9px 12px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.55;
}
.user-bubble {
  background: linear-gradient(135deg, #E4002B, #FF4D6D);
  color: white;
  border-bottom-right-radius: 4px;
}
.ai-bubble {
  background: #f1f5f9;
  color: #1e293b;
  border-bottom-left-radius: 4px;
}
.bubble-text { word-break: break-word; }

/* ── Typing indicator ────────────────────── */
.typing-bubble {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typing 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* ── Input area ──────────────────────────── */
.chat-input-area {
  padding: 12px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  background: #fff;
}
.input-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  padding: 8px 10px;
  transition: border-color 0.2s;
}
.input-container:focus-within {
  border-color: #E4002B;
  box-shadow: 0 0 0 3px rgba(228,0,43,0.1);
}
.chat-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 13px;
  color: #1e293b;
  resize: none;
  font-family: inherit;
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
}
.chat-textarea::placeholder { color: #94a3b8; }
.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #E4002B, #FF4D6D);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
  color: white;
}
.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 3px 10px rgba(228,0,43,0.35);
}
.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.send-icon { width: 16px; height: 16px; }
.powered-by {
  font-size: 10px;
  color: #94a3b8;
  text-align: center;
  margin: 6px 0 0;
}
</style>
