<template>
  <button
    class="base-button"
    :class="[`variant-${variant}`, { block }]"
    :type="nativeType"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup>
/* global defineProps, defineEmits */
defineProps({
  variant: {
    type: String,
    default: 'primary'
  },
  nativeType: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>

<style scoped>
.base-button {
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.base-button.block {
  width: 100%;
}

.base-button.variant-primary {
  border: 0;
  background: #d4b08c;
  color: #ffffff;
  padding: 9px 16px;
  font-weight: 600;
}

.base-button.variant-primary:hover {
  background: #c39d7a;
}

.base-button.variant-ghost {
  border: 1px solid rgba(212, 176, 140, 0.35);
  background: #ffffff;
  color: #b1865b;
  padding: 8px 14px;
}

.base-button.variant-ghost:hover,
.base-button.variant-text:hover {
  background: #fafafa;
  border-color: #d1d5db;
}

.base-button.variant-text {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
  padding: 6px 10px;
}

.base-button.variant-danger {
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #dc2626;
  padding: 6px 10px;
}

.base-button.variant-danger:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}

.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
