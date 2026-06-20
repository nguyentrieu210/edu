<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Quản lý tài khoản đăng nhập</span>
      <div class="ws-head__actions">
        <input v-model="q" class="search" type="search" placeholder="Tìm email / tên…" @keyup.enter="load" />
        <SkButton variant="secondary" left-icon="search" @click="load">Tìm</SkButton>
        <SkButton variant="solid" left-icon="plus" @click="openCreate">Tạo tài khoản</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <SkState v-if="loading" state="loading" />
      <SkState v-else-if="error" state="error" title="Không tải được" :message="error" action-label="Thử lại" @action="load" />
      <SkState v-else-if="!users.length" state="empty" title="Chưa có tài khoản" message="Tạo tài khoản đầu tiên." action-label="Tạo tài khoản" @action="openCreate" />

      <div v-else class="card">
        <table class="tbl">
          <thead>
            <tr><th>Email</th><th>Họ tên</th><th>Vai trò</th><th>Liên kết</th><th>Trạng thái</th><th style="text-align:right;">Thao tác</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.name">
              <td class="tbl__name">{{ u.email || u.name }}</td>
              <td>{{ u.full_name || '—' }}</td>
              <td>
                <select class="role-sel" :value="primaryRole(u)" :disabled="busy === u.name" @change="changeRole(u, $event)">
                  <option v-for="r in ROLES" :key="r" :value="r">{{ roleLabel(r) }}</option>
                </select>
              </td>
              <td class="tbl__sub">{{ u.student ? ('HV ' + u.student) : (u.teacher ? ('GV ' + u.teacher) : '—') }}</td>
              <td>
                <SkBadge :variant="u.enabled ? 'success' : 'neutral'" :label="u.enabled ? 'Đang bật' : 'Đã tắt'" />
              </td>
              <td style="text-align:right; white-space:nowrap;">
                <SkButton variant="ghost" size="sm" left-icon="mail" :loading="busy === u.name + ':mail'" @click="resetMail(u)">Gửi lại mail</SkButton>
                <SkButton variant="ghost" size="sm" :left-icon="u.enabled ? 'user-x' : 'user-check'" :loading="busy === u.name + ':en'" @click="toggleEnabled(u)">{{ u.enabled ? 'Tắt' : 'Bật' }}</SkButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <SkModal v-model="showCreate" title="Tạo tài khoản">
      <form class="form-grid" @submit.prevent="create">
        <label class="fg fg--full"><span>Email *</span><input v-model.trim="form.email" class="field" type="email" required /></label>
        <label class="fg fg--full"><span>Họ tên</span><input v-model.trim="form.full_name" class="field" /></label>
        <label class="fg"><span>Vai trò</span>
          <select v-model="form.role" class="field">
            <option v-for="r in ROLES" :key="r" :value="r">{{ roleLabel(r) }}</option>
          </select>
        </label>
        <label class="fg fg--check"><input v-model="form.send_welcome" type="checkbox" /> <span>Gửi mail đặt mật khẩu</span></label>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="saving" @click="showCreate = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="saving" @click="create">Tạo</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from '../api'
import { toast } from '../utils/toast'
import SkButton from '../components/ui/SkButton.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkState from '../components/ui/SkState.vue'
import SkModal from '../components/ui/SkModal.vue'

const ROLES = ['Student', 'Teacher', 'Academic Manager']
const ROLE_LABELS = { Student: 'Học viên', Teacher: 'Giáo viên', 'Academic Manager': 'Giáo vụ / Admin' }
const roleLabel = (r) => ROLE_LABELS[r] || r

const loading = ref(true)
const error = ref('')
const users = ref([])
const q = ref('')
const busy = ref('')
const showCreate = ref(false)
const saving = ref(false)
const form = ref({ email: '', full_name: '', role: 'Student', send_welcome: true })

function primaryRole(u) {
  return ROLES.find((r) => (u.roles || []).includes(r)) || 'Student'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    users.value = (await call('list_users', { search: q.value || undefined })) || []
  } catch (e) {
    error.value = e?.messages?.[0] || e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value = { email: '', full_name: '', role: 'Student', send_welcome: true }
  showCreate.value = true
}

async function create() {
  if (!form.value.email) { toast.error('Cần email'); return }
  saving.value = true
  try {
    await call('create_user', {
      email: form.value.email, full_name: form.value.full_name,
      role: form.value.role, send_welcome: form.value.send_welcome ? 1 : 0,
    })
    toast.success('Đã tạo tài khoản', form.value.send_welcome ? 'Đã gửi mail đặt mật khẩu.' : '')
    showCreate.value = false
    await load()
  } catch (e) {
    toast.error('Không tạo được', e?.messages?.[0] || e?.message || String(e))
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(u) {
  busy.value = u.name + ':en'
  try {
    await call('set_user_enabled', { user: u.name, enabled: u.enabled ? 0 : 1 })
    u.enabled = u.enabled ? 0 : 1
  } catch (e) {
    toast.error('Không đổi được trạng thái', e?.messages?.[0] || e?.message || String(e))
  } finally { busy.value = '' }
}

async function changeRole(u, ev) {
  const role = ev.target.value
  busy.value = u.name
  try {
    await call('set_user_role', { user: u.name, role })
    toast.success('Đã đổi vai trò')
    await load()
  } catch (e) {
    toast.error('Không đổi được vai trò', e?.messages?.[0] || e?.message || String(e))
  } finally { busy.value = '' }
}

async function resetMail(u) {
  busy.value = u.name + ':mail'
  try {
    await call('reset_user_password', { user: u.name })
    toast.success('Đã gửi mail đặt lại mật khẩu')
  } catch (e) {
    toast.error('Không gửi được mail', e?.messages?.[0] || e?.message || String(e))
  } finally { busy.value = '' }
}

onMounted(load)
</script>

<style scoped>
.search { height: 34px; border: 1px solid #ecd0da; border-radius: 8px; padding: 0 12px; font-size: 13px; outline: none; min-width: 220px; }
.search:focus { border-color: #d4567f; }
.card { background: #fff; border: 1px solid #f2d4df; border-radius: 12px; overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.tbl th { text-align: left; padding: 10px 14px; background: #fdf3f7; color: #8a5c6c; font-weight: 600; border-bottom: 1px solid #f2d4df; }
.tbl td { padding: 10px 14px; border-bottom: 1px solid #f7e6ee; }
.tbl__name { font-weight: 600; color: #5a3a46; }
.tbl__sub { color: #a07c8a; font-size: 12px; }
.role-sel { height: 30px; border: 1px solid #ecd0da; border-radius: 7px; background: #fff; padding: 0 8px; font-size: 12.5px; color: #7a5c68; font-family: inherit; cursor: pointer; outline: none; }
.role-sel:focus { border-color: #d4567f; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: #7a5c68; }
.fg--full { grid-column: 1 / -1; }
.fg--check { flex-direction: row; align-items: center; gap: 8px; grid-column: 1 / -1; }
.field { height: 36px; border: 1px solid #ecd0da; border-radius: 8px; padding: 0 12px; font-size: 13px; outline: none; font-family: inherit; }
.field:focus { border-color: #d4567f; }
</style>
