<template>
  <label class="base-form-field" :class="`variant-${variant}`">
    <span v-if="label" class="field-label">{{ label }}</span>
    <slot />
  </label>
</template>

<script setup>
/* global defineProps */
defineProps({
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'panel'
  }
})
</script>

<style scoped>
.base-form-field {
  display: grid;
  gap: 8px;
}

.field-label {
  font-size: 12px;
  color: #6b7280;
}

.base-form-field.variant-auth .field-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #6c5f56;
}

.base-form-field :slotted(input),
.base-form-field :slotted(textarea) {
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.base-form-field.variant-panel :slotted(input),
.base-form-field.variant-panel :slotted(textarea) {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 11px 12px;
  font-size: 14px;
}

.base-form-field.variant-panel :slotted(input:focus),
.base-form-field.variant-panel :slotted(textarea:focus) {
  border-color: #d4b08c;
  box-shadow: 0 0 0 3px rgba(212, 176, 140, 0.14);
}

.base-form-field.variant-panel :slotted(textarea) {
  resize: vertical;
}

.base-form-field.variant-auth :slotted(input),
.base-form-field.variant-auth :slotted(textarea) {
  padding: 1rem 1.1rem;
  border-radius: 18px;
  border: 1px solid rgba(145, 106, 74, 0.12);
  background: rgba(255, 255, 255, 0.78);
}

.base-form-field.variant-auth :slotted(input:focus),
.base-form-field.variant-auth :slotted(textarea:focus) {
  border-color: rgba(171, 127, 91, 0.42);
  box-shadow: 0 0 0 4px rgba(212, 176, 140, 0.14);
}
</style>
