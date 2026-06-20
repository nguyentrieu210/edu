<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="isOpen" class="cmd-overlay" @click="close">
        <div class="cmd" @click.stop>
          <div class="cmd-search">
            <FeatherIcon name="search" style="width:18px;height:18px;color:#c08aa0;" />
            <input
              ref="inputRef"
              v-model="q"
              class="cmd-input"
              placeholder="Tìm trang, học viên, lớp, lệnh…"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="runActive"
            />
            <span class="cmd-esc">ESC</span>
          </div>

          <div class="cmd-list sk-scroll">
            <template v-if="filteredNav.length">
              <div class="cmd-group">Điều hướng</div>
              <button
                v-for="(it, i) in filteredNav"
                :key="it.path"
                class="cmd-item"
                :class="{ 'cmd-item--active': i === active }"
                @click="goTo(it.path)"
                @mouseenter="active = i"
              >
                <span class="cmd-ic"><FeatherIcon :name="it.icon" style="width:15px;height:15px;" /></span>
                <span class="cmd-label">{{ it.label }}</span>
              </button>
            </template>

            <template v-if="filteredCreate.length">
              <div class="cmd-group">Tạo mới</div>
              <button v-for="c in filteredCreate" :key="c.label" class="cmd-item" @click="close">
                <span class="cmd-ic"><FeatherIcon name="plus" style="width:15px;height:15px;" /></span>
                <span class="cmd-label">{{ c.label }}</span>
              </button>
            </template>

            <div v-if="!filteredNav.length && !filteredCreate.length" class="cmd-empty">
              Không có kết quả cho "{{ q }}"
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { NAV_ITEMS } from '../router'

const router = useRouter()
const isOpen = ref(false)
const q = ref('')
const active = ref(0)
const inputRef = ref(null)

const createItems = [
  { label: 'Tạo học viên mới' },
  { label: 'Tạo lớp học' },
  { label: 'Tạo hóa đơn' },
  { label: 'Đăng ký học viên vào lớp' },
]

const filteredNav = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return NAV_ITEMS
  return NAV_ITEMS.filter((i) => i.label.toLowerCase().includes(s))
})
const filteredCreate = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return createItems
  return createItems.filter((i) => i.label.toLowerCase().includes(s))
})

function open() {
  isOpen.value = true
  q.value = ''
  active.value = 0
  nextTick(() => inputRef.value?.focus())
}
function close() {
  isOpen.value = false
}
function toggle() {
  isOpen.value ? close() : open()
}
defineExpose({ open, close, toggle })

function move(d) {
  const n = filteredNav.value.length
  if (!n) return
  active.value = (active.value + d + n) % n
}
function runActive() {
  const it = filteredNav.value[active.value]
  if (it) goTo(it.path)
}
function goTo(path) {
  router.push(path)
  close()
}
</script>

<style scoped>
.cmd-overlay { position: fixed; inset: 0; z-index: 50; background: rgba(60, 20, 35, 0.32); backdrop-filter: blur(3px); display: flex; align-items: flex-start; justify-content: center; padding-top: 12vh; }
.cmd { width: 560px; max-width: 90%; background: #fffdfe; border-radius: 16px; box-shadow: 0 24px 60px rgba(80, 30, 50, 0.35); overflow: hidden; animation: skpop 0.2s ease; }
.cmd-search { display: flex; align-items: center; gap: 11px; padding: 16px 18px; border-bottom: 1px solid #f4dde5; }
.cmd-input { flex: 1; border: none; outline: none; font-family: inherit; font-size: 15px; color: #3d2530; background: none; }
.cmd-input::placeholder { color: #bd8d9c; }
.cmd-esc { font-size: 11px; color: #caa6b4; border: 1px solid #ecd0da; border-radius: 5px; padding: 2px 6px; }
.cmd-list { max-height: 50vh; overflow-y: auto; padding: 8px; }
.cmd-group { font-size: 10.5px; font-weight: 700; color: #c79aaa; letter-spacing: 0.6px; text-transform: uppercase; padding: 8px 12px 4px; }
.cmd-item { display: flex; align-items: center; gap: 11px; width: 100%; text-align: left; border: none; background: none; border-radius: 9px; padding: 9px 12px; cursor: pointer; font-family: inherit; color: #3d2530; }
.cmd-item:hover, .cmd-item--active { background: #fbeef3; }
.cmd-ic { width: 26px; height: 26px; border-radius: 7px; background: #fbeef3; display: flex; align-items: center; justify-content: center; color: #b8456a; flex: none; }
.cmd-label { font-size: 13.5px; font-weight: 500; }
.cmd-empty { padding: 24px; text-align: center; font-size: 13px; color: #a98c98; }
</style>
