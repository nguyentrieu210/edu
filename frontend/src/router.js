import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./pages/Dashboard.vue'),
  },
  // Học viên & Thẻ
  {
    path: '/students',
    name: 'Students',
    component: () => import('./pages/Students.vue'),
  },
  {
    path: '/student-card',
    name: 'StudentCard',
    component: () => import('./pages/StudentCard.vue'),
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: () => import('./pages/Onboarding.vue'),
  },
  // Sale & Lead
  {
    path: '/leads',
    name: 'Leads',
    component: () => import('./pages/Leads.vue'),
  },
  {
    path: '/crm',
    name: 'CRMBoard',
    component: () => import('./pages/CRMBoard.vue'),
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: () => import('./pages/Appointments.vue'),
  },
  // Lớp & Đào tạo
  {
    path: '/teachers',
    name: 'Teachers',
    component: () => import('./pages/Teachers.vue'),
  },
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('./pages/Courses.vue'),
  },
  {
    path: '/classes',
    name: 'Classes',
    component: () => import('./pages/Classes.vue'),
  },
  {
    path: '/enrollments',
    name: 'Enrollments',
    component: () => import('./pages/Enrollments.vue'),
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('./pages/Attendance.vue'),
  },
  {
    path: '/assessments',
    name: 'Assessments',
    component: () => import('./pages/Assessments.vue'),
  },
  // Tài chính
  {
    path: '/invoices',
    name: 'Invoices',
    component: () => import('./pages/Invoices.vue'),
  },
  {
    path: '/payments',
    name: 'Payments',
    component: () => import('./pages/Payments.vue'),
  },
  // Vận hành
  {
    path: '/room-booking',
    name: 'RoomBooking',
    component: () => import('./pages/RoomBooking.vue'),
  },
  {
    path: '/task-board',
    name: 'TaskBoard',
    component: () => import('./pages/TaskBoard.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/education_app'),
  routes,
})

export default router
