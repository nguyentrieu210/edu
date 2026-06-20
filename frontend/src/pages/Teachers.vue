<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Giáo viên</span>
      <div class="ws-head__actions">
        <SkSegmented v-model="tab" :options="TABS" />
        <SkButton v-if="tab === 'list'" variant="solid" left-icon="plus" @click="openCreate">Thêm giáo viên</SkButton>
        <SkButton v-if="tab === 'salary'" variant="solid" left-icon="plus" @click="openCalc">Tính lương</SkButton>
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <!-- DANH SÁCH -->
      <div v-if="tab === 'list'">
        <SkState v-if="loadingList" state="loading" />
        <SkState v-else-if="!teachers.length" state="empty" title="Chưa có giáo viên" message="Thêm giáo viên đầu tiên." action-label="Thêm giáo viên" @action="openCreate" />
        <div v-else class="card">
          <table class="tbl">
            <thead><tr><th>Giáo viên</th><th>Chuyên môn</th><th style="text-align:right;">Đơn giá/buổi</th><th style="text-align:right;">Lớp</th><th>Email</th><th>Tài khoản</th><th>Trạng thái</th><th></th></tr></thead>
            <tbody>
              <tr v-for="t in teachers" :key="t.name">
                <td class="tbl__name">{{ t.teacher_name || t.name }}<div class="tbl__sub tnum">{{ t.phone || '' }}</div></td>
                <td>{{ t.specialization || '—' }}</td>
                <td class="tnum" style="text-align:right;">{{ t.rate_per_session ? formatVND(t.rate_per_session) : '—' }}</td>
                <td class="tnum" style="text-align:right;">{{ classCount[t.name] || 0 }}</td>
                <td>{{ t.email || '—' }}</td>
                <td><SkBadge :variant="t.user ? 'success' : 'neutral'" :label="t.user ? 'Đã có' : 'Chưa có'" /></td>
                <td><SkBadge :variant="t.status === 'Active' ? 'success' : 'neutral'" :label="t.status || '—'" /></td>
                <td style="text-align:right;"><SkButton variant="ghost" size="sm" left-icon="edit-2" @click="openEdit(t)">Sửa</SkButton></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- CHẤM CÔNG -->
      <div v-else-if="tab === 'timesheet'">
        <div class="filterbar">
          <select v-model.number="month" class="field" @change="loadTimesheet"><option v-for="m in 12" :key="m" :value="m">Tháng {{ m }}</option></select>
          <select v-model.number="year" class="field" @change="loadTimesheet"><option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option></select>
        </div>
        <SkState v-if="loadingTs" state="loading" />
        <SkState v-else-if="!timesheet.length" state="empty" title="Chưa có buổi dạy" message="Không có buổi dạy trong tháng này." />
        <div v-else class="card">
          <table class="tbl">
            <thead><tr><th>Giáo viên</th><th style="text-align:right;">Tổng buổi</th><th style="text-align:right;">Đã dạy</th><th style="text-align:right;">Có mặt</th><th style="text-align:right;">Vắng</th></tr></thead>
            <tbody>
              <tr v-for="r in timesheet" :key="r.teacher">
                <td class="tbl__name">{{ r.teacher_name }}</td>
                <td class="tnum" style="text-align:right;">{{ r.total }}</td>
                <td class="tnum" style="text-align:right;">{{ r.taught }}</td>
                <td class="tnum" style="text-align:right; color:#2f8a5d;">{{ r.present }}</td>
                <td class="tnum" style="text-align:right; color:#c44a3f;">{{ r.absent }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- LƯƠNG -->
      <div v-else>
        <div class="filterbar">
          <select v-model.number="salYear" class="field" @change="loadSalary"><option :value="0">Tất cả năm</option><option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option></select>
        </div>
        <SkState v-if="loadingSal" state="loading" />
        <SkState v-else-if="!salary.length" state="empty" title="Chưa có bảng lương" message="Bấm 'Tính lương' để tạo bảng lương." action-label="Tính lương" @action="openCalc" />
        <div v-else class="card">
          <table class="tbl">
            <thead><tr><th>Giáo viên</th><th>Kỳ</th><th style="text-align:right;">Số buổi</th><th style="text-align:right;">Đơn giá</th><th style="text-align:right;">Tổng lương</th><th>Trạng thái</th></tr></thead>
            <tbody>
              <tr v-for="s in salary" :key="s.name">
                <td class="tbl__name">{{ s.teacher_name }}</td>
                <td class="tnum">{{ s.month }}/{{ s.year }}</td>
                <td class="tnum" style="text-align:right;">{{ s.total_sessions_taught }}</td>
                <td class="tnum" style="text-align:right;">{{ formatVND(s.rate_per_session) }}</td>
                <td class="tnum" style="text-align:right; font-weight:700;">{{ formatVND(s.total_salary) }}</td>
                <td><SkBadge :variant="s.status === 'Paid' ? 'success' : 'warning'" :label="s.status || '—'" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal thêm/sửa giáo viên -->
    <SkModal v-model="showForm" :title="formMode === 'create' ? 'Thêm giáo viên' : 'Sửa giáo viên'">
      <form class="form-grid" @submit.prevent="saveTeacher">
        <label class="fg fg--full"><span>Tên giáo viên *</span><input v-model.trim="form.teacher_name" class="field" required /></label>
        <label class="fg"><span>Email</span><input v-model.trim="form.email" class="field" type="email" /></label>
        <label class="fg"><span>Số điện thoại</span><input v-model.trim="form.phone" class="field" /></label>
        <label class="fg"><span>Chuyên môn / cấp độ</span><input v-model.trim="form.specialization" class="field" placeholder="vd: N2, IELTS" /></label>
        <label class="fg"><span>Đơn giá / buổi</span><input v-model.number="form.rate_per_session" class="field" type="number" min="0" step="1000" /></label>
        <label class="fg"><span>Trạng thái</span><select v-model="form.status" class="field"><option value="Active">Active</option><option value="Inactive">Inactive</option></select></label>
        <p v-if="formMode === 'create'" class="hint fg--full">Có email → hệ thống tự tạo tài khoản + gửi mail đặt mật khẩu.</p>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="saving" @click="showForm = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="saving" @click="saveTeacher">{{ formMode === 'create' ? 'Tạo' : 'Lưu' }}</SkButton>
      </template>
    </SkModal>

    <!-- Modal tính lương -->
    <SkModal v-model="showCalc" title="Tính lương giáo viên">
      <form class="form-grid" @submit.prevent="runCalc">
        <label class="fg fg--full"><span>Giáo viên *</span>
          <select v-model="calc.teacher" class="field" @change="onCalcTeacher">
            <option value="" disabled>Chọn giáo viên</option>
            <option v-for="t in teachers" :key="t.name" :value="t.name">{{ t.teacher_name || t.name }}</option>
          </select>
        </label>
        <label class="fg"><span>Tháng</span><select v-model.number="calc.month" class="field"><option v-for="m in 12" :key="m" :value="m">Tháng {{ m }}</option></select></label>
        <label class="fg"><span>Năm</span><select v-model.number="calc.year" class="field"><option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option></select></label>
        <label class="fg fg--full"><span>Đơn giá / buổi *</span><input v-model.number="calc.rate" class="field" type="number" min="0" step="1000" /></label>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="calcing" @click="showCalc = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="calcing" @click="runCalc">Tính lương</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call, db } from '../api'
import { formatVND } from '../utils/format'
import { toast } from '../utils/toast'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkModal from '../components/ui/SkModal.vue'
import SkState from '../components/ui/SkState.vue'

const TABS = [
  { label: 'Danh sách', value: 'list' },
  { label: 'Chấm công', value: 'timesheet' },
  { label: 'Lương', value: 'salary' },
]
const now = new Date()
const YEARS = [now.getFullYear() - 1, now.getFullYear(), now.getFullYear() + 1]

const tab = ref('list')
const teachers = ref([])
const classCount = ref({})
const loadingList = ref(true)
const timesheet = ref([])
const loadingTs = ref(false)
const month = ref(now.getMonth() + 1)
const year = ref(now.getFullYear())
const salary = ref([])
const loadingSal = ref(false)
const salYear = ref(now.getFullYear())

async function loadList() {
  loadingList.value = true
  try {
    teachers.value = (await call('get_teachers')) || []
    const cls = (await call('get_classes')) || []
    const cc = {}
    for (const c of cls) if (c.teacher) cc[c.teacher] = (cc[c.teacher] || 0) + 1
    classCount.value = cc
  } catch { teachers.value = [] } finally { loadingList.value = false }
}
async function loadTimesheet() {
  loadingTs.value = true
  try { timesheet.value = ((await call('get_teacher_timesheet', { month: month.value, year: year.value })) || {}).rows || [] }
  catch { timesheet.value = [] } finally { loadingTs.value = false }
}
async function loadSalary() {
  loadingSal.value = true
  try { salary.value = (await call('get_salary_slips', { year: salYear.value || undefined })) || [] }
  catch { salary.value = [] } finally { loadingSal.value = false }
}

/* ---- Thêm/sửa giáo viên ---- */
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = ref({})
function blankForm() { return { teacher_name: '', email: '', phone: '', specialization: '', rate_per_session: null, status: 'Active' } }
function openCreate() { form.value = blankForm(); formMode.value = 'create'; showForm.value = true }
function openEdit(t) { form.value = { name: t.name, teacher_name: t.teacher_name, email: t.email, phone: t.phone, specialization: t.specialization, rate_per_session: t.rate_per_session, status: t.status }; formMode.value = 'edit'; showForm.value = true }
async function saveTeacher() {
  if (!form.value.teacher_name) { toast.error('Cần tên giáo viên'); return }
  saving.value = true
  try {
    const payload = {
      teacher_name: form.value.teacher_name, email: form.value.email || null, phone: form.value.phone || null,
      specialization: form.value.specialization || null, rate_per_session: form.value.rate_per_session || null,
      status: form.value.status || 'Active',
    }
    if (formMode.value === 'create') {
      await db.insert({ doctype: 'Teacher', ...payload })
      toast.success('Đã thêm giáo viên', form.value.email ? 'Đã gửi mail tạo tài khoản.' : '')
    } else {
      await db.setValue('Teacher', form.value.name, payload)
      toast.success('Đã lưu giáo viên')
    }
    showForm.value = false
    await loadList()
  } catch (e) {
    toast.error('Không lưu được', e?.messages?.[0] || e?.message || String(e))
  } finally { saving.value = false }
}

/* ---- Tính lương ---- */
const showCalc = ref(false)
const calcing = ref(false)
const calc = ref({ teacher: '', month: now.getMonth() + 1, year: now.getFullYear(), rate: null })
function openCalc() { calc.value = { teacher: '', month: now.getMonth() + 1, year: now.getFullYear(), rate: null }; showCalc.value = true }
function onCalcTeacher() {
  const t = teachers.value.find((x) => x.name === calc.value.teacher)
  if (t && t.rate_per_session) calc.value.rate = t.rate_per_session
}
async function runCalc() {
  if (!calc.value.teacher || !calc.value.rate) { toast.error('Cần chọn giáo viên và đơn giá'); return }
  calcing.value = true
  try {
    await call('calculate_teacher_salary', { teacher: calc.value.teacher, month: calc.value.month, year: calc.value.year, rate_per_session: calc.value.rate })
    toast.success('Đã tính lương')
    showCalc.value = false
    tab.value = 'salary'
    await loadSalary()
  } catch (e) {
    toast.error('Không tính được lương', e?.messages?.[0] || e?.message || String(e))
  } finally { calcing.value = false }
}

onMounted(() => { loadList(); loadTimesheet(); loadSalary() })
</script>

<style scoped>
.card { background: #fff; border: 1px solid #f2d4df; border-radius: 12px; overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.tbl th { text-align: left; padding: 10px 14px; background: #fdf3f7; color: #8a5c6c; font-weight: 600; border-bottom: 1px solid #f2d4df; }
.tbl td { padding: 10px 14px; border-bottom: 1px solid #f7e6ee; }
.tbl__name { font-weight: 600; color: #5a3a46; }
.tbl__sub { font-weight: 400; color: #a07c8a; font-size: 11.5px; margin-top: 2px; }
.filterbar { display: flex; gap: 10px; margin-bottom: 14px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: #7a5c68; }
.fg--full { grid-column: 1 / -1; }
.hint { font-size: 12px; color: #a98c98; }
.field { height: 36px; border: 1px solid #ecd0da; border-radius: 8px; padding: 0 12px; font-size: 13px; outline: none; font-family: inherit; background: #fff; }
.field:focus { border-color: #d4567f; }
</style>
