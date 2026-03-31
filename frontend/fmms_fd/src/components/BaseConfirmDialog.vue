<template>
  <BaseModal
    :model-value="modelValue"
    :title="title"
    :description="description"
    :width="width"
    :close-on-overlay="!loading"
    @update:modelValue="handleVisibleChange"
    @close="$emit('close')"
  >
    <div class="confirm-content">
      <slot>
        <p>{{ content }}</p>
      </slot>
    </div>

    <div class="confirm-actions">
      <button type="button" class="confirm-cancel" :disabled="loading" @click="handleCancel">{{ cancelText }}</button>
      <button
        type="button"
        class="confirm-submit"
        :class="{ danger }"
        :disabled="loading"
        @click="$emit('confirm')"
      >
        {{ loading ? loadingText : confirmText }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
/* global defineProps, defineEmits */
import BaseModal from './BaseModal.vue'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '请确认'
  },
  description: {
    type: String,
    default: ''
  },
  content: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '460px'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  loadingText: {
    type: String,
    default: '处理中...'
  },
  loading: {
    type: Boolean,
    default: false
  },
  danger: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'confirm'])

function handleVisibleChange(value) {
  emit('update:modelValue', value)
}

function handleCancel() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped>
.confirm-content {
  border-radius: 16px;
  border: 1px solid #f3f4f6;
  background: #fcfaf7;
  padding: 18px 16px;
  margin-bottom: 18px;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.7;
}

.confirm-content p {
  margin: 0;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.confirm-cancel,
.confirm-submit {
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 96px;
}

.confirm-cancel {
  border: 1px solid rgba(212, 176, 140, 0.35);
  background: #ffffff;
  color: #b1865b;
  padding: 8px 14px;
}

.confirm-cancel:hover {
  background: #fafafa;
  border-color: #d1d5db;
}

.confirm-submit {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
  padding: 8px 14px;
}

.confirm-submit:hover {
  background: #fafafa;
  border-color: #d1d5db;
}

.confirm-submit.danger {
  color: #dc2626;
  border-color: #fecaca;
  background: #fef2f2;
}

.confirm-submit:disabled,
.confirm-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .confirm-actions {
    flex-direction: column;
  }
}
</style>
