<template>
  <div class="login">
    <router-link to="/" class="login__home">← Về trang chủ</router-link>
    <div class="login__card">
      <div class="login__brand">
        <div class="login__logo">
          <svg width="30" height="30" viewBox="0 0 64 64">
            <g fill="#fff">
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(0 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(72 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(144 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(216 32 32)" />
              <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(288 32 32)" />
            </g>
            <circle cx="32" cy="32" r="4.4" fill="#ffd98e" />
          </svg>
        </div>
        <div class="login__title font-display">IKE Ohashi</div>
        <div class="login__sub">日本語 · Education ERP</div>
      </div>

      <form class="login__form" @submit.prevent="submit">
        <label class="login__fg">
          <span>Email / Tài khoản</span>
          <input v-model.trim="usr" class="login__field" type="text" autocomplete="username" autofocus :disabled="loading" />
        </label>
        <label class="login__fg">
          <span>Mật khẩu</span>
          <input v-model="pwd" class="login__field" type="password" autocomplete="current-password" :disabled="loading" />
        </label>

        <div v-if="error" class="login__error">{{ error }}</div>

        <button class="login__btn" type="submit" :disabled="loading">
          {{ loading ? 'Đang đăng nhập…' : 'Đăng nhập' }}
        </button>
        <a class="login__forgot" href="/update-password">Quên mật khẩu?</a>
      </form>
    </div>
    <div class="login__foot">© IKE Ohashi · Education ERP</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const usr = ref('')
const pwd = ref('')
const loading = ref(false)
const error = ref('')

function redirectTarget() {
  const p = new URLSearchParams(window.location.search).get('redirect-to')
  return p && p.startsWith('/') ? p : '/'
}

async function submit() {
  if (!usr.value || !pwd.value) { error.value = 'Nhập tài khoản và mật khẩu.'; return }
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/method/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Frappe-CSRF-Token': window.csrf_token || '',
      },
      body: new URLSearchParams({ usr: usr.value, pwd: pwd.value }),
      credentials: 'include',
    })
    if (res.ok) {
      // Tải lại để phiên/csrf/boot làm mới rồi App.vue whoami điều hướng.
      window.location.href = redirectTarget()
      return
    }
    if (res.status === 401) error.value = 'Sai tài khoản hoặc mật khẩu.'
    else error.value = `Đăng nhập thất bại (${res.status}).`
  } catch (e) {
    error.value = 'Không kết nối được máy chủ.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login { min-height: 100vh; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; background: linear-gradient(140deg, #fff7fa 0%, #fdedf3 48%, #fbe4ee 100%); }
.login__card { width: min(380px, 92vw); background: #fff; border: 1px solid #f2d4df; border-radius: 18px; padding: 30px 28px 26px; box-shadow: 0 12px 40px rgba(180, 80, 120, 0.16); }
.login__brand { text-align: center; margin-bottom: 22px; }
.login__logo { width: 52px; height: 52px; border-radius: 14px; margin: 0 auto 12px; background: linear-gradient(140deg, #f7a8c4, #d6557e); display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(214, 85, 126, 0.34); }
.login__title { font-size: 22px; font-weight: 900; color: #4a2230; letter-spacing: 0.4px; }
.login__sub { font-size: 11.5px; color: #b07e90; margin-top: 3px; }
.login__form { display: flex; flex-direction: column; gap: 14px; }
.login__fg { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: #7a5c68; font-weight: 500; }
.login__field { height: 40px; border: 1px solid #ecd0da; border-radius: 9px; padding: 0 13px; font-size: 14px; outline: none; font-family: inherit; }
.login__field:focus { border-color: #d4567f; }
.login__error { background: #fdecef; border: 1px solid #f5c2cd; color: #c43254; border-radius: 8px; padding: 8px 11px; font-size: 12.5px; }
.login__btn { height: 42px; margin-top: 4px; border: none; border-radius: 10px; background: linear-gradient(135deg, #ef82a6, #d6557e); color: #fff; font-size: 14.5px; font-weight: 700; cursor: pointer; font-family: inherit; box-shadow: 0 6px 16px rgba(214, 85, 126, 0.3); }
.login__btn:disabled { opacity: 0.7; cursor: default; }
.login__forgot { text-align: center; font-size: 12px; color: #b07e90; text-decoration: none; margin-top: 2px; }
.login__forgot:hover { color: #d6557e; text-decoration: underline; }
.login__foot { font-size: 11.5px; color: #c79bab; }
.login__home { position: fixed; top: 18px; left: 20px; font-size: 13px; color: #b07e90; text-decoration: none; font-weight: 600; }
.login__home:hover { color: #d6557e; }
</style>
