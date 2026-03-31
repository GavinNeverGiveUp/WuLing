<template>
  <section class="base-panel" :class="{ 'header-center': headerCenter }">
    <div v-if="hasHeader" class="base-panel-head">
      <div class="base-panel-copy">
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
        <slot name="title" />
      </div>
      <div v-if="$slots.extra" class="base-panel-extra">
        <slot name="extra" />
      </div>
    </div>

    <slot />
  </section>
</template>

<script setup>
/* global defineProps */
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  headerCenter: {
    type: Boolean,
    default: false
  }
})

const slots = useSlots()
const hasHeader = computed(() => Boolean(props.title || props.description || slots.title || slots.extra))
</script>

<style scoped>
.base-panel {
  background: #ffffff;
  border: 1px solid #f3f4f6;
  border-radius: 20px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
  padding: 22px;
}

.base-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.base-panel.header-center .base-panel-head {
  align-items: center;
}

.base-panel-copy h2 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.base-panel-copy p {
  margin: 8px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.base-panel-extra {
  flex-shrink: 0;
}
</style>
