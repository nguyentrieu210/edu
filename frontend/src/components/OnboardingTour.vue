<template>
  <Teleport to="body">
    <transition name="ob-fade">
      <div v-if="open" class="ob-mask" @click.self="skip">
        <transition name="ob-pop" mode="out-in">
          <div :key="i" class="ob-card">
            <div class="ob-head">
              <div class="ob-ico"><FeatherIcon :name="cur.icon" style="width:26px;height:26px;" /></div>
              <button class="ob-x" aria-label="Đóng" @click="skip"><FeatherIcon name="x" style="width:18px;height:18px;" /></button>
            </div>
            <div class="ob-body">
              <div class="ob-step">Bước {{ i + 1 }}/{{ STEPS.length }}</div>
              <h3 class="ob-title">{{ cur.title }}</h3>
              <p class="ob-desc">{{ cur.desc }}</p>
            </div>
            <div class="ob-dots">
              <span v-for="(s, k) in STEPS" :key="k" class="ob-dot" :class="{ 'ob-dot--on': k === i }" @click="i = k" />
            </div>
            <div class="ob-foot">
              <button class="ob-btn ob-btn--ghost" @click="skip">Bỏ qua</button>
              <div class="ob-foot__r">
                <button v-if="i > 0" class="ob-btn ob-btn--ghost" @click="i--">Trước</button>
                <button v-if="i < STEPS.length - 1" class="ob-btn ob-btn--solid" @click="i++">Tiếp</button>
                <button v-else class="ob-btn ob-btn--solid" @click="finish">Bắt đầu dùng 🎉</button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const KEY = 'edu_onboarded_v1'
const STEPS = [
  { icon: 'compass', title: 'Chào mừng đến Education ERP', desc: 'Hệ thống quản lý trung tâm của IKE Ohashi. Đi nhanh qua các tính năng chính trong 1 phút nhé!' },
  { icon: 'grid', title: 'Bảng điều khiển', desc: 'Trang Dashboard hiển thị realtime: học viên đang học, lớp vận hành, chuyên cần, công nợ, lịch hôm nay và cảnh báo cần xử lý.' },
  { icon: 'user-plus', title: 'Tuyển sinh (CRM)', desc: 'Quản lý lead theo pipeline kéo-thả, đổi giai đoạn (Tư vấn → Test → Học thử → Nhập học), đặt lịch hẹn và ghi nhật ký tư vấn.' },
  { icon: 'users', title: 'Học viên', desc: 'Hồ sơ học viên, người giám hộ, đăng ký lớp (tự sinh học phí + hóa đơn), theo dõi chuyên cần & điểm trung bình.' },
  { icon: 'book-open', title: 'Lớp học & Lên lịch', desc: 'Tạo lớp rồi bấm "Lên lịch học" để sinh buổi theo mẫu 2-4-6 / 3-5-7 / T7-CN. Lưu ý: nhập Giờ bắt đầu & Giờ kết thúc trước khi lên lịch.' },
  { icon: 'check-square', title: 'Điểm danh', desc: 'Điểm danh theo từng buổi học; hệ thống tự cập nhật tỷ lệ chuyên cần cho học viên.' },
  { icon: 'credit-card', title: 'Tài chính', desc: 'Theo dõi hóa đơn, thu tiền, hoàn tiền và in hóa đơn. Nút "In hóa đơn" mở bản in chuẩn.' },
  { icon: 'smartphone', title: 'Cổng Giáo viên & Học viên', desc: 'Hai cổng riêng cho GV và HV. Quản trị viên có thể vào xem thử cả hai cổng để kiểm tra.' },
  { icon: 'shield', title: 'Quản lý tài khoản', desc: 'Tạo/khóa tài khoản, đổi vai trò, gửi lại mail. Khi tạo Học viên/Giáo viên có email, hệ thống tự tạo tài khoản + gửi mail đặt mật khẩu.' },
  { icon: 'zap', title: 'Trợ lý AI ✨', desc: 'Bong bóng AI hỗ trợ gợi ý hành động, nhận xét lớp và đọc hồ sơ. Chúc bạn làm việc hiệu quả!' },
]

const open = ref(false)
const i = ref(0)
const cur = computed(() => STEPS[i.value])

function start() { i.value = 0; open.value = true }
function close() { open.value = false }
function skip() { localStorage.setItem(KEY, '1'); close() }
function finish() { localStorage.setItem(KEY, '1'); close() }

function maybeAutoStart() {
  try { if (!localStorage.getItem(KEY)) start() } catch { /* ignore */ }
}

defineExpose({ start, maybeAutoStart })
</script>

<style scoped>
.ob-mask { position: fixed; inset: 0; z-index: 2000; background: rgba(74, 34, 48, 0.42); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; padding: 16px; }
.ob-card { width: min(440px, 94vw); background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 24px 70px rgba(120, 40, 70, 0.4); }
.ob-head { height: 92px; background: linear-gradient(135deg, #f7a8c4 0%, #d6557e 100%); display: flex; align-items: center; justify-content: center; position: relative; }
.ob-ico { width: 56px; height: 56px; border-radius: 16px; background: rgba(255,255,255,0.22); color: #fff; display: flex; align-items: center; justify-content: center; }
.ob-x { position: absolute; top: 12px; right: 12px; width: 30px; height: 30px; border: none; border-radius: 8px; background: rgba(255,255,255,0.22); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.ob-x:hover { background: rgba(255,255,255,0.35); }
.ob-body { padding: 22px 26px 6px; text-align: center; }
.ob-step { font-size: 12px; font-weight: 700; color: #c98aa0; letter-spacing: 0.5px; }
.ob-title { font-size: 20px; font-weight: 900; color: #4a2230; margin: 8px 0 10px; }
.ob-desc { font-size: 14px; color: #6f5360; line-height: 1.6; min-height: 66px; }
.ob-dots { display: flex; justify-content: center; gap: 7px; padding: 10px 0 4px; }
.ob-dot { width: 7px; height: 7px; border-radius: 50%; background: #f0cdd9; cursor: pointer; transition: all 0.2s; }
.ob-dot--on { background: #d6557e; width: 20px; border-radius: 4px; }
.ob-foot { display: flex; align-items: center; justify-content: space-between; padding: 14px 22px 20px; }
.ob-foot__r { display: flex; gap: 8px; }
.ob-btn { border: none; border-radius: 9px; font-family: inherit; font-weight: 700; font-size: 13.5px; cursor: pointer; padding: 9px 16px; }
.ob-btn--solid { background: linear-gradient(135deg, #ef82a6, #d6557e); color: #fff; box-shadow: 0 5px 14px rgba(214,85,126,0.3); }
.ob-btn--ghost { background: #fbeaf0; color: #b8456a; }
.ob-btn:hover { filter: brightness(1.04); }
/* animations: nhảy nhảy */
.ob-fade-enter-active, .ob-fade-leave-active { transition: opacity 0.25s; }
.ob-fade-enter-from, .ob-fade-leave-to { opacity: 0; }
.ob-pop-enter-active { animation: ob-pop 0.32s cubic-bezier(0.34, 1.56, 0.64, 1); }
.ob-pop-leave-active { transition: opacity 0.12s; opacity: 0; }
@keyframes ob-pop { 0% { transform: scale(0.85) translateY(12px); opacity: 0; } 100% { transform: scale(1) translateY(0); opacity: 1; } }
</style>
