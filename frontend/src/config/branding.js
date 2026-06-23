/**
 * White-label branding config — nguồn duy nhất cho tên, logo, màu, text.
 * Mỗi khách hàng có thể override thông qua window.__BRANDING__ khi deploy.
 */
const defaults = {
  // Tên & mô tả
  brandName: 'Kairo',
  brandSub: 'Education ERP',
  brandTagline: 'Hệ thống quản lý trung tâm giáo dục',

  // App title (hiển thị trên tab trình duyệt)
  appTitle: 'Kairo · Education ERP',

  // Footer copyright
  copyright: '© Kairo · Education ERP',

  // Hero tagline (landing page)
  heroEyebrow: 'Education ERP',
  heroTitle: 'Quản lý trung tâm giáo dục\nthông minh & trọn vẹn',
  heroDesc: 'Tuyển sinh, đào tạo, tài chính, cổng giáo viên – học viên và trợ lý AI — tất cả trong một nền tảng.',

  // Màu sắc chủ đạo (CSS custom properties sẽ được inject)
  colors: {
    primary: '#d6557e',
    primaryLight: '#f7a8c4',
    primaryDark: '#b8456a',
    primaryBg: '#fff7fa',
    gradient: 'linear-gradient(140deg, #f7a8c4, #d6557e)',
    gradientBg: 'linear-gradient(160deg, #fff7fa 0%, #fdeaf1 45%, #fbdfeb 100%)',
    textPrimary: '#4a2230',
    textSecondary: '#7a5c68',
    border: '#f3d3df',
  },

  // Logo (SVG inline — có thể override bằng URL)
  logoType: 'default', // 'default' | 'custom'
  logoSvg: null, // SVG string nếu logoType='custom'

  // Favicon
  favicon: '/assets/edu/frontend/favicon.ico',
}

// Merge với window.__BRANDING__ nếu có (inject từ backend khi deploy)
const win = typeof window !== 'undefined' ? window : {}
const merged = { ...defaults, ...(win.__BRANDING__ || {}) }
merged.colors = { ...defaults.colors, ...(win.__BRANDING__?.colors || {}) }

export default merged

/**
 * Logo SVG mặc định — hoa anh đào cách điệu (Sakura).
 * Có thể thay bằng window.__BRANDING__.logoSvg.
 */
export const DEFAULT_LOGO_SVG = `<svg width="26" height="26" viewBox="0 0 64 64">
  <g fill="#fff">
    <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(0 32 32)" />
    <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(72 32 32)" />
    <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(144 32 32)" />
    <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(216 32 32)" />
    <path d="M32 13 C28 18 28 26 32 30 C36 26 36 18 32 13Z" transform="rotate(288 32 32)" />
  </g>
  <circle cx="32" cy="32" r="4.4" fill="#ffd98e" />
</svg>`
