<template>
  <div class="sk-tile" :style="{ background: accent ? 'linear-gradient(135deg,#fdeef4,#fbe0ea)' : '#fff' }">
    <div class="sk-tile__label" :style="{ color: accent ? '#a8607b' : '#a98c98' }">{{ label }}</div>
    <div class="sk-tile__value tnum" :style="{ color: valueColor }">{{ value }}</div>
    <div v-if="note" class="sk-tile__note" :style="{ color: noteColor }">{{ note }}</div>
    <div v-if="progress != null" class="sk-tile__bar"><span :style="{ width: progress }" /></div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  note: String,
  valueColor: { type: String, default: '#3d2530' },
  noteColor: { type: String, default: '#a98c98' },
  accent: Boolean,
  progress: { type: String, default: null }, // '27%'
})
</script>

<style scoped>
.sk-tile { border: 1px solid #f3d9e1; border-radius: 12px; padding: 15px 16px; }
.sk-tile__label { font-size: 12px; font-weight: 500; }
.sk-tile__value { font-size: 25px; font-weight: 700; margin-top: 6px; }
.sk-tile__note { font-size: 11.5px; margin-top: 3px; }
.sk-tile__bar { height: 6px; border-radius: 4px; background: rgba(255, 255, 255, 0.6); margin-top: 9px; overflow: hidden; }
.sk-tile__bar > span { display: block; height: 100%; background: linear-gradient(90deg, #f7a8c4, #d6557e); border-radius: 4px; }
</style>
