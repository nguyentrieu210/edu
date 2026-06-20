<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="sk-btn press"
    :class="[`sk-btn--${variant}`, `sk-btn--${size}`, { 'sk-btn--icon': icon, 'sk-btn--block': block }]"
  >
    <span v-if="loading" class="sk-spin sk-btn__spin" />
    <FeatherIcon v-else-if="leftIcon" :name="leftIcon" class="sk-btn__ic" />
    <slot />
  </button>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  variant: { type: String, default: 'solid' }, // solid | secondary | ghost | danger
  size: { type: String, default: 'md' },        // sm | md | lg
  type: { type: String, default: 'button' },
  loading: Boolean,
  disabled: Boolean,
  icon: Boolean,    // icon-only (vuông)
  block: Boolean,
  leftIcon: String, // tên FeatherIcon bên trái
})
</script>

<style scoped>
.sk-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  border: none; border-radius: 8px; cursor: pointer;
  font-family: inherit; font-weight: 600; white-space: nowrap;
  transition: filter 0.12s ease, background-color 0.12s ease, transform 0.12s ease;
}
.sk-btn:disabled { cursor: not-allowed; }
.sk-btn--block { width: 100%; }

/* sizes */
.sk-btn--sm { height: 30px; padding: 0 12px; font-size: 12px; border-radius: 7px; }
.sk-btn--md { height: 36px; padding: 0 16px; font-size: 13px; }
.sk-btn--lg { height: 40px; padding: 0 20px; font-size: 14px; border-radius: 9px; }
.sk-btn--icon.sk-btn--sm { width: 30px; padding: 0; }
.sk-btn--icon.sk-btn--md { width: 34px; height: 34px; padding: 0; border-radius: 8px; }
.sk-btn--icon.sk-btn--lg { width: 40px; padding: 0; }

/* variants */
.sk-btn--solid { color: #fff; background: linear-gradient(135deg, #e87aa3, #d4567f); box-shadow: 0 3px 9px rgba(212, 86, 127, 0.28); }
.sk-btn--solid:hover:not(:disabled) { filter: brightness(1.05); }
.sk-btn--secondary { color: #7a5c68; background: #fff; border: 1px solid #f0d3dd; font-weight: 500; }
.sk-btn--secondary:hover:not(:disabled) { background: #fdeef3; }
.sk-btn--ghost { color: #b8456a; background: transparent; font-weight: 500; }
.sk-btn--ghost:hover:not(:disabled) { background: #fbeef3; }
.sk-btn--danger { color: #c43232; background: #fdeeec; border: 1px solid #f3cdc9; }
.sk-btn--danger:hover:not(:disabled) { background: #fbe0dd; }

.sk-btn:disabled { color: #c9aab5; background: #f5e7ed; border: none; box-shadow: none; filter: none; }
.sk-btn--secondary:disabled, .sk-btn--ghost:disabled, .sk-btn--danger:disabled { color: #c9aab5; }

.sk-btn__ic { width: 15px; height: 15px; }
.sk-btn--lg .sk-btn__ic { width: 17px; height: 17px; }
.sk-btn__spin { width: 14px; height: 14px; border: 2px solid rgba(255, 255, 255, 0.5); border-top-color: #fff; border-radius: 50%; }
.sk-btn--secondary .sk-btn__spin, .sk-btn--ghost .sk-btn__spin { border-color: rgba(184, 69, 106, 0.35); border-top-color: #b8456a; }
</style>
