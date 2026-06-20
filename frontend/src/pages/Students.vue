<template>
  <div class="md">
    <section class="ctx">
      <div class="ctx__head">
        <div>
          <span class="ctx__title">Học viên</span>
          <span class="ctx__count">{{ filtered.length }}</span>
        </div>
        <div class="ctx__head-act">
          <ExcelTools
            label="học viên"
            export-method="export_students"
            template-method="download_student_template"
            import-method="import_students"
            @imported="load"
          />
          <SkButton size="sm" variant="solid" left-icon="plus" @click="openCreateStudent">Thêm</SkButton>
        </div>
      </div>

      <div class="ctx__tools">
        <div class="field field--icon">
          <FeatherIcon name="search" style="width:15px;height:15px;color:#bd8d9c;" />
          <input v-model="q" placeholder="Tìm theo tên, mã, SĐT..." />
        </div>
        <SkSegmented v-model="filter" :options="FILTERS" />
        <label class="period-wrap" title="Lọc theo ngày nhập học (ngày tạo hồ sơ)">
          <span class="period-cap">Nhập học</span>
          <select v-model="period" class="period-sel">
            <option v-for="p in PERIODS" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </label>
      </div>

      <div class="ctx__list sk-scroll">
        <SkState v-if="loading" state="loading" />
        <SkState
          v-else-if="error"
          state="error"
          title="Không tải được học viên"
          :message="error"
          action-label="Thử lại"
          @action="load"
        />
        <SkState
          v-else-if="!filtered.length"
          state="empty"
          title="Không có học viên"
          message="Thử đổi bộ lọc hoặc thêm học viên mới."
          action-label="Thêm học viên"
          @action="openCreateStudent"
        />
        <button
          v-for="s in filtered"
          :key="s.name"
          class="srow"
          :class="{ 'srow--active': s.name === selectedId }"
          @click="select(s.name)"
        >
          <SkAvatar :name="s.full_name" :src="s.student_image" :size="38"
            editable upload-doctype="Student" :upload-name="s.name" upload-field="student_image"
            @update:src="s.student_image = $event" @click.stop />
          <div class="srow__main">
            <div class="srow__top">
              <span class="srow__name">{{ s.full_name }}</span>
              <SkBadge v-bind="healthMeta(s.health_status)" />
            </div>
            <div class="srow__bottom">
              <span class="srow__sub">{{ s.phone || s.name }}</span>
              <span class="srow__note">{{ s.progress || '—' }}</span>
            </div>
          </div>
        </button>
      </div>
    </section>

    <main class="dtl">
      <SkState
        v-if="!selectedId && !loading"
        state="empty"
        title="Chọn một học viên"
        message="Chọn học viên ở danh sách bên trái để xem chi tiết."
      />

      <template v-else-if="selectedId">
        <header class="dtl__head">
          <SkAvatar :name="profileName" :src="prof.profile.student_image" :size="36"
            editable upload-doctype="Student" :upload-name="prof.profile.name" upload-field="student_image"
            @update:src="prof.profile.student_image = $event" />
          <div class="dtl__id">
            <span class="dtl__name">{{ profileName }}</span>
            <span class="dtl__slash">/</span>
            <span class="dtl__code tnum">{{ selectedId }}</span>
            <SkBadge v-bind="statusMeta('Student', 'student_status', prof.profile.student_status)" />
          </div>
          <div class="dtl__actions">
            <SkButton variant="secondary" left-icon="external-link" @click="openDesk">Mở hồ sơ</SkButton>
            <SkButton variant="solid" left-icon="edit-2" @click="openEditStudent">Sửa hồ sơ</SkButton>
          </div>
        </header>

        <div class="dtl__tabs">
          <button
            v-for="t in TABS"
            :key="t.id"
            class="tab"
            :class="{ 'tab--active': tab === t.id }"
            @click="tab = t.id"
          >
            {{ t.label }}
          </button>
        </div>

        <div class="dtl__body sk-scroll">
          <SkState v-if="detailLoading" state="loading" />
          <div v-else class="dtl__inner">
            <div v-if="tab === 'overview'" class="ovw">
              <div class="grid4">
                <SkStatTile label="Chuyên cần" :value="pct(prof.profile.attendance_rate)" />
                <SkStatTile label="Điểm trung bình" :value="score(prof.profile.average_score)" note="Điểm chuẩn hóa" note-color="#3f9b6e" />
                <SkStatTile label="Buổi đã học" :value="sessionsDone" :note="`Tổng ${sessionsTotal} buổi`" />
                <SkStatTile label="Tiến độ khóa" :value="progressPct" accent value-color="#b8456a" :progress="progressPct" />
              </div>

              <div class="block">
                <div class="block__head">
                  <div class="block__title">Thông tin cá nhân</div>
                  <SkButton size="sm" variant="ghost" left-icon="edit-2" @click="openEditStudent">Chỉnh sửa</SkButton>
                </div>
                <div class="info">
                  <div class="info__c"><div class="info__l">Họ và tên</div><div class="info__v">{{ profileName }}</div></div>
                  <div class="info__c"><div class="info__l">Mã học viên</div><div class="info__v tnum">{{ selectedId }}</div></div>
                  <div class="info__c"><div class="info__l">Ngày sinh</div><div class="info__v">{{ formatDate(prof.profile.date_of_birth) }}</div></div>
                  <div class="info__c"><div class="info__l">Điện thoại</div><div class="info__v"><InlineCell doctype="Student" :name="prof.profile.name" field="phone" v-model="prof.profile.phone" @saved="reloadStudents" /></div></div>
                  <div class="info__c"><div class="info__l">Email</div><div class="info__v"><InlineCell doctype="Student" :name="prof.profile.name" field="email" v-model="prof.profile.email" /></div></div>
                  <div class="info__c"><div class="info__l">Nghề nghiệp</div><div class="info__v"><InlineCell doctype="Student" :name="prof.profile.name" field="occupation" v-model="prof.profile.occupation" /></div></div>
                  <div class="info__c"><div class="info__l">Nguồn</div><div class="info__v">{{ prof.profile.source || '—' }}</div></div>
                  <div class="info__c"><div class="info__l">Tình trạng học tập</div><div class="info__v"><InlineCell doctype="Student" :name="prof.profile.name" field="health_status" type="select" :options="HEALTH_STATUS" v-model="prof.profile.health_status" @saved="reloadStudents" /></div></div>
                  <div class="info__c"><div class="info__l">Trạng thái vòng đời</div><div class="info__v"><InlineCell doctype="Student" :name="prof.profile.name" field="student_status" type="select" :options="STUDENT_STATUS" v-model="prof.profile.student_status" @saved="reloadStudents" /></div></div>
                </div>
              </div>

              <div class="block">
                <div class="block__head">
                  <div class="block__title">Trợ lý AI ✨</div>
                </div>
                <AiAssistPanel :actions="STUDENT_AI" :context="aiContext" />
              </div>

              <div class="divider" />

              <div class="grid2">
                <div>
                  <div class="block__title">Người giám hộ</div>
                  <div v-if="prof.guardian" class="guardian">
                    <SkAvatar :name="prof.guardian.guardian_name" :size="42" />
                    <div>
                      <div class="guardian__name">{{ prof.guardian.guardian_name }}</div>
                      <div class="guardian__sub">{{ prof.guardian.phone || '—' }}</div>
                    </div>
                  </div>
                  <div v-else class="muted">Chưa có người giám hộ.</div>
                </div>
                <div>
                  <div class="block__head">
                    <div class="block__title">Lớp đang học</div>
                    <SkButton size="sm" variant="ghost" left-icon="plus" @click="openEnrollment">Đăng ký</SkButton>
                  </div>
                  <div v-if="activeEnr" class="clscard">
                    <div class="clscard__top">
                      <span class="clscard__name">{{ activeEnr.class_name || activeEnr.class_id }}</span>
                      <SkBadge variant="success" label="Active" />
                    </div>
                    <div class="clscard__sub">Net fee {{ formatVND(activeEnr.net_fee) }} · Đăng ký {{ formatDate(activeEnr.enrollment_date) }}</div>
                  </div>
                  <div v-else class="muted">Chưa có lớp đang học.</div>
                </div>
              </div>
            </div>

            <div v-else-if="tab === 'enrollment'" class="stack">
              <div class="block__head">
                <div>
                  <div class="block__title">Lịch sử đăng ký lớp</div>
                  <div class="block__hint">Tạo đăng ký sẽ tự submit, chốt học phí và sinh hóa đơn theo backend.</div>
                </div>
                <SkButton variant="solid" left-icon="plus" @click="openEnrollment">Đăng ký lớp</SkButton>
              </div>
              <div v-if="!prof.enrollments.length" class="empty-action">
                <div class="muted">Chưa có đăng ký nào.</div>
                <SkButton size="sm" variant="secondary" left-icon="plus" @click="openEnrollment">Đăng ký lớp đầu tiên</SkButton>
              </div>
              <div v-for="e in prof.enrollments" :key="e.name" class="enr">
                <div>
                  <div class="enr__title">{{ e.class_name || e.class_id }}</div>
                  <div class="enr__sub">{{ e.name }} · {{ formatDate(e.enrollment_date) }} · {{ e.enrollment_type }} · Net fee {{ formatVND(e.net_fee) }}</div>
                </div>
                <div class="enr__actions">
                  <SkBadge v-bind="enrMeta(e.enrollment_status)" />
                  <SkButton v-if="['Active', 'Deferred'].includes(e.enrollment_status)" size="sm" variant="solid" left-icon="git-branch" @click="openEnrWorkflow(e)">Thao tác</SkButton>
                  <SkButton size="sm" variant="ghost" @click="openEnrollmentDesk(e.name)">Mở</SkButton>
                </div>
              </div>
            </div>

            <div v-else-if="tab === 'attendance'">
              <div class="block__head">
                <div class="block__title">Chuyên cần · {{ prof.attendance.length }} buổi gần nhất</div>
                <SkButton size="sm" variant="secondary" left-icon="clipboard" @click="$router.push('/attendance')">Mở điểm danh</SkButton>
              </div>
              <div class="tblwrap">
                <table class="tbl">
                  <thead><tr><th>Ngày</th><th>Loại</th><th>Trạng thái</th><th style="text-align:right;">Đi muộn</th></tr></thead>
                  <tbody>
                    <tr v-if="!prof.attendance.length"><td colspan="4" class="muted" style="padding:16px;">Chưa có điểm danh.</td></tr>
                    <tr v-for="(a, i) in prof.attendance" :key="i">
                      <td class="tbl__name tnum">{{ formatDate(a.attendance_date) }}</td>
                      <td class="tbl__sub">{{ a.attendance_type || '—' }}</td>
                      <td><SkBadge v-bind="statusMeta('Student Attendance', 'status', a.status)" /></td>
                      <td class="tbl__sub tnum" style="text-align:right;">{{ a.minutes_late ? a.minutes_late + ' phút' : '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-else-if="tab === 'grades'">
              <div class="block__head">
                <div class="block__title">Điểm số theo kỹ năng · TB {{ score(prof.profile.average_score) }}</div>
                <SkButton size="sm" variant="secondary" left-icon="edit-3" @click="$router.push('/attendance')">Nhập điểm</SkButton>
              </div>
              <div class="tblwrap">
                <table class="tbl">
                  <thead><tr><th>Đánh giá</th><th>Loại</th><th style="text-align:right;">Điểm</th><th style="text-align:right;">Chuẩn hóa</th><th>Nhận xét</th></tr></thead>
                  <tbody>
                    <tr v-if="!prof.assessments.length"><td colspan="5" class="muted" style="padding:16px;">Chưa có điểm.</td></tr>
                    <tr v-for="(g, i) in prof.assessments" :key="i">
                      <td class="tbl__name">{{ g.assessment_name || '—' }}</td>
                      <td class="tbl__sub">{{ g.assessment_type || '—' }}</td>
                      <td class="tbl__name tnum" style="text-align:right;">{{ g.score }}</td>
                      <td class="tnum" style="text-align:right;" :style="{ color: normColor(g) }">{{ normalized(g) }}</td>
                      <td class="tbl__sub">{{ g.notes || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-else-if="tab === 'fees'" class="stack">
              <div class="grid3">
                <SkStatTile label="Tổng học phí" :value="formatVND(prof.fees.total)" />
                <SkStatTile label="Đã thu" :value="formatVND(prof.fees.paid)" value-color="#2f8a5d" />
                <SkStatTile label="Còn nợ" :value="formatVND(prof.fees.outstanding)" value-color="#c43232" :accent="prof.fees.outstanding > 0" />
              </div>
              <div>
                <div class="block__head">
                  <div class="block__title">Hóa đơn</div>
                  <SkButton
                    v-if="nextPayableInvoice"
                    size="sm"
                    variant="solid"
                    left-icon="credit-card"
                    @click="openPayment(nextPayableInvoice)"
                  >
                    Thu học phí
                  </SkButton>
                </div>
                <div class="tblwrap">
                  <table class="tbl">
                    <thead><tr><th>Mã hóa đơn</th><th>Hạn</th><th style="text-align:right;">Số tiền</th><th style="text-align:right;">Còn nợ</th><th style="text-align:right;">Trạng thái</th><th></th></tr></thead>
                    <tbody>
                      <tr v-if="!prof.invoices.length"><td colspan="6" class="muted" style="padding:16px;">Chưa có hóa đơn.</td></tr>
                      <tr v-for="i in prof.invoices" :key="i.name">
                        <td class="tbl__name tnum">{{ i.name }}</td>
                        <td class="tbl__sub tnum">{{ formatDate(i.due_date) }}</td>
                        <td class="tbl__name tnum" style="text-align:right;">{{ formatVND(i.total_amount) }}</td>
                        <td class="tnum" style="text-align:right;" :style="{ color: i.outstanding_amount > 0 ? '#c43232' : '#2f8a5d' }">{{ formatVND(i.outstanding_amount) }}</td>
                        <td style="text-align:right;"><SkBadge v-bind="statusMeta('Fee Invoice', 'status', i.status)" /></td>
                        <td style="text-align:right;">
                          <SkButton v-if="Number(i.outstanding_amount) > 0" size="sm" variant="ghost" @click="openPayment(i)">Thu</SkButton>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div v-else-if="tab === 'history'">
              <div class="block__title">Lịch sử hoạt động</div>
              <div v-if="!timeline.length" class="muted">Chưa có hoạt động.</div>
              <div class="timeline">
                <div v-for="(h, i) in timeline" :key="i" class="tl">
                  <div class="tl__rail"><span class="tl__dot" :style="{ background: h.dot }" /><span class="tl__line" /></div>
                  <div class="tl__body">
                    <div class="tl__date tnum">{{ formatDate(h.date) }}</div>
                    <div class="tl__title">{{ h.title }}</div>
                    <div class="tl__detail">{{ h.detail }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>

    <SkModal v-model="studentOpen" :title="studentMode === 'create' ? 'Thêm học viên' : 'Sửa hồ sơ học viên'" width="620px">
      <form class="form" @submit.prevent="saveStudent">
        <div class="form-grid">
          <label class="fg fg--full">
            <span>Họ và tên</span>
            <input v-model.trim="studentForm.full_name" class="field" required placeholder="Nguyễn Văn An" />
          </label>
          <label class="fg">
            <span>Điện thoại</span>
            <input v-model.trim="studentForm.phone" class="field" placeholder="09..." />
          </label>
          <label class="fg">
            <span>Email</span>
            <input v-model.trim="studentForm.email" class="field" type="email" placeholder="email@example.com" />
          </label>
          <label class="fg">
            <span>Ngày sinh</span>
            <input v-model="studentForm.date_of_birth" class="field" type="date" />
          </label>
          <label class="fg">
            <span>Giới tính</span>
            <select v-model="studentForm.gender" class="field">
              <option value=""></option>
              <option value="Nam">Nam</option>
              <option value="Nữ">Nữ</option>
              <option value="Khác">Khác</option>
            </select>
          </label>
          <label class="fg">
            <span>Nguồn</span>
            <select v-model="studentForm.source" class="field">
              <option value=""></option>
              <option value="Website">Website</option>
              <option value="Facebook">Facebook</option>
              <option value="Google">Google</option>
              <option value="Khác">Khác</option>
            </select>
          </label>
          <label class="fg">
            <span>Nghề nghiệp</span>
            <input v-model.trim="studentForm.occupation" class="field" placeholder="Sinh viên, nhân viên..." />
          </label>
          <label class="fg">
            <span>Trạng thái</span>
            <select v-model="studentForm.student_status" class="field">
              <option v-for="s in STUDENT_STATUS" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
          <label class="fg">
            <span>Tình trạng học tập</span>
            <select v-model="studentForm.health_status" class="field">
              <option v-for="s in HEALTH_STATUS" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingStudent" @click="studentOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingStudent" @click="saveStudent">{{ studentMode === 'create' ? 'Tạo học viên' : 'Lưu hồ sơ' }}</SkButton>
      </template>
    </SkModal>

    <SkModal v-model="enrollmentOpen" title="Đăng ký lớp" width="600px">
      <form class="form" @submit.prevent="saveEnrollment">
        <div class="form-grid">
          <label class="fg fg--full">
            <span>Lớp học</span>
            <select v-model="enrollmentForm.class_id" class="field" required>
              <option value="">Chọn lớp</option>
              <option v-for="c in classOptions" :key="c.name" :value="c.name">
                {{ c.class_name || c.name }} · {{ c.status || '—' }}
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Ngày nhập học</span>
            <input v-model="enrollmentForm.enrollment_date" class="field" type="date" required />
          </label>
          <label class="fg">
            <span>Loại đăng ký</span>
            <select v-model="enrollmentForm.enrollment_type" class="field">
              <option value="Official">Official</option>
              <option value="Trial">Trial</option>
            </select>
          </label>
          <label class="fg">
            <span>Giá niêm yết</span>
            <input v-model.number="enrollmentForm.list_price" class="field" type="number" min="0" step="1000" placeholder="Tự lấy theo lớp" />
          </label>
          <label class="fg">
            <span>Loại ưu đãi</span>
            <select v-model="enrollmentForm.discount_type" class="field">
              <option value=""></option>
              <option value="Percent">Percent</option>
              <option value="Amount">Amount</option>
            </select>
          </label>
          <label class="fg">
            <span>Giá trị ưu đãi</span>
            <input v-model.number="enrollmentForm.discount_value" class="field" type="number" min="0" step="1000" />
          </label>
          <label class="fg fg--full">
            <span>Lý do ưu đãi</span>
            <textarea v-model.trim="enrollmentForm.discount_reason" class="field field--area" placeholder="Ví dụ: ưu đãi học viên cũ, duyệt bởi..." />
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingEnrollment" @click="enrollmentOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingEnrollment" @click="saveEnrollment">Đăng ký</SkButton>
      </template>
    </SkModal>

    <WorkflowModal v-model="wfOpen" :title="wfTitle" :subtitle="wfSub" :actions="wfActions" @done="onWfDone" />

    <SkModal v-model="paymentOpen" title="Thu học phí" width="520px">
      <form class="form" @submit.prevent="savePayment">
        <div class="form-grid">
          <label class="fg fg--full">
            <span>Hóa đơn</span>
            <select v-model="paymentForm.invoice" class="field" required @change="syncInvoiceAmount">
              <option v-for="i in payableInvoices" :key="i.name" :value="i.name">
                {{ i.name }} · còn {{ formatVND(i.outstanding_amount) }}
              </option>
            </select>
          </label>
          <label class="fg">
            <span>Số tiền thu</span>
            <input v-model.number="paymentForm.amount" class="field" type="number" min="0" step="1000" required />
          </label>
          <label class="fg">
            <span>Ngày thu</span>
            <input v-model="paymentForm.payment_date" class="field" type="date" required />
          </label>
          <label class="fg">
            <span>Phương thức</span>
            <select v-model="paymentForm.payment_method" class="field">
              <option value="Cash">Cash</option>
              <option value="Bank Transfer">Bank Transfer</option>
              <option value="Card">Card</option>
              <option value="Other">Other</option>
            </select>
          </label>
          <label class="fg">
            <span>Mã tham chiếu</span>
            <input v-model.trim="paymentForm.reference_no" class="field" placeholder="Mã giao dịch" />
          </label>
        </div>
      </form>
      <template #footer>
        <SkButton variant="secondary" :disabled="savingPayment" @click="paymentOpen = false">Hủy</SkButton>
        <SkButton variant="solid" :loading="savingPayment" @click="savePayment">Xác nhận thu</SkButton>
      </template>
    </SkModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { call, db } from '../api'
import { formatVND, formatDate } from '../utils/format'
import { statusMeta } from '../utils/labels'
import { toast } from '../utils/toast'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkButton from '../components/ui/SkButton.vue'
import ExcelTools from '../components/ExcelTools.vue'
import { PERIODS, inPeriod } from '../utils/period'
import SkModal from '../components/ui/SkModal.vue'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkStatTile from '../components/ui/SkStatTile.vue'
import SkState from '../components/ui/SkState.vue'
import InlineCell from '../components/common/InlineCell.vue'
import WorkflowModal from '../components/common/WorkflowModal.vue'
import AiAssistPanel from '../components/common/AiAssistPanel.vue'

const TABS = [
  { id: 'overview', label: 'Tổng quan' },
  { id: 'enrollment', label: 'Đăng ký lớp' },
  { id: 'attendance', label: 'Chuyên cần' },
  { id: 'grades', label: 'Điểm số' },
  { id: 'fees', label: 'Học phí' },
  { id: 'history', label: 'Lịch sử' },
]
const FILTERS = ['Tất cả', 'Đang học', 'Cảnh báo']
const STUDENT_STATUS = ['Mới nhập học', 'Đang học', 'Bảo lưu', 'Đã tốt nghiệp', 'Nghỉ học']
const HEALTH_STATUS = ['Đang học đều', 'Cần theo dõi', 'Cảnh báo', 'Khẩn cấp', 'Ngừng học']

const loading = ref(true)
const error = ref('')
const students = ref([])
const q = ref('')
const filter = ref('Tất cả')
const period = ref('all')
const selectedId = ref(null)
const tab = ref('overview')
const today = () => new Date().toISOString().slice(0, 10)

const detailLoading = ref(false)
const prof = reactive({ profile: {}, guardian: null, enrollments: [], attendance: [], assessments: [], invoices: [], fees: {} })

const studentOpen = ref(false)
const studentMode = ref('create')
const savingStudent = ref(false)
const studentForm = ref(defaultStudentForm())

const enrollmentOpen = ref(false)
const savingEnrollment = ref(false)
const enrollmentForm = ref(defaultEnrollmentForm())
const classOptions = ref([])

const paymentOpen = ref(false)
const savingPayment = ref(false)
const paymentForm = ref(defaultPaymentForm())

const healthMeta = (s) => statusMeta('Student', 'health_status', s)
const enrMeta = (s) => {
  const map = { Active: 'success', Pending: 'warning', Deferred: 'warning', Completed: 'neutral', Dropped: 'danger', Transferred: 'info', Rejected: 'danger' }
  return { label: s || '—', variant: map[s] || 'neutral' }
}
const pct = (v) => `${Math.round(Number(v) || 0)}%`
const score = (v) => (v == null || v === '' ? '—' : Number(v).toFixed(1))

const filtered = computed(() => {
  let list = students.value
  const s = q.value.trim().toLowerCase()
  if (s) {
    list = list.filter((x) =>
      [x.full_name, x.name, x.phone, x.email].some((v) => String(v || '').toLowerCase().includes(s)),
    )
  }
  if (filter.value === 'Đang học') list = list.filter((x) => x.health_status === 'Đang học đều')
  else if (filter.value === 'Cảnh báo') list = list.filter((x) => ['Cảnh báo', 'Khẩn cấp'].includes(x.health_status))
  if (period.value !== 'all') list = list.filter((x) => inPeriod(x.creation, period.value))
  return list
})

const profileName = computed(() => prof.profile.full_name || selectedId.value)
const activeEnr = computed(() => prof.enrollments.find((e) => e.enrollment_status === 'Active'))
const payableInvoices = computed(() => prof.invoices.filter((i) => Number(i.outstanding_amount) > 0))
const nextPayableInvoice = computed(() => payableInvoices.value[0])

const progParts = computed(() => {
  const m = String(prof.profile.progress || '').match(/(\d+)\s*\/\s*(\d+)/)
  return m ? { done: +m[1], total: +m[2] } : { done: 0, total: 0 }
})
const sessionsDone = computed(() => progParts.value.done)
const sessionsTotal = computed(() => progParts.value.total)
const progressPct = computed(() => (progParts.value.total ? `${Math.round((progParts.value.done / progParts.value.total) * 100)}%` : '0%'))

function normalized(g) {
  const max = Number(g.max_score) || 100
  return max ? `${Math.round((Number(g.score) / max) * 100)}%` : '—'
}
function normColor(g) {
  const max = Number(g.max_score) || 100
  const n = max ? (Number(g.score) / max) * 100 : 0
  return n >= 80 ? '#2f8a5d' : n >= 70 ? '#b07a1f' : '#c44a3f'
}

const timeline = computed(() => {
  const items = []
  for (const e of prof.enrollments) items.push({ date: e.enrollment_date || e.creation, title: `Đăng ký lớp ${e.class_id}`, detail: `${e.name} · Trạng thái ${e.enrollment_status}`, dot: '#9b6fc4' })
  for (const i of prof.invoices) items.push({ date: i.posting_date, title: `Hóa đơn ${i.name}`, detail: `${formatVND(i.total_amount)} · ${statusMeta('Fee Invoice', 'status', i.status).label}`, dot: '#3f9b6e' })
  return items.filter((x) => x.date).sort((a, b) => String(b.date).localeCompare(String(a.date))).slice(0, 12)
})

function defaultStudentForm() {
  return {
    full_name: '',
    phone: '',
    email: '',
    date_of_birth: '',
    gender: '',
    source: '',
    occupation: '',
    student_status: 'Mới nhập học',
    health_status: 'Đang học đều',
  }
}
function defaultEnrollmentForm() {
  return {
    class_id: '',
    enrollment_date: today(),
    enrollment_type: 'Official',
    list_price: '',
    discount_type: '',
    discount_value: 0,
    discount_reason: '',
  }
}
function defaultPaymentForm() {
  return { invoice: '', amount: 0, payment_date: today(), payment_method: 'Cash', reference_no: '' }
}
function cleanPayload(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== '' && value != null))
}

function openCreateStudent() {
  studentMode.value = 'create'
  studentForm.value = defaultStudentForm()
  studentOpen.value = true
}
function openEditStudent() {
  if (!selectedId.value) return
  studentMode.value = 'edit'
  studentForm.value = {
    ...defaultStudentForm(),
    full_name: prof.profile.full_name || '',
    phone: prof.profile.phone || '',
    email: prof.profile.email || '',
    date_of_birth: prof.profile.date_of_birth || '',
    gender: prof.profile.gender || '',
    source: prof.profile.source || '',
    occupation: prof.profile.occupation || '',
    student_status: prof.profile.student_status || 'Mới nhập học',
    health_status: prof.profile.health_status || 'Đang học đều',
  }
  studentOpen.value = true
}
async function saveStudent() {
  if (!studentForm.value.full_name) {
    toast.error('Thiếu họ tên học viên')
    return
  }
  savingStudent.value = true
  try {
    let id = selectedId.value
    if (studentMode.value === 'create') {
      const created = await db.insert({ doctype: 'Student', ...cleanPayload(studentForm.value) })
      id = created.name
      toast.success('Đã thêm học viên')
    } else {
      await db.setValue('Student', selectedId.value, cleanPayload(studentForm.value))
      toast.success('Đã lưu hồ sơ')
    }
    studentOpen.value = false
    await reloadStudents()
    await select(id, true)
  } catch (e) {
    toast.error('Không lưu được học viên', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingStudent.value = false
  }
}

function openEnrollment() {
  if (!selectedId.value) return
  enrollmentForm.value = defaultEnrollmentForm()
  if (!classOptions.value.length) loadClassOptions()
  enrollmentOpen.value = true
}
async function saveEnrollment() {
  if (!selectedId.value || !enrollmentForm.value.class_id) {
    toast.error('Thiếu lớp đăng ký')
    return
  }
  savingEnrollment.value = true
  try {
    await call('create_enrollment', { student: selectedId.value, ...cleanPayload(enrollmentForm.value), submit: 1 })
    toast.success('Đã đăng ký lớp')
    enrollmentOpen.value = false
    tab.value = 'enrollment'
    await reloadStudents()
    await loadDetail(selectedId.value)
  } catch (e) {
    toast.error('Không đăng ký được lớp', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingEnrollment.value = false
  }
}

function openPayment(invoice) {
  paymentForm.value = {
    ...defaultPaymentForm(),
    invoice: invoice.name,
    amount: Number(invoice.outstanding_amount) || 0,
  }
  paymentOpen.value = true
}
function syncInvoiceAmount() {
  const inv = payableInvoices.value.find((i) => i.name === paymentForm.value.invoice)
  if (inv) paymentForm.value.amount = Number(inv.outstanding_amount) || 0
}
async function savePayment() {
  if (!selectedId.value || !paymentForm.value.invoice || Number(paymentForm.value.amount) <= 0) {
    toast.error('Thiếu thông tin thu học phí')
    return
  }
  savingPayment.value = true
  try {
    await call('create_payment', { student: selectedId.value, ...cleanPayload(paymentForm.value) })
    toast.success('Đã ghi nhận học phí')
    paymentOpen.value = false
    tab.value = 'fees'
    await loadDetail(selectedId.value)
  } catch (e) {
    toast.error('Không thu được học phí', e?.messages?.[0] || e?.message || String(e))
  } finally {
    savingPayment.value = false
  }
}

/* ---- Trợ lý AI ---- */
const STUDENT_AI = [
  { label: 'Tóm tắt hồ sơ', icon: 'file-text', prompt: 'Tóm tắt ngắn gọn tình hình học viên này (học lực, chuyên cần, học phí).' },
  { label: 'Cảnh báo rủi ro', icon: 'alert-triangle', prompt: 'Đánh giá rủi ro bỏ học/cần can thiệp của học viên này và đề xuất 2-3 hành động cụ thể.' },
]
const aiContext = computed(() => {
  const p = prof.profile
  return [
    `Tên: ${p.full_name || ''}`,
    `Trạng thái: ${p.student_status || ''} / ${p.health_status || ''}`,
    `Chuyên cần: ${pct(p.attendance_rate)}`,
    `Điểm TB: ${score(p.average_score)}`,
    `Tiến độ: ${p.progress || ''}`,
    `Công nợ: ${formatVND(prof.fees?.outstanding || 0)}`,
    `Số đăng ký lớp: ${prof.enrollments?.length || 0}`,
  ].join('\n')
})

/* ---- Workflow đăng ký lớp (bảo lưu / tiếp tục / chuyển lớp / nghỉ học) ---- */
const wfOpen = ref(false)
const wfTitle = ref('')
const wfSub = ref('')
const wfActions = ref([])

function openEnrWorkflow(e) {
  wfTitle.value = 'Thao tác đăng ký lớp'
  wfSub.value = `${e.class_id} · ${e.name} · ${e.enrollment_status}`
  const classOpts = classOptions.value.map((c) => ({ value: c.name, label: c.class_name || c.name }))
  const actions = []
  if (e.enrollment_status === 'Active') {
    actions.push({
      value: 'defer', label: 'Bảo lưu', successMsg: 'Đã bảo lưu',
      fields: [
        { key: 'leave_from_date', label: 'Từ ngày', type: 'date', required: true, default: today() },
        { key: 'leave_to_date', label: 'Đến ngày', type: 'date', required: true },
        { key: 'reason', label: 'Lý do', type: 'textarea', full: true },
      ],
      run: (f) => call('defer_enrollment', { program_enrollment: e.name, leave_from_date: f.leave_from_date, leave_to_date: f.leave_to_date, reason: f.reason }),
    })
    actions.push({
      value: 'transfer', label: 'Chuyển lớp', successMsg: 'Đã chuyển lớp',
      hint: 'Đóng đăng ký hiện tại (Transferred) và tạo đăng ký mới ở lớp đích.',
      fields: [
        { key: 'to_class', label: 'Lớp mới', type: 'select', options: classOpts, required: true, full: true },
        { key: 'transfer_date', label: 'Ngày chuyển', type: 'date', default: today() },
        { key: 'reason', label: 'Lý do', type: 'textarea', full: true },
      ],
      run: (f) => call('transfer_enrollment', { program_enrollment: e.name, to_class: f.to_class, transfer_date: f.transfer_date, reason: f.reason }),
    })
  }
  if (e.enrollment_status === 'Deferred') {
    actions.push({ value: 'resume', label: 'Tiếp tục học', successMsg: 'Đã tiếp tục học', run: () => call('resume_enrollment', { program_enrollment: e.name }) })
  }
  actions.push({
    value: 'drop', label: 'Nghỉ học', successMsg: 'Đã cho nghỉ học',
    hint: 'Đánh dấu nghỉ học. Hoàn phí (nếu có) sẽ duyệt ở màn Tài chính.',
    fields: [{ key: 'reason', label: 'Lý do', type: 'textarea', full: true }],
    run: (f) => call('drop_enrollment', { program_enrollment: e.name, reason: f.reason }),
  })
  wfActions.value = actions
  wfOpen.value = true
}
async function onWfDone() {
  await reloadStudents()
  await loadDetail(selectedId.value)
}

function openDesk() {
  if (selectedId.value) window.open(`/app/student/${selectedId.value}`, '_blank')
}
function openEnrollmentDesk(name) {
  window.open(`/app/program-enrollment/${name}`, '_blank')
}

async function select(id, keepTab = false) {
  selectedId.value = id
  if (!keepTab) tab.value = 'overview'
  await loadDetail(id)
}
async function loadDetail(id) {
  detailLoading.value = true
  try {
    const res = await call('get_student_profile', { student: id })
    Object.assign(prof, { profile: {}, guardian: null, enrollments: [], attendance: [], assessments: [], invoices: [], fees: {} }, res || {})
  } catch (e) {
    toast.error('Không tải được hồ sơ', e?.message || String(e))
  } finally {
    detailLoading.value = false
  }
}
async function reloadStudents() {
  students.value = (await call('get_students')) || []
}
async function loadClassOptions() {
  try {
    classOptions.value = await db.getList('Class', {
      fields: ['name', 'class_name', 'status', 'standard_fee'],
      filters: { status: ['in', ['Upcoming', 'Ongoing']] },
      order_by: 'modified desc',
      limit_page_length: 100,
    })
  } catch (e) {
    toast.error('Không tải được danh sách lớp', e?.message || String(e))
  }
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    await reloadStudents()
    loadClassOptions()
    if (students.value.length) {
      const next = selectedId.value && students.value.some((s) => s.name === selectedId.value) ? selectedId.value : students.value[0].name
      await select(next, true)
    } else {
      selectedId.value = null
    }
  } catch (e) {
    error.value = e?.message || String(e)
    students.value = []
    selectedId.value = null
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.md { flex: 1; min-width: 0; display: flex; height: 100vh; }

.ctx { flex: none; width: 326px; display: flex; flex-direction: column; background: rgba(255, 252, 253, 0.82); border-right: 1px solid #f2d4df; }
.ctx__head { height: 56px; flex: none; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 0 14px 0 18px; border-bottom: 1px solid #f4dde5; }
.ctx__head-act { display: flex; align-items: center; gap: 8px; }
.period-wrap { display: inline-flex; align-items: center; gap: 6px; }
.period-cap { font-size: 11.5px; font-weight: 600; color: #a07c8a; white-space: nowrap; }
.period-sel { height: 32px; border: 1px solid #ecd0da; border-radius: 8px; background: #fff; padding: 0 9px; font-size: 12px; color: #7a5c68; font-family: inherit; cursor: pointer; outline: none; }
.period-sel:focus { border-color: #d4567f; }
.ctx__title { font-size: 16px; font-weight: 600; color: #4a2230; }
.ctx__count { margin-left: 8px; font-size: 11.5px; color: #a98c98; }
.ctx__tools { padding: 12px 14px 10px; display: flex; flex-direction: column; gap: 10px; }
.field--icon { display: flex; align-items: center; gap: 8px; }
.field--icon input { flex: 1; min-width: 0; border: none; outline: none; background: none; font-family: inherit; font-size: 13px; color: #3d2530; }
.field--icon input::placeholder { color: #bd8d9c; }
.ctx__list { flex: 1; overflow-y: auto; padding-bottom: 12px; }

.srow { display: flex; align-items: center; gap: 11px; width: 100%; text-align: left; border: none; border-bottom: 1px solid #f7e6ec; background: transparent; padding: 10px 14px 10px 11px; cursor: pointer; border-left: 3px solid transparent; font-family: inherit; }
.srow:hover { background: #fdf2f6; }
.srow--active { background: #fbd9e5; border-left-color: #d6557e; }
.srow__main { flex: 1; min-width: 0; }
.srow__top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.srow__name { font-size: 13.5px; font-weight: 600; color: #3d2530; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.srow__bottom { display: flex; justify-content: space-between; gap: 8px; margin-top: 4px; }
.srow__sub { font-size: 11.5px; color: #a98c98; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.srow__note { font-size: 11px; color: #bd97a5; flex: none; }

.dtl { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; }
.dtl__head { height: 56px; flex: none; display: flex; align-items: center; gap: 11px; padding: 0 18px; border-bottom: 1px solid #f1dbe3; }
.dtl__id { min-width: 0; display: flex; align-items: center; gap: 9px; }
.dtl__name { font-size: 16px; font-weight: 600; color: #3d2530; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dtl__slash { font-size: 13px; color: #bd97a5; }
.dtl__code { font-size: 13px; color: #a98c98; }
.dtl__actions { margin-left: auto; display: flex; gap: 8px; }
.dtl__tabs { flex: none; display: flex; align-items: center; padding: 0 24px; border-bottom: 1px solid #f1dbe3; overflow-x: auto; }
.tab { border: none; background: none; padding: 13px 2px 12px; margin-right: 28px; cursor: pointer; font-family: inherit; font-size: 13.5px; font-weight: 500; color: #7a5c68; border-bottom: 2px solid transparent; white-space: nowrap; }
.tab--active { color: #b8456a; font-weight: 600; border-bottom-color: #d6557e; }
.dtl__body { flex: 1; overflow-y: auto; }
.dtl__inner { padding: 26px 30px 44px; max-width: 1120px; }

.ovw { display: flex; flex-direction: column; gap: 30px; }
.grid4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.grid2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 32px; }
.stack { display: flex; flex-direction: column; gap: 22px; }
.block__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.block__title { font-size: 15px; font-weight: 600; color: #4a2230; }
.block__hint { margin-top: 3px; font-size: 12px; color: #a98c98; }
.info { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 32px; }
.info__l { font-size: 11.5px; color: #a98c98; margin-bottom: 3px; }
.info__v { font-size: 14px; color: #3d2530; font-weight: 500; min-width: 0; overflow-wrap: anywhere; }
.divider { height: 1px; background: #f4dde5; }
.guardian { display: flex; align-items: center; gap: 12px; }
.guardian__name { font-size: 14px; font-weight: 600; color: #3d2530; }
.guardian__sub { font-size: 12px; color: #a98c98; }
.clscard { border: 1px solid #f3d9e1; border-radius: 11px; padding: 14px 16px; background: #fff; }
.clscard__top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.clscard__name { font-size: 14px; font-weight: 600; color: #3d2530; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.clscard__sub { font-size: 12.5px; color: #a98c98; margin-top: 7px; }
.muted { font-size: 13px; color: #a98c98; }
.empty-action { border: 1px dashed #efcdd9; border-radius: 11px; padding: 20px; display: flex; align-items: center; justify-content: space-between; gap: 14px; background: #fffafb; }

.enr { border: 1px solid #f3d9e1; border-radius: 11px; padding: 15px 17px; background: #fff; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.enr__title { font-size: 14px; font-weight: 600; color: #3d2530; }
.enr__sub { font-size: 12.5px; color: #a98c98; margin-top: 4px; }
.enr__actions { flex: none; display: flex; align-items: center; gap: 8px; }

.tblwrap { border: 1px solid #f3d9e1; border-radius: 11px; overflow: auto; background: #fff; }
.tbl { width: 100%; border-collapse: collapse; min-width: 720px; }
.tbl thead tr { background: #fdf2f6; }
.tbl th { text-align: left; font-size: 11.5px; font-weight: 600; color: #a07c8a; padding: 10px 16px; }
.tbl td { padding: 12px 16px; border-top: 1px solid #f6e3ea; }
.tbl tbody tr:hover { background: #fefafb; }
.tbl__name { font-size: 13.5px; font-weight: 500; color: #3d2530; }
.tbl__sub { font-size: 13px; color: #7a5c68; }

.timeline { display: flex; flex-direction: column; }
.tl { display: flex; gap: 14px; }
.tl__rail { flex: none; display: flex; flex-direction: column; align-items: center; }
.tl__dot { width: 11px; height: 11px; border-radius: 50%; margin-top: 4px; }
.tl__line { flex: 1; width: 2px; background: #f4dde5; }
.tl__body { padding-bottom: 20px; }
.tl__date { font-size: 11.5px; color: #bd97a5; }
.tl__title { font-size: 13.5px; font-weight: 500; color: #3d2530; margin-top: 2px; }
.tl__detail { font-size: 12.5px; color: #a98c98; margin-top: 2px; }

.form { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.fg { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fg--full { grid-column: 1 / -1; }
.fg > span { font-size: 12px; font-weight: 600; color: #7a5c68; }
.field { width: 100%; min-height: 36px; border: 1px solid #ecd0da; border-radius: 9px; background: #fff; padding: 0 11px; color: #3d2530; font-family: inherit; font-size: 13.5px; outline: none; }
.field--area { min-height: 72px; resize: vertical; padding: 9px 11px; }
.field:focus { border-color: #d4567f; box-shadow: 0 0 0 3px rgba(212, 86, 127, 0.12); }

@media (max-width: 1100px) {
  .ctx { width: 292px; }
  .grid4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .info { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
