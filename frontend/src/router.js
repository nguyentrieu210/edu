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
      { label: 'Lịch hẹn', icon: 'clock', path: '/appointments' },
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
    items: [
      { label: 'Quản lý tài khoản', icon: 'shield', path: '/accounts' },
      { label: 'Component Library', icon: 'layout', path: '/ui-kit' },
    ],
  },
]

// Danh sách phẳng cho Command Palette.
export const NAV_ITEMS = NAV_SECTIONS.flatMap((s) => s.items)

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('./pages/Dashboard.vue') },
  { path: '/admissions', name: 'Admissions', component: () => import('./pages/Admissions.vue') },
  { path: '/appointments', name: 'Appointments', component: () => import('./pages/Appointments.vue') },
  { path: '/students', name: 'Students', component: () => import('./pages/Students.vue') },
  { path: '/classes', name: 'Classes', component: () => import('./pages/Classes.vue') },
  { path: '/attendance', name: 'Attendance', component: () => import('./pages/Attendance.vue') },
  { path: '/calendar', name: 'Calendar', component: () => import('./pages/Calendar.vue') },
  { path: '/finance', name: 'Finance', component: () => import('./pages/Finance.vue') },
  { path: '/reports', name: 'Reports', component: () => import('./pages/Reports.vue') },
  { path: '/teacher', name: 'TeacherPortal', component: () => import('./pages/TeacherPortal.vue') },
  { path: '/student', name: 'StudentPortal', component: () => import('./pages/StudentPortal.vue') },
  { path: '/ui-kit', name: 'UiKit', component: () => import('./pages/UiKit.vue') },
  { path: '/accounts', name: 'Accounts', component: () => import('./pages/Accounts.vue') },
  { path: '/login', name: 'Login', component: () => import('./pages/Login.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

// ---- Phân quyền hiển thị theo vai trò ----
// Roles thật lấy từ whoami (boot của www-SPA không có sẵn). App.vue gọi setUserRoles sau khi load.
let _userRoles = []
export function setUserRoles(roles) { _userRoles = roles || [] }
function isPrivileged(roles) {
  return roles.includes('System Manager') || roles.includes('Academic Manager') || roles.includes('Administrator')
}
// Chỉ giới hạn khi BIẾT CHẮC là HV/GV thuần. Chưa biết role -> hiện đầy đủ (tránh mất sidebar).
function isPureStudent(roles) { return roles.includes('Student') && !roles.includes('Teacher') && !isPrivileged(roles) }
function isPureTeacher(roles) { return roles.includes('Teacher') && !roles.includes('Student') && !isPrivileged(roles) }

// Sidebar lọc theo vai trò: HV chỉ thấy cổng học viên, GV chỉ thấy cổng giáo viên.
export function navSectionsFor(roles) {
  const r = roles || []
  const allow = []
  if (isPureStudent(r)) allow.push('/student')
  if (isPureTeacher(r)) allow.push('/teacher')
  if (!allow.length) return NAV_SECTIONS // admin / role lạ / chưa xác định -> đầy đủ
  return NAV_SECTIONS
    .map((s) => ({ ...s, items: s.items.filter((it) => allow.includes(it.path)) }))
    .filter((s) => s.items.length)
}

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

// Giới hạn điều hướng: HV thuần -> /student, GV thuần -> /teacher; còn lại tự do.
// Dùng _userRoles (set sau whoami); chưa biết -> không chặn.
router.beforeEach((to) => {
  if (isPureStudent(_userRoles)) return to.path === '/student' ? true : '/student'
  if (isPureTeacher(_userRoles)) return to.path === '/teacher' ? true : '/teacher'
  return true
})

export default router
