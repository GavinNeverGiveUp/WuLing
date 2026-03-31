<template>
  <header class="mobile-topbar-shell" :class="{ sticky }">
    <div class="topbar-left">
      <slot name="leading" />
      <div class="title-block">
        <slot name="title">
          <h1>{{ title }}</h1>
          <p v-if="subtitle">{{ subtitle }}</p>
        </slot>
      </div>
    </div>

    <div v-if="$slots.actions" class="topbar-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  sticky: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.mobile-topbar-shell {
  position: relative;
  z-index: 26;
  overflow: visible;
  flex-shrink: 0;
  padding: max(12px, env(safe-area-inset-top)) 12px 10px;
  border-bottom: 1px solid #eceff3;
  background: rgba(255, 255, 255, 0.84);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mobile-topbar-shell.sticky {
  position: sticky;
  top: 0;
  z-index: 30;
}

.topbar-left,
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-left {
  min-width: 0;
  align-items: flex-start;
}

.title-block {
  min-width: 0;
}

.title-block :deep(h1) {
  margin: 0;
  font-size: 20px;
  line-height: 1.2;
  color: #111827;
}

.title-block :deep(p) {
  margin: 4px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

@media (max-width: 380px) {
  .mobile-topbar-shell {
    padding-left: 12px;
    padding-right: 12px;
  }

  .topbar-actions {
    gap: 8px;
  }
}
</style>
