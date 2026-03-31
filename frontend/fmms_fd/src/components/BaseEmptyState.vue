<template>
  <div class="base-empty-state" :class="{ rich }">
    <slot>
      <span>{{ text }}</span>
    </slot>
  </div>
</template>

<script setup>
/* global defineProps */
defineProps({
  text: {
    type: String,
    default: ''
  },
  rich: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-empty-state {
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  color: #9ca3af;
  font-size: 13px;
  text-align: center;
  padding: 24px;
}

.base-empty-state.rich {
  display: grid;
  gap: 14px;
  justify-items: center;
}
</style>
