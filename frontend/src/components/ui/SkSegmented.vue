<template>
  <div class="sk-seg">
    <button
      v-for="opt in normalized"
      :key="opt.value"
      class="sk-seg__btn"
      :class="{ 'sk-seg__btn--active': opt.value === modelValue }"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  options: { type: Array, required: true }, // ['A','B'] hoặc [{label,value}]
})
defineEmits(['update:modelValue'])

const normalized = computed(() =>
  props.options.map((o) => (typeof o === 'object' ? o : { label: o, value: o })),
)
</script>

<style scoped>
.sk-seg { display: inline-flex; background: #fbe6ee; border-radius: 8px; padding: 3px; gap: 2px; }
.sk-seg__btn {
  height: 28px; padding: 0 12px; border: none; border-radius: 6px; cursor: pointer;
  font-family: inherit; font-size: 12.5px; font-weight: 500;
  background: transparent; color: #a07c8a; transition: all 0.12s ease;
}
.sk-seg__btn--active { background: #fff; color: #b8456a; font-weight: 600; box-shadow: 0 1px 3px rgba(180, 80, 120, 0.18); }
</style>
