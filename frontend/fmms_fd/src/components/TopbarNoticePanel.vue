<template>
  <div ref="rootRef" class="topbar-notice-wrap">
    <button class="topbar-notice-btn" type="button" :aria-label="buttonLabel" @click.stop="togglePanel">
      <slot name="button-icon">
        <img class="notice-icon" src="https://api.iconify.design/solar/bell-linear.svg?color=%239ca3af" alt="" aria-hidden="true">
      </slot>
      <span v-if="showDot" class="topbar-notice-dot"></span>
    </button>

    <div v-if="isOpen" class="topbar-notice-panel">
      <h3>{{ title }}</h3>
      <p v-if="!hasContent" class="topbar-notice-empty">{{ emptyText }}</p>

      <template v-else>
        <div v-for="group in visibleGroups" :key="group.key" class="topbar-notice-group">
          <p class="topbar-notice-group-title">{{ group.title }}</p>
          <ul>
            <li v-for="item in group.items" :key="item.id || item.key || `${group.key}-${item.title}`">
              <slot name="item" :item="item">
                <div class="default-item-main">
                  <span class="default-item-title">{{ item.title }}</span>
                  <span v-if="item.tag" class="default-item-tag" :class="{ danger: item.tagType === 'danger' }">{{ item.tag }}</span>
                </div>
                <p v-if="item.meta" class="default-item-meta">{{ item.meta }}</p>
              </slot>
            </li>
          </ul>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
/* global defineProps */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '通知'
  },
  emptyText: {
    type: String,
    default: '暂无通知'
  },
  buttonLabel: {
    type: String,
    default: '通知'
  },
  showDot: {
    type: Boolean,
    default: false
  },
  groups: {
    type: Array,
    default: () => []
  }
})

const rootRef = ref(null)
const isOpen = ref(false)

const visibleGroups = computed(() => {
  if (!Array.isArray(props.groups)) {
    return []
  }

  return props.groups
    .map((group, index) => ({
      key: group?.key || `group-${index}`,
      title: group?.title || '提醒',
      items: Array.isArray(group?.items) ? group.items : []
    }))
    .filter((group) => group.items.length > 0)
})

const hasContent = computed(() => visibleGroups.value.length > 0)

function togglePanel() {
  isOpen.value = !isOpen.value
}

function handleClickOutside(event) {
  if (!isOpen.value) {
    return
  }

  const root = rootRef.value
  if (root && !root.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.topbar-notice-wrap {
  position: relative;
}

.topbar-notice-btn {
  position: relative;
  border: 0;
  background: transparent;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.topbar-notice-btn:hover {
  background: rgba(212, 176, 140, 0.1);
}

.notice-icon {
  width: 22px;
  height: 22px;
  display: block;
}

.topbar-notice-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #f87171;
  border: 2px solid #ffffff;
}

.topbar-notice-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: min(380px, 82vw);
  max-height: 360px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #eceff3;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.14);
  z-index: 60;
}

.topbar-notice-panel h3 {
  margin: 0;
  font-size: 14px;
  color: #111827;
}

.topbar-notice-empty {
  margin: 12px 0 4px;
  color: #9ca3af;
  font-size: 12px;
}

.topbar-notice-group + .topbar-notice-group {
  margin-top: 12px;
}

.topbar-notice-group-title {
  margin: 12px 0 8px;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
}

.topbar-notice-group ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.topbar-notice-group li {
  border: 1px solid #f2f4f7;
  border-radius: 10px;
  padding: 8px 10px;
  background: #fcfcfd;
}

.default-item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.default-item-title {
  color: #111827;
  font-size: 13px;
  font-weight: 700;
}

.default-item-tag {
  color: #8f6746;
  background: rgba(212, 176, 140, 0.16);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  white-space: nowrap;
}

.default-item-tag.danger {
  color: #b91c1c;
  background: rgba(248, 113, 113, 0.16);
}

.default-item-meta {
  margin: 6px 0 0;
  color: #9ca3af;
  font-size: 11px;
}
</style>
