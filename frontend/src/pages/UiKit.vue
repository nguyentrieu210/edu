<template>
  <div class="ws">
    <header class="ws-head">
      <span class="ws-head__title">Component Library</span>
      <span class="ws-head__sub">Sakura UI Kit · token + component chuẩn</span>
    </header>

    <div class="ws-body sk-scroll">
      <!-- Buttons -->
      <section class="sec">
        <div class="sec__label">Buttons</div>
        <div class="box col">
          <div class="row">
            <SkButton variant="solid">Primary</SkButton>
            <SkButton variant="secondary">Secondary</SkButton>
            <SkButton variant="ghost">Ghost</SkButton>
            <SkButton variant="danger">Danger</SkButton>
          </div>
          <div class="hr" />
          <div class="row">
            <SkButton variant="solid" size="sm">Small</SkButton>
            <SkButton variant="solid" size="md">Medium</SkButton>
            <SkButton variant="solid" size="lg">Large</SkButton>
            <SkButton variant="solid" loading>Đang lưu…</SkButton>
            <SkButton variant="solid" disabled>Disabled</SkButton>
          </div>
          <div class="hr" />
          <div class="row">
            <SkButton variant="secondary" icon><FeatherIcon name="edit-2" style="width:16px;height:16px;" /></SkButton>
            <SkButton variant="danger" icon><FeatherIcon name="trash-2" style="width:16px;height:16px;" /></SkButton>
            <SkButton variant="secondary" icon><FeatherIcon name="more-horizontal" style="width:18px;height:18px;" /></SkButton>
          </div>
        </div>
      </section>

      <!-- Inputs -->
      <section class="sec">
        <div class="sec__label">Inputs & controls</div>
        <div class="box grid3">
          <div>
            <div class="f-label">Họ và tên</div>
            <input class="field" value="Nguyễn Văn An" />
          </div>
          <div>
            <div class="f-label">Select</div>
            <div class="field field--select">N5 cấp tốc <FeatherIcon name="chevron-down" style="width:15px;height:15px;color:#bd8d9c;" /></div>
          </div>
          <div>
            <div class="f-label">Search</div>
            <div class="field field--icon"><FeatherIcon name="search" style="width:15px;height:15px;color:#bd8d9c;" /><span>Tìm kiếm…</span></div>
          </div>
          <div>
            <div class="f-label">Segmented</div>
            <SkSegmented v-model="seg" :options="['Tháng', 'Tuần', 'Ngày']" />
          </div>
          <div>
            <div class="f-label">Number / stepper</div>
            <div class="stepper">
              <button @click="num = Math.max(0, num - 1)">−</button>
              <span class="tnum">{{ num }}</span>
              <button @click="num++">+</button>
            </div>
          </div>
          <div>
            <div class="f-label">Avatar</div>
            <SkAvatar name="Nguyễn Văn An" :size="36" />
          </div>
        </div>
      </section>

      <!-- Badges -->
      <section class="sec">
        <div class="sec__label">Badges</div>
        <div class="box row">
          <SkBadge variant="success" label="Active" />
          <SkBadge variant="info" label="Upcoming" />
          <SkBadge variant="warning" label="Warning" />
          <SkBadge variant="neutral" label="Cancelled" />
          <SkBadge variant="danger" label="Overdue" />
          <SkBadge variant="sakura" label="Sakura" />
        </div>
      </section>

      <!-- States -->
      <section class="sec">
        <div class="sec__label">Trạng thái màn hình</div>
        <div class="grid2">
          <div class="box"><SkState state="empty" title="Chưa có học viên" message="Thêm học viên đầu tiên để bắt đầu." action-label="Thêm học viên" /></div>
          <div class="box"><SkState state="loading" /></div>
          <div class="box" style="padding:0;"><SkState state="error" title="Không tải được dữ liệu" message="Đã xảy ra lỗi khi tải danh sách." action-label="Thử lại" /></div>
          <div class="box"><SkState state="denied" title="Không có quyền truy cập" message="Tài khoản không được phép xem nội dung này (403)." action-label="Quay lại" /></div>
        </div>
      </section>

      <!-- Overlays -->
      <section class="sec">
        <div class="sec__label">Overlays</div>
        <div class="box row">
          <SkButton variant="secondary" @click="modal = true">Mở Modal</SkButton>
          <SkButton variant="secondary" @click="drawer = true">Mở Drawer</SkButton>
          <SkButton variant="secondary" @click="toast.success('Đã lưu thành công', 'Hồ sơ học viên đã được cập nhật.')">Hiện Toast</SkButton>
        </div>
      </section>

      <!-- Tokens -->
      <section class="sec">
        <div class="sec__label">Design tokens · Màu</div>
        <div class="box row">
          <div v-for="c in colors" :key="c.name" class="swatch">
            <div class="swatch__chip" :style="{ background: c.hex }" />
            <div class="swatch__name">{{ c.name }}</div>
          </div>
        </div>
      </section>
    </div>

    <SkModal v-model="modal" title="Xác nhận xóa học viên">
      Bạn sắp xóa hồ sơ <b>Nguyễn Văn An</b>. Hành động này không thể hoàn tác.
      <template #footer>
        <SkButton variant="secondary" @click="modal = false">Hủy</SkButton>
        <SkButton variant="danger" @click="modal = false">Xóa</SkButton>
      </template>
    </SkModal>

    <SkDrawer v-model="drawer" title="Inspector · Nguyễn Văn An">
      <div class="insp"><div class="insp__l">Mã học viên</div><div class="insp__v">STU-2026-0034</div></div>
      <div class="insp"><div class="insp__l">Lớp đang học</div><div class="insp__v">N5-TP-001 · N5 cấp tốc</div></div>
      <div class="insp"><div class="insp__l">Chuyên cần</div><div class="insp__v">78% · 8/12 buổi</div></div>
    </SkDrawer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { toast } from '../utils/toast'
import SkButton from '../components/ui/SkButton.vue'
import SkBadge from '../components/ui/SkBadge.vue'
import SkAvatar from '../components/ui/SkAvatar.vue'
import SkSegmented from '../components/ui/SkSegmented.vue'
import SkState from '../components/ui/SkState.vue'
import SkModal from '../components/ui/SkModal.vue'
import SkDrawer from '../components/ui/SkDrawer.vue'

const seg = ref('Tháng')
const num = ref(16)
const modal = ref(false)
const drawer = ref(false)

const colors = [
  { name: 'sakura-300', hex: '#f7a8c4' },
  { name: 'sakura-400', hex: '#e87aa3' },
  { name: 'sakura-500', hex: '#d6557e' },
  { name: 'sakura-600', hex: '#b8456a' },
  { name: 'success', hex: '#3f9b6e' },
  { name: 'warning', hex: '#c98a2e' },
  { name: 'danger', hex: '#c43232' },
  { name: 'info', hex: '#4a6fb5' },
  { name: 'text', hex: '#3d2530' },
]
</script>

<style scoped>
.ws { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fffdfe; height: 100vh; }
.ws-head { height: 56px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 24px; border-bottom: 1px solid #f1dbe3; }
.ws-head__title { font-size: 16px; font-weight: 600; color: #3d2530; }
.ws-head__sub { font-size: 13px; color: #a98c98; }
.ws-body { flex: 1; overflow-y: auto; padding: 26px 30px 60px; max-width: 1100px; }

.sec { margin-bottom: 30px; }
.sec__label { font-size: 12px; font-weight: 700; color: #b8456a; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 13px; }
.box { border: 1px solid #f3d9e1; border-radius: 12px; background: #fff; padding: 22px; }
.box.col { display: flex; flex-direction: column; gap: 18px; }
.row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.hr { height: 1px; background: #f6e3ea; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 22px 24px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.f-label { font-size: 12px; color: #7a5c68; font-weight: 500; margin-bottom: 6px; }
.field--select, .field--icon { display: flex; align-items: center; gap: 8px; color: #3d2530; }
.field--select { justify-content: space-between; }
.field--icon span { color: #bd8d9c; font-size: 13px; }
.stepper { display: flex; align-items: center; height: 36px; border: 1px solid #ecd0da; border-radius: 8px; width: 120px; overflow: hidden; }
.stepper button { width: 34px; height: 100%; border: none; background: #fdf2f6; color: #b8456a; cursor: pointer; font-size: 16px; }
.stepper span { flex: 1; text-align: center; font-size: 13px; color: #3d2530; }

.swatch { text-align: center; }
.swatch__chip { width: 56px; height: 44px; border-radius: 9px; border: 1px solid rgba(0,0,0,0.04); }
.swatch__name { font-size: 10.5px; color: #a98c98; margin-top: 5px; }

.insp { margin-bottom: 16px; }
.insp__l { font-size: 11.5px; color: #a98c98; margin-bottom: 3px; }
.insp__v { font-size: 14px; color: #3d2530; font-weight: 500; }
</style>
