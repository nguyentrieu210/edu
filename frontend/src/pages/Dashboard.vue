<template>
  <div class="space-y-6">
    <!-- Stat Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
      <div class="card-paper p-5">
        <p class="eyebrow-muted mb-2">Tổng Số Học Viên</p>
        <p class="text-3xl font-semibold text-ink num">{{ stats.data?.students_count || 0 }}</p>
      </div>
      <div class="card-paper p-5">
        <p class="eyebrow mb-2">Doanh Thu Đã Thu</p>
        <p class="text-3xl font-semibold text-sage num">{{ formatCurrency(stats.data?.paid_amount || 0) }}</p>
      </div>
      <div class="card-paper p-5">
        <p class="eyebrow-muted mb-2 !text-rose">Tổng Số Tiền Còn Nợ</p>
        <p class="text-3xl font-semibold text-rose num">{{ formatCurrency(stats.data?.outstanding_amount || 0) }}</p>
      </div>
    </div>

    <!-- Quick Actions or Recent Activities -->
    <div class="card-paper p-5">
      <div class="eyebrow mb-3">Thông tin chung</div>
      <h3 class="ff-display text-lg font-semibold text-ink">Chào mừng bạn đến với hệ thống ERP giáo dục trung tâm IKE Ohashi.</h3>
      <p class="mt-1 text-sm text-muted leading-relaxed">Phân hệ quản lý học phí và học viên đã sẵn sàng hoạt động. Mọi tính năng được tối ưu hóa cho tốc độ và trải nghiệm mượt mà.</p>
    </div>
  </div>
</template>

<script setup>
import { apiResource } from '../api'

const formatCurrency = (val) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val)
}

const stats = apiResource('get_dashboard_stats', { auto: true })
</script>
