<template>
  <aside class="app-sidebar">
    <div class="sidebar-top">
      <router-link class="home-button" to="/" aria-label="返回首页">
        <img
          class="icon-img icon-lg"
          src="https://api.iconify.design/solar/home-smile-bold-duotone.svg?color=%23D4B08C"
          alt=""
          aria-hidden="true"
        >
      </router-link>

      <nav class="sidebar-nav">
        <div class="nav-trigger">
          <router-link class="nav-icon" :class="{ active: activeNav === 'home' }" to="/home" aria-label="对话">
            <img class="icon-img" :src="getNavIcon('home')" alt="" aria-hidden="true">
          </router-link>
          <span class="nav-tooltip">对话</span>
        </div>

        <div class="nav-trigger">
          <router-link class="nav-icon" :class="{ active: activeNav === 'mgmt' }" to="/mgmt" aria-label="管理">
            <img class="icon-img" :src="getNavIcon('mgmt')" alt="" aria-hidden="true">
          </router-link>
          <span class="nav-tooltip">管理</span>
        </div>
      </nav>
    </div>

    <div class="sidebar-bottom">
      <div class="logout-trigger">
        <button class="logout-btn" type="button" aria-label="退出登录" @click="$emit('logout')">
          <img class="icon-img" src="https://api.iconify.design/solar/logout-2-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
        </button>
        <span class="logout-tooltip">退出登录</span>
      </div>

      <div class="settings-trigger">
        <router-link class="settings-btn" :class="{ active: settingsActive }" to="/settings" aria-label="设置" :aria-current="settingsActive ? 'page' : undefined">
          <img class="icon-img" :src="settingsActive ? settingsIconActive : settingsIconInactive" alt="" aria-hidden="true">
        </router-link>
        <span class="settings-tooltip">设置</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
/* global defineProps, defineEmits */
const props = defineProps({
  activeNav: {
    type: String,
    default: ''
  },
  settingsActive: {
    type: Boolean,
    default: false
  }
})

defineEmits(['logout'])

const homeIconActive = 'https://api.iconify.design/solar/chat-round-line-bold.svg?color=%23D4B08C'
const homeIconInactive = 'https://api.iconify.design/solar/chat-round-line-bold.svg?color=%239ca3af'
const mgmtIconActive = 'https://api.iconify.design/solar/box-minimalistic-bold.svg?color=%23D4B08C'
const mgmtIconInactive = 'https://api.iconify.design/solar/box-minimalistic-bold.svg?color=%239ca3af'
const settingsIconActive = 'https://api.iconify.design/solar/settings-bold.svg?color=%23D4B08C'
const settingsIconInactive = 'https://api.iconify.design/solar/settings-bold.svg?color=%239ca3af'

function getNavIcon(target) {
  if (target === 'home') {
    return props.activeNav === 'home' ? homeIconActive : homeIconInactive
  }

  return props.activeNav === 'mgmt' ? mgmtIconActive : mgmtIconInactive
}
</script>

<style scoped>
.app-sidebar {
  width: 80px;
  background: #ffffff;
  border-right: 1px solid #f3f4f6;
  padding: 32px 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 32px;
  align-items: center;
}

.home-button {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 176, 140, 0.1);
  margin-bottom: 40px;
  transition: transform 0.2s ease, box-shadow 0.22s ease, background-color 0.2s ease;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.nav-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon,
.settings-btn {
  border: 0;
  background: transparent;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.18s ease, background-color 0.2s ease, box-shadow 0.22s ease;
  text-decoration: none;
}

.nav-icon:hover,
.nav-icon.active,
.settings-btn:hover,
.settings-btn.active {
  background: rgba(212, 176, 140, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(212, 176, 140, 0.12);
}

.nav-tooltip,
.logout-tooltip,
.settings-tooltip {
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%) translateX(-8px);
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
  background: #ffffff;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
  color: #6b7280;
  font-size: 12px;
  line-height: 1;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease, filter 0.18s ease;
  z-index: 20;
  filter: blur(2px);
}

.nav-trigger:hover .nav-tooltip,
.logout-trigger:hover .logout-tooltip,
.settings-trigger:hover .settings-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
  filter: blur(0);
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
  padding-bottom: 4px;
}

.logout-trigger,
.settings-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn {
  border: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.18s ease, background-color 0.2s ease, box-shadow 0.22s ease;
}

.logout-btn:hover {
  background: rgba(212, 176, 140, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(212, 176, 140, 0.12);
}

.home-button:hover {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 12px 24px rgba(212, 176, 140, 0.18);
}

.home-button:active,
.nav-icon:active,
.settings-btn:active,
.logout-btn:active {
  transform: translateY(0) scale(0.98);
}

.icon-img {
  width: 22px;
  height: 22px;
  display: block;
}

.icon-lg {
  width: 28px;
  height: 28px;
}

.logout-btn .icon-img,
.settings-btn .icon-img {
  width: 20px;
  height: 20px;
}

@media (prefers-reduced-motion: reduce) {
  .home-button,
  .nav-icon,
  .settings-btn,
  .logout-btn,
  .nav-tooltip,
  .logout-tooltip,
  .settings-tooltip {
    transition: none;
  }
}

@media (min-width: 1024px) {
  .app-sidebar {
    width: 96px;
  }
}

@media (max-width: 1024px) {
  .app-sidebar {
    width: 72px;
  }
}

@media (max-width: 768px) {
  .app-sidebar {
    width: 100%;
    height: 74px;
    flex-direction: row;
    padding: 10px 14px;
    border-right: 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .sidebar-top {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    gap: 14px;
  }

  .home-button {
    width: 40px;
    height: 40px;
    margin-bottom: 0;
  }

  .sidebar-nav,
  .sidebar-bottom {
    flex-direction: row;
    gap: 8px;
  }

  .nav-tooltip,
  .logout-tooltip,
  .settings-tooltip {
    left: auto;
    right: 0;
    top: auto;
    bottom: calc(100% + 8px);
    transform: translateY(8px);
  }

  .nav-trigger:hover .nav-tooltip,
  .logout-trigger:hover .logout-tooltip,
  .settings-trigger:hover .settings-tooltip {
    transform: translateY(0);
  }
}
</style>
