<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Giáo viên</span>
      <div class="ws-head__actions">
        <SkSegmented v-model="tab" :options="TABS" />
      </div>
    </header>

    <div class="ws-body sk-scroll">
      <!-- DANH SÁCH -->
      <div v-if="tab === 'list'">
        <SkState v-if="loadingList" state="loading" />
        <SkState v-else-if="!teachers.length" state="empty" title="Chưa có giáo viên" message="Chưa có hồ sơ giáo viên." />
        <div v-else class="card">
          <table class="tbl">
            <thead><tr><th>Giáo viên</th><th>Email</th><th>Điện thoại</th><th>Tài khoản</th><th>Trạng thái</th></tr></thead>
            <tbody>
              <tr v-for="t in teachers" :key="t.name">
                <td class="tbl__name">{{ t.teacher_name || t.name }}</td>
                <td>{{ t.email || '—' }}</td>
                <td class="tnum">{{ t.phone || '—' }}</td>
                <td><SkBadge :variant="t.user ? 'success' : 'neutral'" :label="t.user ? 'Đã có' : 'Chưa có'" /></td>
                <td><SkBadge :variant="t.status === 'Active' ? 'success' : 'neutral'" :label="t.status || '—'" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- CHẤM CÔNG -->
      <div v-else-if="tab === 'timesheet'">
        <div class="filterbar">
          <select v-model.number="month" class="field" @change="loadTimesheet">
            <option v-for="m in 12" :key="m" :value="m">Tháng {{ m }}</option>
          </select>
          <select v-model.number="year" class="field" @change="loadTimesheet">
            <option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option>
          </select>
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
          <select v-model.number="salYear" class="field" @change="loadSalary">
            <option :value="0">Tất cả năm</option>
            <option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <SkState v-if="loadingSal" state="loading" />
        <SkState v-else-if="!salary.length" state="empty" title="Chưa có bảng lương" message="Chưa có bảng lương giáo viên." />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from '../api'
import { formatVND } from '../utils/format'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkBadge from '../components/ui/SkBadge.vue'
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
  try { teachers.value = (await call('get_teachers')) || [] } catch { teachers.value = [] } finally { loadingList.value = false }
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

onMounted(() => {
  loadList(); loadTimesheet(); loadSalary()
})
</script>

<style scoped>
.card { background: #fff; border: 1px solid #f2d4df; border-radius: 12px; overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.tbl th { text-align: left; padding: 10px 14px; background: #fdf3f7; color: #8a5c6c; font-weight: 600; border-bottom: 1px solid #f2d4df; }
.tbl td { padding: 10px 14px; border-bottom: 1px solid #f7e6ee; }
.tbl__name { font-weight: 600; color: #5a3a46; }
.filterbar { display: flex; gap: 10px; margin-bottom: 14px; }
.field { height: 34px; border: 1px solid #ecd0da; border-radius: 8px; padding: 0 12px; font-size: 13px; outline: none; font-family: inherit; background: #fff; }
.field:focus { border-color: #d4567f; }
</style>
