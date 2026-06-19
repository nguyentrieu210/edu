import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { FrappeUI, Button, Badge, FeatherIcon, LoadingIndicator, setConfig, frappeRequest } from 'frappe-ui'

// Read CSRF token from cookie
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? match[2] : ''
}
window.csrf_token = window.csrf_token || getCookie('csrf_token') || getCookie('sid')

const pinia = createPinia()
const app = createApp(App)

setConfig('resourceFetcher', (options) => {
  return frappeRequest({
    ...options,
    method: options.method || 'GET',
  })
})

app.use(FrappeUI)
app.use(pinia)
app.use(router)

app.component('Button', Button)
app.component('Badge', Badge)
app.component('FeatherIcon', FeatherIcon)
app.component('LoadingIndicator', LoadingIndicator)

// Fetch accurate CSRF token to fix CSRFTokenError in dev and prod
fetch('/api/method/education_erp.education_erp.api.get_csrf_token', { credentials: 'include' })
  .then(res => res.json())
  .then(data => {
    if (data && data.message) {
      window.csrf_token = data.message;
    }
  })
  .catch(err => console.error("Could not fetch CSRF token", err))
  .finally(() => {
    app.mount('#app');
  })
