<template>
  <div class="md">
    <!-- CONTEXT -->
    <section class="ctx">
      <div class="ctx__head">
        <span class="ctx__title">Hóa đơn</span>
        <span class="ctx__overdue">{{ overdueCount }} quá hạn</span>
      </div>
      <div class="ctx__tools">
        <SkSegmented v-model="filter" :options="['Tất cả', 'Chưa thu', 'Quá hạn', 'Đã thu']" />
      </div>
      <div class="ctx__list sk-scroll">
        <SkState v-if="loading" state="loading" />
        <SkState v-else-if="!filtered.length" state="empty" title="Không có hóa đơn" message="Thử đổi bộ lọc." />
        <button v-for="i in filtered" :key="i.name" class="irow" :class="{ 'irow--active': i.name === selectedId }" @click="select(i.name)">
          <div class="irow__top">
            <span class="irow__id tnum">{{ i.name }}</span>
            <SkBadge v-bind="invMeta(i)" />
          </div>
          <div class="irow__bottom">
            <span class="irow__student">{{ i.student_name }}</span>
            <span class="irow__total tnum">{{ formatVND(i.total_amount) }}</span>
          </div>
        </button>
      </div>
    </section>

    <!-- DETAIL -->
    <main class="dtl">
      <SkState v-if="!selectedId && !loading" state="empty" title="Chọn một hóa đơn" message="Chọn hóa đơn ở danh sách bên trái để xem chi tiết." />

      <template v-else-if="selectedId">
        <header class="dtl__head">
          <div class="dtl__id">
            <span class="dtl__name tnum">{{ cur.name }}</span>
            <SkBadge v-bind="invMeta(cur)" />
          </div>
          <div class="dtl__actions">
            <SkButton variant="secondary">In hóa đơn</SkButton>
            <SkButton v-if="cur.outstanding_amount > 0" variant="solid" @click="openPay">Thu tiền</SkButton>
          </div>
        </header>

        <div class="dtl__body sk-scroll">
          <SkState v-if="detailLoading" state="loading" />
          <div v-else class="dtl__inner">
            <div class="who">
              <SkAvatar :name="cur.student_name" :size="46" />
              <div>
                <div class="who__name">{{ cur.student_name }}</div>
                <div class="who__sub">{{ cur.program_enrollment || '—' }}</div>
              </div>
            </div>

            <div class="grid3">
              <SkStatTile label="Tổng hóa đơn" :value="formatVND(cur.total_amount)" />
              <SkStatTile label="Đã thu" :value="formatVND(paid)" value-color="#2f8a5d" />
              <SkStatTile label="Còn nợ" :value="formatVND(cur.outstanding_amount)" :accent="cur.outstanding_amount > 0" :value-color="cur.outstanding_amount > 0 ? '#c43232' : '#3d2530'" />
            </div>

            <div class="info">
              <div class="info__c"><div class="info__l">Ngày lập</div><div class="info__v tnum">{{ formatDate(cur.posting_date) }}</div></div>
              <div class="info__c"><div class="info__l">Hạn thu</div><div class="info__v tnum">{{ formatDate(cur.due_date) }}</div></div>
            </div>

            <div v-if="cur.items && cur.items.length">
              <div class="block__title">Khoản mục</div>
              <div class="tblwrap">
                <table class="tbl">
                  <thead><tr><th>Nội dung</th><th style="text-align:right;">Số tiền</th></tr></thead>
                  <tbody>
                    <tr v-for="(it, i) in cur.items" :key="i"><td class="tbl__name">{{ it.item_name }}</td><td class="tbl__name tnum" style="text-align:right;">{{ formatVND(it.amount) }}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <div class="block__title">Lịch sử thanh toán</div>
              <div v-if="!cur.payments || !cur.payments.length" class="nopay">Chưa có phiếu thu nào cho hóa đơn này.</div>
              <div v-else class="timeline">
                <div v-for="(p, i) in cur.payments" :key="i" class="tl">
                  <div class="tl__rail"><span class="tl__dot" /><span class="tl__line" /></div>
                  <div class="tl__body">
                    <div class="tl__date tnum">{{ formatDate(p.date) }}</div>
                    <div class="tl__title">Thu {{ formatVND(p.amount) }}</div>
                    <div class="tl__detail">{{ methodLabel(p.method) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>

    <!-- THU TIỀN MODAL -->
    <SkModal v-model="payOpen" title="Thu học phí" width="440px">
      <div class="form">
        <div class="form__row"><div class="f-label">Hóa đơn</div><div class="f-static tnum">{{ cur.name }}</div></div>
        <div class="form__row"><div class="f-label">Còn nợ</div><div class="f-static" style="color:#c43232;font-weight:600;">{{ formatVND(cur.outstanding_amount) }}</div></div>
        <div class="form__row"><div class="f-label">Số tiền thu</div><input v-model="pay.amount" type="number" class="field" /></div>
        <div class="form__row"><div class="f-label">Hình thức</div>
          <select v-model="pay.method" class="field">
            <option value="Cash">Tiền mặt</option>
            <option value="Bank Transfer">Chuyển khoản</option>
            <option value="Card">Thẻ</option>
            <option value="Other">Khác</option>
          </select>
        </div>
        <div class="form__row"><div class="f-label">Ngày thu</div><input v-model="pay.date" type="date" class="field" /></div>
      </div>
      <template #footer>
        <SkButton variant="secondary" @click="payOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="paying" @click="submitPay">Xác nhận thu</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '../api'
import { formatVND, formatDate, isOverdue } from '../utils/format'
import { statusMeta } from '../utils/labels'
import { toast } from '../utils/toast'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkButton from '../components/ui/SkButton.vue'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkStatTile from '../components/ui/SkStatTile.vue'
import SkState from '../components/ui/SkState.vue'
import SkModal from '../components/ui/SkModal.vue'

const loading = ref(true)
const invoices = ref([])
const filter = ref('Tất cả')
const selectedId = ref(null)
const detailLoading = ref(false)
const cur = reactive({})

const payOpen = ref(false)
const paying = ref(false)
const pay = reactive({ amount: 0, method: 'Cash', date: new Date().toISOString().slice(0, 10) })

const METHODS = { Cash: 'Tiền mặt', 'Bank Transfer': 'Chuyển khoản', Card: 'Thẻ', Other: 'Khác' }
const methodLabel = (m) => METHODS[m] || m || '—'
const paid = computed(() => (Number(cur.total_amount) || 0) - (Number(cur.outstanding_amount) || 0))

function invMeta(i) {
  if (isOverdue(i.due_date, i.outstanding_amount)) return statusMeta('Fee Invoice', 'status', 'Overdue')
  return statusMeta('Fee Invoice', 'status', i.status)
}

const overdueCount = computed(() => invoices.value.filter((i) => isOverdue(i.due_date, i.outstanding_amount)).length)

const filtered = computed(() => {
  if (filter.value === 'Chưa thu') return invoices.value.filter((i) => i.outstanding_amount > 0 && !isOverdue(i.due_date, i.outstanding_amount))
  if (filter.value === 'Quá hạn') return invoices.value.filter((i) => isOverdue(i.due_date, i.outstanding_amount))
  if (filter.value === 'Đã thu') return invoices.value.filter((i) => i.outstanding_amount <= 0)
  return invoices.value
})

function openPay() {
  pay.amount = Number(cur.outstanding_amount) || 0
  pay.method = 'Cash'
  pay.date = new Date().toISOString().slice(0, 10)
  payOpen.value = true
}

async function submitPay() {
  if (!(Number(pay.amount) > 0)) { toast.error('Số tiền không hợp lệ'); return }
  paying.value = true
  try {
    await call('create_payment', {
      student: cur.student,
      payment_date: pay.date,
      payment_method: pay.method,
      amount: pay.amount,
      invoice: cur.name,
    })
    toast.success('Đã ghi nhận phiếu thu', `${formatVND(pay.amount)} cho ${cur.name}`)
    payOpen.value = false
    await loadDetail(cur.name)
    await load(false)
  } catch (e) {
    toast.error('Thu tiền thất bại', e?.message || String(e))
  } finally {
    paying.value = false
  }
}

async function loadDetail(id) {
  detailLoading.value = true
  try {
    Object.assign(cur, {}, (await call('get_invoice_detail', { invoice: id })) || {})
  } finally {
    detailLoading.value = false
  }
}

function select(id) {
  selectedId.value = id
  loadDetail(id)
}

async function load(reselect = true) {
  loading.value = true
  try {
    invoices.value = (await call('get_invoices')) || []
    if (reselect && invoices.value.length) select(invoices.value[0].name)
  } finally {
    loading.value = false
  }
}
onMounted(() => load(true))
</script>

<style scoped>
.md { flex: 1; min-width: 0; display: flex; height: 100vh; }
.ctx { flex: none; width: 326px; display: flex; flex-direction: column; background: rgba(255, 252, 253, 0.82); border-right: 1px solid #f2d4df; }
.ctx__head { height: 56px; flex: none; display: flex; align-items: center; justify-content: space-between; padding: 0 18px; border-bottom: 1px solid #f4dde5; }
.ctx__title { font-size: 16px; font-weight: 600; color: #4a2230; }
.ctx__overdue { font-size: 11.5px; color: #c44a3f; font-weight: 600; }
.ctx__tools { padding: 12px 14px 10px; }
.ctx__list { flex: 1; overflow-y: auto; padding-bottom: 12px; }

.irow { display: block; width: 100%; text-align: left; border: none; border-bottom: 1px solid #f7e6ec; background: transparent; padding: 11px 16px 11px 13px; cursor: pointer; border-left: 3px solid transparent; font-family: inherit; }
.irow:hover { background: #fdf2f6; }
.irow--active { background: #fbd9e5; border-left-color: #d6557e; }
.irow__top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.irow__id { font-size: 13px; font-weight: 600; color: #3d2530; }
.irow__bottom { display: flex; justify-content: space-between; gap: 8px; margin-top: 5px; }
.irow__student { font-size: 11.5px; color: #a98c98; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.irow__total { font-size: 12px; font-weight: 600; color: #3d2530; flex: none; }

.dtl { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; }
.dtl__head { height: 56px; flex: none; display: flex; align-items: center; gap: 11px; padding: 0 18px; border-bottom: 1px solid #f1dbe3; }
.dtl__id { min-width: 0; display: flex; align-items: center; gap: 9px; }
.dtl__name { font-size: 16px; font-weight: 600; color: #3d2530; }
.dtl__actions { margin-left: auto; display: flex; gap: 8px; }
.dtl__body { flex: 1; overflow-y: auto; }
.dtl__inner { padding: 26px 30px 44px; max-width: 900px; display: flex; flex-direction: column; gap: 28px; }

.who { display: flex; align-items: center; gap: 13px; }
.who__name { font-size: 15px; font-weight: 600; color: #3d2530; }
.who__sub { font-size: 12.5px; color: #a98c98; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.info { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px 32px; }
.info__l { font-size: 11.5px; color: #a98c98; margin-bottom: 3px; }
.info__v { font-size: 14px; color: #3d2530; font-weight: 500; }
.block__title { font-size: 15px; font-weight: 600; color: #4a2230; margin-bottom: 14px; }

.tblwrap { border: 1px solid #f3d9e1; border-radius: 11px; overflow: hidden; background: #fff; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl thead tr { background: #fdf2f6; }
.tbl th { text-align: left; font-size: 11.5px; font-weight: 600; color: #a07c8a; padding: 10px 16px; }
.tbl td { padding: 11px 16px; border-top: 1px solid #f6e3ea; }
.tbl__name { font-size: 13.5px; font-weight: 500; color: #3d2530; }

.nopay { font-size: 13px; color: #a98c98; border: 1px dashed #ecd0da; border-radius: 10px; padding: 18px; text-align: center; }
.timeline { display: flex; flex-direction: column; }
.tl { display: flex; gap: 14px; }
.tl__rail { flex: none; display: flex; flex-direction: column; align-items: center; }
.tl__dot { width: 11px; height: 11px; border-radius: 50%; margin-top: 4px; background: #3f9b6e; }
.tl__line { flex: 1; width: 2px; background: #f4dde5; }
.tl__body { padding-bottom: 18px; }
.tl__date { font-size: 11.5px; color: #bd97a5; }
.tl__title { font-size: 13.5px; font-weight: 500; color: #3d2530; margin-top: 2px; }
.tl__detail { font-size: 12.5px; color: #a98c98; }

.form { display: flex; flex-direction: column; gap: 14px; }
.form__row { display: flex; flex-direction: column; gap: 6px; }
.f-label { font-size: 12px; color: #7a5c68; font-weight: 500; }
.f-static { font-size: 14px; color: #3d2530; }
select.field { appearance: none; }
</style>
