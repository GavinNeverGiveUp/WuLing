<template>
  <div class="base-skeleton" :style="skeletonStyle"></div>
</template>

<script setup>
import { computed, defineProps } from 'vue'

const props = defineProps({
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '16px'
  },
  radius: {
    type: String,
    default: '10px'
  }
})

const skeletonStyle = computed(() => ({
  width: props.width,
  height: props.height,
  borderRadius: props.radius
}))
</script>

<style scoped>
.base-skeleton {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, #f3f4f6 0%, #ece7e1 48%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.35s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .base-skeleton {
    animation: none;
  }
}
</style>
