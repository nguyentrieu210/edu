<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-xl font-bold text-ink-2">Cổng Học Viên</h3>
      <p class="text-xs text-muted mt-1">Tiến độ, điểm số, bài tập và công nợ của bạn (chỉ hiển thị dữ liệu cá nhân).</p>
    </div>

    <div v-if="overview.loading" class="flex justify-center py-8"><LoadingIndicator /></div>

    <div v-else-if="overview.error" class="rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
      Tài khoản của bạn chưa được gắn với hồ sơ học viên. Liên hệ giáo vụ để được cấp quyền.
    </div>

    <template v-else-if="overview.data">
      <!-- Metric tiles -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Tiến độ</p>
          <h4 class="text-lg font-bold text-ink-2 mt-1">{{ overview.data.profile?.progress || '—' }}</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Chuyên cần</p>
          <h4 class="text-lg font-bold text-brand mt-1">{{ (overview.data.profile?.attendance_rate || 0).toFixed(0) }}%</h4>
        </div>
        <div class="bg-white p-4 rounded-xl border border-border shadow-sm">
          <p class="text-xs text-muted font-semibold uppercase tracking-wider">Điểm trung bình</p>
          <h4 class="text-lg font-bold text-blue-600 mt-1">{{ (overview.data.profile?.average_score || 0).toFixed(1) }}</h4>
        </div>
      </div>

      <!-- Homework -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Bài tập</h4></div>
        <div v-if="(overview.data.homework || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Không có bài tập nào.</div>
        <div v-else class="divide-y divide-border">
          <div v-for="h in overview.data.homework" :key="h.name" class="px-6 py-3 flex items-center justify-between">
            <p class="text-sm font-medium text-ink-2">{{ h.title }} <span class="text-xs text-faint">· {{ h.class_id }}</span></p>
            <span class="text-xs text-muted">Hạn: {{ h.due_date || '—' }}</span>
          </div>
        </div>
      </div>

      <!-- Recent assessments -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Điểm gần đây</h4></div>
        <div v-if="(overview.data.recent_assessments || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Chưa có điểm.</div>
        <table v-else class="min-w-full divide-y divide-border">
          <tbody class="divide-y divide-border">
            <tr v-for="(a, i) in overview.data.recent_assessments" :key="i" class="hover:bg-hover/40">
              <td class="px-6 py-3 text-sm text-ink-2">{{ a.assessment_name }} <span class="text-xs text-faint">· {{ a.assessment_type }}</span></td>
              <td class="px-6 py-3 text-right text-sm font-semibold text-ink-2 tabular-nums">{{ a.score }} / {{ a.max_score }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Invoices -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Học phí & công nợ</h4></div>
        <div v-if="(overview.data.invoices || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Không có hóa đơn.</div>
        <table v-else class="min-w-full divide-y divide-border">
          <thead class="bg-hover/40"><tr>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Hóa đơn</th>
            <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Tổng</th>
            <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Còn nợ</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng thái</th>
          </tr></thead>
          <tbody class="divide-y divide-border">
            <tr v-for="inv in overview.data.invoices" :key="inv.name" class="hover:bg-hover/40">
              <td class="px-6 py-3 text-sm font-medium text-brand">{{ inv.name }}</td>
              <td class="px-6 py-3 text-right text-sm tabular-nums">{{ money(inv.total_amount) }}</td>
              <td class="px-6 py-3 text-right text-sm tabular-nums" :class="inv.outstanding_amount > 0 ? 'text-thaco-red font-semibold' : 'text-muted'">{{ money(inv.outstanding_amount) }}</td>
              <td class="px-6 py-3 text-sm text-muted">{{ inv.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { LoadingIndicator } from 'frappe-ui'
import { apiResource } from '../api'

const overview = apiResource('get_my_student_overview', { auto: true })
const money = (v) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(v || 0)
</script>
