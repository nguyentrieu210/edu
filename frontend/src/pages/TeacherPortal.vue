<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-xl font-bold text-ink-2">Cổng Giáo Viên</h3>
      <p class="text-xs text-muted mt-1">Lịch dạy hôm nay và các lớp được phân công (chỉ hiển thị dữ liệu của bạn).</p>
    </div>

    <div v-if="overview.loading" class="flex justify-center py-8"><LoadingIndicator /></div>

    <div v-else-if="overview.error" class="rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
      Tài khoản của bạn chưa được gắn với hồ sơ giáo viên. Liên hệ giáo vụ để được cấp quyền.
    </div>

    <template v-else-if="overview.data">
      <!-- Today sessions -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Buổi dạy hôm nay</h4></div>
        <div v-if="(overview.data.sessions_today || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Hôm nay bạn không có buổi dạy nào.</div>
        <div v-else class="divide-y divide-border">
          <div v-for="s in overview.data.sessions_today" :key="s.name" class="px-6 py-3 flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-ink-2">{{ s.class_id }} · {{ fmt(s.start_time) }}–{{ fmt(s.end_time) }}</p>
              <p class="text-xs text-muted">{{ s.lesson_topic || 'Chưa cập nhật nội dung' }}</p>
            </div>
            <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">{{ s.session_status }}</span>
          </div>
        </div>
      </div>

      <!-- My classes -->
      <div class="overflow-hidden rounded-xl border border-border bg-white shadow-sm">
        <div class="px-6 py-4 border-b border-border bg-hover/40"><h4 class="text-sm font-semibold text-ink-2 uppercase tracking-wider">Lớp được phân công</h4></div>
        <div v-if="(overview.data.classes || []).length === 0" class="px-6 py-8 text-center text-sm text-muted">Chưa có lớp nào.</div>
        <table v-else class="min-w-full divide-y divide-border">
          <thead class="bg-hover/40"><tr>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Lớp</th>
            <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted">Trạng thái</th>
            <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-muted">Tiến độ</th>
          </tr></thead>
          <tbody class="divide-y divide-border">
            <tr v-for="c in overview.data.classes" :key="c.name" class="hover:bg-hover/40">
              <td class="px-6 py-3 text-sm font-medium text-ink-2">{{ c.name }} - {{ c.class_name }}</td>
              <td class="px-6 py-3 text-sm text-muted">{{ c.status }}</td>
              <td class="px-6 py-3 text-right text-sm font-semibold text-brand tabular-nums">{{ (c.progress || 0).toFixed(0) }}%</td>
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

const overview = apiResource('get_my_teacher_overview', { auto: true })
const fmt = (t) => (t ? String(t).slice(0, 5) : '')
</script>
