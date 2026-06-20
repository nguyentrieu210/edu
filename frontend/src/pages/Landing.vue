<template>
  <div class="lp">
    <!-- Nav -->
    <header class="lp-nav">
      <div class="lp-nav__brand">
        <div class="lp-logo">
          <svg width="24" height="24" viewBox="0 0 64 64"><g fill="#fff">
            <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(0 32 32)" />
            <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(72 32 32)" />
            <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(144 32 32)" />
            <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(216 32 32)" />
            <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(288 32 32)" />
          </g><circle cx="32" cy="32" r="4.4" fill="#ffd98e" /></svg>
        </div>
        <span class="lp-nav__name font-display">IKE Ohashi</span>
      </div>
      <nav class="lp-nav__links">
        <a href="#features">Tính năng</a>
        <a href="#demo">Demo</a>
        <a href="#contact">Liên hệ</a>
        <button class="lp-btn lp-btn--ghost" @click="goLogin">Đăng nhập</button>
      </nav>
    </header>

    <!-- Hero -->
    <section class="lp-hero">
      <div class="lp-hero__txt">
        <div class="lp-eyebrow">日本語 · Education ERP</div>
        <h1 class="font-display">Quản lý trung tâm giáo dục<br>thông minh & trọn vẹn</h1>
        <p>Tuyển sinh, đào tạo, tài chính, cổng giáo viên – học viên và trợ lý AI — tất cả trong một nền tảng cho IKE Ohashi.</p>
        <div class="lp-hero__cta">
          <button class="lp-btn lp-btn--solid" @click="scrollTo('contact')">Đăng ký tư vấn</button>
          <button class="lp-btn lp-btn--ghost" @click="goLogin">Đăng nhập hệ thống</button>
        </div>
      </div>
      <div class="lp-hero__art">
        <img :src="dashboardImg" alt="Education ERP dashboard" />
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="lp-sec">
      <h2 class="lp-sec__title font-display">Tính năng nổi bật</h2>
      <div class="lp-feats">
        <div v-for="f in FEATURES" :key="f.title" class="lp-feat">
          <div class="lp-feat__ico"><FeatherIcon :name="f.icon" style="width:22px;height:22px;" /></div>
          <div class="lp-feat__title">{{ f.title }}</div>
          <div class="lp-feat__desc">{{ f.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Demo -->
    <section id="demo" class="lp-sec lp-demo">
      <h2 class="lp-sec__title font-display">Giao diện trực quan</h2>
      <p class="lp-sec__sub">Bảng điều khiển realtime: học viên đang học, lớp vận hành, chuyên cần, công nợ.</p>
      <div class="lp-demo__frame"><img :src="dashboardImg" alt="Dashboard demo" /></div>
    </section>

    <!-- Contact / consultation -->
    <section id="contact" class="lp-sec lp-contact">
      <div class="lp-contact__card">
        <h2 class="font-display">Đăng ký tư vấn</h2>
        <p>Để lại thông tin, bộ phận tuyển sinh sẽ liên hệ với bạn.</p>
        <form class="lp-form" @submit.prevent="submit">
          <input v-model.trim="form.full_name" class="lp-field" placeholder="Họ và tên *" :disabled="sent || sending" />
          <input v-model.trim="form.phone" class="lp-field" placeholder="Số điện thoại *" :disabled="sent || sending" />
          <input v-model.trim="form.email" class="lp-field" type="email" placeholder="Email (để nhận xác nhận)" :disabled="sent || sending" />
          <div v-if="err" class="lp-err">{{ err }}</div>
          <div v-if="sent" class="lp-ok">✅ Đã gửi! Cảm ơn bạn, chúng tôi sẽ liên hệ sớm.</div>
          <button v-if="!sent" class="lp-btn lp-btn--solid lp-btn--block" type="submit" :disabled="sending">
            {{ sending ? 'Đang gửi…' : 'Gửi đăng ký' }}
          </button>
        </form>
      </div>
    </section>

    <footer class="lp-foot">
      <div>© IKE Ohashi · Education ERP</div>
      <div class="lp-foot__links"><a href="#features">Tính năng</a> · <button class="lp-foot__link" @click="goLogin">Đăng nhập</button></div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { call } from '../api'
import dashboardImg from '../assets/edu-dashboard.png'

const router = useRouter()
const goLogin = () => router.push('/login')
const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })

const FEATURES = [
  { icon: 'user-plus', title: 'Tuyển sinh & CRM', desc: 'Pipeline lead kéo-thả, lịch hẹn, tư vấn, test xếp lớp.' },
  { icon: 'book-open', title: 'Đào tạo', desc: 'Lớp học, lên lịch tự động, điểm danh theo buổi, tiến độ.' },
  { icon: 'credit-card', title: 'Tài chính', desc: 'Học phí, hóa đơn, thu/hoàn tiền, lương giáo viên, công nợ.' },
  { icon: 'smartphone', title: 'Cổng GV & HV', desc: 'Giáo viên và học viên có cổng riêng, đăng nhập độc lập.' },
  { icon: 'bar-chart-2', title: 'Báo cáo', desc: 'Dashboard realtime và báo cáo vận hành trực quan.' },
  { icon: 'zap', title: 'Trợ lý AI', desc: 'Gợi ý hành động, nhận xét lớp, đọc hồ sơ bằng AI.' },
]

const form = ref({ full_name: '', phone: '', email: '' })
const sending = ref(false)
const sent = ref(false)
const err = ref('')

async function submit() {
  err.value = ''
  if (!form.value.full_name || !form.value.phone) { err.value = 'Vui lòng nhập họ tên và số điện thoại.'; return }
  sending.value = true
  try {
    await call('submit_consultation', { full_name: form.value.full_name, phone: form.value.phone, email: form.value.email || undefined })
    sent.value = true
  } catch (e) {
    err.value = e?.messages?.[0] || e?.message || 'Gửi không thành công, thử lại sau.'
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.lp { min-height: 100vh; width: 100%; overflow-y: auto; background: linear-gradient(160deg, #fff7fa 0%, #fdeaf1 45%, #fbdfeb 100%); color: #3d2530; }
.font-display { font-weight: 900; }
/* nav */
.lp-nav { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 14px 6vw; background: rgba(255,255,255,0.7); backdrop-filter: blur(8px); border-bottom: 1px solid #f3d3df; }
.lp-nav__brand { display: flex; align-items: center; gap: 10px; }
.lp-logo { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(140deg, #f7a8c4, #d6557e); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(214,85,126,0.3); }
.lp-nav__name { font-size: 18px; color: #4a2230; }
.lp-nav__links { display: flex; align-items: center; gap: 22px; }
.lp-nav__links a { color: #7a5c68; text-decoration: none; font-size: 14px; font-weight: 500; }
.lp-nav__links a:hover { color: #d6557e; }
/* buttons */
.lp-btn { border: none; border-radius: 10px; font-family: inherit; font-weight: 700; cursor: pointer; font-size: 14px; padding: 10px 18px; }
.lp-btn--solid { background: linear-gradient(135deg, #ef82a6, #d6557e); color: #fff; box-shadow: 0 6px 16px rgba(214,85,126,0.3); }
.lp-btn--ghost { background: #fff; color: #b8456a; border: 1px solid #f0c3d2; }
.lp-btn--block { width: 100%; padding: 12px; margin-top: 4px; }
.lp-btn:hover { filter: brightness(1.03); }
/* hero */
.lp-hero { display: grid; grid-template-columns: 1.05fr 1fr; gap: 40px; align-items: center; padding: 60px 6vw 50px; }
.lp-eyebrow { font-size: 12.5px; font-weight: 700; color: #b07e90; letter-spacing: 1px; text-transform: uppercase; }
.lp-hero__txt h1 { font-size: 42px; line-height: 1.12; margin: 12px 0 16px; color: #4a2230; }
.lp-hero__txt p { font-size: 16px; color: #7a5c68; line-height: 1.6; max-width: 480px; }
.lp-hero__cta { display: flex; gap: 12px; margin-top: 26px; flex-wrap: wrap; }
.lp-hero__art img { width: 100%; border-radius: 16px; border: 1px solid #f0c3d2; box-shadow: 0 18px 50px rgba(180,80,120,0.22); }
/* sections */
.lp-sec { padding: 56px 6vw; }
.lp-sec__title { font-size: 30px; text-align: center; color: #4a2230; }
.lp-sec__sub { text-align: center; color: #7a5c68; margin-top: 8px; }
.lp-feats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 34px; }
.lp-feat { background: #fff; border: 1px solid #f3d3df; border-radius: 14px; padding: 22px; box-shadow: 0 6px 18px rgba(180,80,120,0.07); }
.lp-feat__ico { width: 46px; height: 46px; border-radius: 12px; background: linear-gradient(140deg, #fde3ec, #f9c9da); color: #d6557e; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
.lp-feat__title { font-weight: 800; font-size: 16px; color: #4a2230; margin-bottom: 6px; }
.lp-feat__desc { font-size: 13.5px; color: #7a5c68; line-height: 1.55; }
.lp-demo { text-align: center; }
.lp-demo__frame { margin: 30px auto 0; max-width: 900px; }
.lp-demo__frame img { width: 100%; border-radius: 16px; border: 1px solid #f0c3d2; box-shadow: 0 18px 50px rgba(180,80,120,0.2); }
/* contact */
.lp-contact { display: flex; justify-content: center; }
.lp-contact__card { width: min(460px, 92vw); background: #fff; border: 1px solid #f3d3df; border-radius: 18px; padding: 30px; box-shadow: 0 12px 40px rgba(180,80,120,0.14); text-align: center; }
.lp-contact__card h2 { font-size: 24px; color: #4a2230; }
.lp-contact__card p { color: #7a5c68; font-size: 14px; margin: 8px 0 18px; }
.lp-form { display: flex; flex-direction: column; gap: 12px; text-align: left; }
.lp-field { height: 42px; border: 1px solid #ecd0da; border-radius: 10px; padding: 0 14px; font-size: 14px; font-family: inherit; outline: none; }
.lp-field:focus { border-color: #d4567f; }
.lp-err { background: #fdecef; border: 1px solid #f5c2cd; color: #c43254; border-radius: 8px; padding: 8px 11px; font-size: 12.5px; }
.lp-ok { background: #eafaf0; border: 1px solid #b6e6c9; color: #2f8a5d; border-radius: 8px; padding: 10px 12px; font-size: 13.5px; text-align: center; }
/* footer */
.lp-foot { display: flex; align-items: center; justify-content: space-between; padding: 22px 6vw; border-top: 1px solid #f3d3df; color: #a07c8a; font-size: 13px; }
.lp-foot__links a, .lp-foot__link { color: #b8456a; text-decoration: none; background: none; border: none; cursor: pointer; font-family: inherit; font-size: 13px; }
@media (max-width: 860px) {
  .lp-hero { grid-template-columns: 1fr; }
  .lp-hero__txt h1 { font-size: 32px; }
  .lp-feats { grid-template-columns: 1fr; }
  .lp-nav__links a { display: none; }
}
</style>
