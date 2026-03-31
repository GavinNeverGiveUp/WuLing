<template>
  <div v-if="modelValue" class="base-modal-overlay" @click.self="handleOverlayClick">
    <section class="base-modal-card" :style="modalStyle" role="dialog" aria-modal="true">
      <div class="base-modal-head">
        <div>
          <h3>{{ title }}</h3>
          <p v-if="description">{{ description }}</p>
        </div>
        <button type="button" class="base-modal-close" @click="closeModal">{{ closeText }}</button>
      </div>

      <slot />
    </section>
  </div>
</template>

<script setup>
/* global defineProps, defineEmits */
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '720px'
  },
  closeText: {
    type: String,
    default: '关闭'
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const modalStyle = computed(() => ({
  width: `min(${props.width}, 100%)`
}))

function closeModal() {
  emit('update:modelValue', false)
  emit('close')
}

function handleOverlayClick() {
  if (!props.closeOnOverlay) {
    return
  }

  closeModal()
}
</script>

<style scoped>
.base-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}

.base-modal-card {
  max-height: calc(100vh - 40px);
  overflow: auto;
  background: #ffffff;
  border-radius: 24px;
  border: 1px solid #f3f4f6;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.2);
  padding: 22px;
}

.base-modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.base-modal-head h3 {
  margin: 0;
  font-size: 20px;
  color: #1f2937;
}

.base-modal-head p {
  margin: 8px 0 0;
  color: #9ca3af;
  font-size: 12px;
}

.base-modal-close {
  border: 1px solid rgba(212, 176, 140, 0.35);
  background: #ffffff;
  color: #b1865b;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.base-modal-close:hover {
  background: #fafafa;
  border-color: #d1d5db;
}

@media (max-width: 768px) {
  .base-modal-card {
    padding: 18px;
  }
}
</style>
