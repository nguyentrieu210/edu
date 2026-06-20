import { createRouter, createWebHistory } from 'vue-router'

// Cấu trúc điều hướng — nguồn duy nhất cho Sidebar + Command Palette.
// icon dùng tên FeatherIcon (feather/lucide).
export const NAV_SECTIONS = [
  {
    label: '',
    items: [{ label: 'Dashboard', icon: 'grid', path: '/' }],
  },
  {
    label: 'Tuyển sinh & học viên',
    items: [
      { label: 'Tuyển sinh', icon: 'user-plus', path: '/admissions' },
      { label: 'Học viên', icon: 'users', path: '/students' },
    ],
  },
  {
    label: 'Đào tạo',
    items: [
      { label: 'Lớp học', icon: 'book-open', path: '/classes' },
      { label: 'Điểm danh', icon: 'check-square', path: '/attendance' },
      { label: 'Lịch học', icon: 'calendar', path: '/calendar' },
    ],
  },
  {
    label: 'Tài chính & báo cáo',
    items: [
      { label: 'Tài chính', icon: 'credit-card', path: '/finance' },
      { label: 'Báo cáo', icon: 'bar-chart-2', path: '/reports' },
    ],
  },
  {
    label: 'Cổng truy cập',
    items: [
      { label: 'Cổng giáo viên', icon: 'briefcase', path: '/teacher' },
      { label: 'Cổng học viên', icon: 'smartphone', path: '/student' },
    ],
  },
  {
    label: 'Hệ thống',
    items: [{ label: 'Component Library', icon: 'layout', path: '/ui-kit' }],
  },
]

// Danh sách phẳng cho Command Palette.
export const NAV_ITEMS = NAV_SECTIONS.flatMap((s) => s.items)

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('./pages/Dashboard.vue') },
  { path: '/admissions', name: 'Admissions', component: () => import('./pages/Admissions.vue') },
  { path: '/students', name: 'Students', component: () => import('./pages/Students.vue') },
  { path: '/classes', name: 'Classes', component: () => import('./pages/Classes.vue') },
  { path: '/attendance', name: 'Attendance', component: () => import('./pages/Attendance.vue') },
  { path: '/calendar', name: 'Calendar', component: () => import('./pages/Calendar.vue') },
  { path: '/finance', name: 'Finance', component: () => import('./pages/Finance.vue') },
  { path: '/reports', name: 'Reports', component: () => import('./pages/Reports.vue') },
  { path: '/teacher', name: 'TeacherPortal', component: () => import('./pages/TeacherPortal.vue') },
  { path: '/student', name: 'StudentPortal', component: () => import('./pages/StudentPortal.vue') },
  { path: '/ui-kit', name: 'UiKit', component: () => import('./pages/UiKit.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/edu'),
  routes,
})

export default router
