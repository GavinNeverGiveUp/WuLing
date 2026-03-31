<template>
  <div class="settings-page">
    <AppSidebar :settings-active="true" @logout="handleLogout" />

    <main class="settings-main">
      <header class="settings-header">
        <div>
          <h1>设置中心</h1>
          <p>管理账号信息与 API Key</p>
        </div>
        <router-link class="back-home" to="/home">返回对话</router-link>
      </header>

      <section class="settings-content">
        <BasePanel class="profile-panel" title="账号信息">
          <div class="profile-body">
            <div class="profile-avatar" aria-label="用户头像">
              <img v-if="userProfile.avatar" :src="userProfile.avatar" alt="用户头像">
              <span v-else>{{ userInitial }}</span>
            </div>

            <div class="profile-grid">
              <div>
                <label>用户名</label>
                <strong>{{ userProfile.username || '-' }}</strong>
              </div>
              <div>
                <label>邮箱</label>
                <strong>{{ userProfile.email || '-' }}</strong>
              </div>
              <div>
                <label>手机号</label>
                <strong>{{ userProfile.phone || '-' }}</strong>
              </div>
            </div>
          </div>
        </BasePanel>

        <BasePanel class="key-panel" title="API Key 管理">
          <template #extra>
            <span class="panel-tip">创建、查看与管理你的 Key</span>
          </template>
          <div class="create-row">
            <input
              v-model="newKeyName"
              type="text"
              maxlength="40"
              placeholder="输入 Key 名称，例如：智能家居助手"
            >
            <button type="button" :disabled="isCreatingKey" @click="createApiKey">{{ isCreatingKey ? '创建中...' : '创建 API Key' }}</button>
          </div>

          <div v-if="latestCreatedKey" class="latest-key">
            <p>新 Key 仅在此完整展示一次，请妥善保存：</p>
            <code>{{ latestCreatedKey }}</code>
            <button type="button" @click="copyKey(latestCreatedKey)">复制</button>
          </div>

          <BaseEmptyState v-if="isLoadingKeys" text="API Key 列表加载中..." />

          <BaseEmptyState v-else-if="apiKeys.length === 0" text="还没有 API Key，先创建一个吧。" />

          <ul v-else class="key-list">
            <li v-for="item in apiKeys" :key="item.id" class="key-item">
              <div class="key-main">
                <strong>{{ item.name }}</strong>
                <span>创建于 {{ formatDate(item.created_at) }}</span>
              </div>

              <div class="key-secret">
                <code>{{ item.key_preview }}</code>
              </div>

              <div class="key-meta">
                <span class="status-badge" :class="item.status === 'active' ? 'is-active' : 'is-revoked'">
                  {{ item.status === 'active' ? '生效中' : '已吊销' }}
                </span>
                <span class="last-used">最近使用：{{ formatDate(item.last_used_at) }}</span>
              </div>

              <div class="key-actions">
                <button type="button" class="danger" @click="removeKey(item.id)">吊销</button>
              </div>
            </li>
          </ul>
        </BasePanel>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import AppSidebar from '@/components/AppSidebar.vue'
import BaseEmptyState from '@/components/BaseEmptyState.vue'
import request from '@/utils/request'
import BasePanel from '@/components/BasePanel.vue'

const router = useRouter()
const store = useStore()

const userProfile = ref({
  id: '',
  username: '',
  email: '',
  phone: '',
  avatar: ''
})
const apiKeys = ref([])
const newKeyName = ref('')
const latestCreatedKey = ref('')
const isCreatingKey = ref(false)
const isLoadingKeys = ref(false)

const userInitial = computed(() => (userProfile.value.username || 'U').slice(0, 1).toUpperCase())

onMounted(() => {
  loadUserProfile()
  loadApiKeys()
})

async function loadUserProfile() {
  try {
    const me = await request.get('/user/me')
    const merged = {
      ...(store.state.userInfo || {}),
      ...(me || {})
    }

    store.commit('SET_USER_INFO', merged)
    userProfile.value = {
      id: merged.id || '',
      username: merged.username || '',
      email: merged.email || '',
      phone: merged.phone || '',
      avatar: merged.avatar || ''
    }
  } catch (error) {
    console.error('Failed to load user profile:', error)
    const fallback = store.state.userInfo || {}
    userProfile.value = {
      id: fallback.id || '',
      username: fallback.username || '',
      email: fallback.email || '',
      phone: fallback.phone || '',
      avatar: fallback.avatar || ''
    }
  }
}

async function loadApiKeys() {
  isLoadingKeys.value = true
  try {
    const response = await request.get('/user/api-keys')
    apiKeys.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to load api keys:', error)
    apiKeys.value = []
  } finally {
    isLoadingKeys.value = false
  }
}

async function createApiKey() {
  if (isCreatingKey.value) {
    return
  }

  isCreatingKey.value = true
  try {
    const name = newKeyName.value.trim()
    const created = await request.post('/user/api-keys', {
      name: name || undefined
    })

    latestCreatedKey.value = created?.api_key || ''
    newKeyName.value = ''
    message.success('API Key 创建成功')
    await loadApiKeys()
  } catch (error) {
    console.error('Failed to create api key:', error)
  } finally {
    isCreatingKey.value = false
  }
}

async function copyKey(value) {
  try {
    await navigator.clipboard.writeText(value)
    message.success('已复制到剪贴板')
  } catch (error) {
    console.error('Failed to copy key:', error)
    message.error('复制失败，请手动复制')
  }
}

async function removeKey(id) {
  try {
    await request.delete(`/user/api-keys/${id}`)
    message.success('API Key 已吊销')
    await loadApiKeys()
  } catch (error) {
    console.error('Failed to revoke api key:', error)
  }
}

function formatDate(isoString) {
  if (!isoString) {
    return '-'
  }

  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function handleLogout() {
  store.commit('CLEAR_TOKEN')
  router.push('/')
  message.success('已退出登录')
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  background: #fdfbf9;
  color: #374151;
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
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

.settings-sidebar {
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

.nav-icon {
  border: 0;
  background: transparent;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-decoration: none;
}

.nav-icon:hover {
  background: rgba(212, 176, 140, 0.08);
}

.nav-tooltip {
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
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 20;
}

.nav-trigger:hover .nav-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
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

.logout-btn,
.settings-btn {
  border: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.logout-btn:hover,
.settings-btn:hover,
.settings-btn.active {
  background: rgba(212, 176, 140, 0.1);
}

.logout-btn .icon-img,
.settings-btn .icon-img {
  width: 20px;
  height: 20px;
}

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
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 20;
}

.logout-trigger:hover .logout-tooltip,
.settings-trigger:hover .settings-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.settings-main {
  flex: 1;
  min-width: 0;
  padding: 28px 34px;
}

.settings-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.settings-header h1 {
  margin: 0;
  font-size: 28px;
  color: #1f2937;
}

.settings-header p {
  margin: 8px 0 0;
  color: #9ca3af;
  font-size: 13px;
}

.back-home {
  text-decoration: none;
  border-radius: 12px;
  border: 1px solid rgba(212, 176, 140, 0.35);
  color: #b1865b;
  padding: 10px 14px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.back-home:hover {
  background: rgba(212, 176, 140, 0.12);
}

.settings-content {
  display: grid;
  gap: 18px;
}

.panel-tip {
  font-size: 12px;
  color: #9ca3af;
}

.profile-body {
  display: flex;
  align-items: center;
  gap: 18px;
}

.profile-avatar {
  width: 74px;
  height: 74px;
  border-radius: 999px;
  border: 3px solid rgba(212, 176, 140, 0.24);
  overflow: hidden;
  background: #efe7df;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b1865b;
  font-size: 24px;
  font-weight: 700;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.profile-grid div {
  background: #fcfaf7;
  border: 1px solid #f3ece4;
  border-radius: 12px;
  padding: 10px 12px;
}

.profile-grid label {
  display: block;
  font-size: 12px;
  color: #9ca3af;
}

.profile-grid strong {
  display: block;
  margin-top: 6px;
  font-size: 14px;
  color: #374151;
  overflow-wrap: anywhere;
}

.create-row {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.create-row input {
  flex: 1;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
}

.create-row input:focus {
  border-color: #d4b08c;
  box-shadow: 0 0 0 3px rgba(212, 176, 140, 0.14);
}

.create-row button {
  border: 0;
  border-radius: 12px;
  padding: 0 18px;
  background: #d4b08c;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.create-row button:hover {
  background: #c39d7a;
}

.latest-key {
  border: 1px dashed rgba(212, 176, 140, 0.45);
  background: #fcf8f3;
  border-radius: 14px;
  padding: 12px;
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
}

.latest-key p {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.latest-key code {
  font-size: 13px;
  color: #8b6a4a;
  word-break: break-all;
}

.latest-key button {
  width: fit-content;
  border: 1px solid rgba(212, 176, 140, 0.4);
  background: #ffffff;
  color: #8b6a4a;
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
}

.key-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.key-item {
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  padding: 12px;
  background: #ffffff;
}

.key-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.key-main strong {
  font-size: 14px;
  color: #1f2937;
}

.key-main span {
  font-size: 12px;
  color: #9ca3af;
}

.key-secret {
  margin-top: 10px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 10px;
  padding: 8px 10px;
}

.key-secret code {
  font-size: 12px;
  color: #6b7280;
  word-break: break-all;
}

.key-meta {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.status-badge {
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.is-active {
  color: #15803d;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.status-badge.is-revoked {
  color: #9ca3af;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.last-used {
  font-size: 12px;
  color: #9ca3af;
}
.key-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.key-actions button {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 5px 10px;
  background: #ffffff;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
}

.key-actions button:hover {
  border-color: #d1d5db;
  background: #fafafa;
}

.key-actions .danger {
  color: #dc2626;
  border-color: #fecaca;
  background: #fef2f2;
}

@media (min-width: 1024px) {
  .settings-sidebar {
    width: 96px;
  }
}

@media (max-width: 1024px) {
  .settings-sidebar {
    width: 72px;
  }

  .settings-main {
    padding: 20px;
  }

  .profile-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .settings-page {
    flex-direction: column;
  }

  .settings-sidebar {
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

  .settings-header {
    flex-direction: column;
    gap: 10px;
  }

  .profile-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-grid {
    width: 100%;
    grid-template-columns: 1fr;
  }

  .create-row {
    flex-direction: column;
  }

  .key-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .key-meta {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.status-badge {
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.is-active {
  color: #15803d;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.status-badge.is-revoked {
  color: #9ca3af;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.last-used {
  font-size: 12px;
  color: #9ca3af;
}
.key-actions {
    flex-wrap: wrap;
  }
}
</style>

