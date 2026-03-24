<template>
  <div class="dashboard-page">
    <aside class="sidebar">
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
          <button class="nav-icon active" type="button" aria-label="对话">
            <img class="icon-img" src="https://api.iconify.design/solar/chat-round-line-bold.svg?color=%23D4B08C" alt="" aria-hidden="true">
          </button>
          <!-- <button class="nav-icon" type="button" aria-label="物资">
            <img class="icon-img" src="https://api.iconify.design/solar/box-minimalistic-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
          </button>
          <button class="nav-icon" type="button" aria-label="定位">
            <img class="icon-img" src="https://api.iconify.design/solar/streets-navigation-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
          </button>
          <button class="nav-icon" type="button" aria-label="统计">
            <img class="icon-img" src="https://api.iconify.design/solar/pie-chart-2-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
          </button> -->
        </nav>
      </div>

      <div class="sidebar-bottom">
        <div class="logout-trigger">
          <button class="logout-btn" type="button" aria-label="退出登录" @click="handleLogout">
            <img class="icon-img" src="https://api.iconify.design/solar/logout-2-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
          </button>
          <span class="logout-tooltip">退出登录</span>
        </div>

        <div class="settings-trigger">
          <button class="settings-btn" type="button" aria-label="设置" @click="goToSettings">
            <img class="icon-img" src="https://api.iconify.design/solar/settings-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
          </button>
          <span class="settings-tooltip">设置</span>
        </div>
      </div>
    </aside>

    <main class="main-wrap">
      <header class="topbar">
        <div>
          <h1 class="hello-text">
            <span class="hello-muted">你好，</span>
            <span>{{ userDisplayName }}</span>
          </h1>
          <p class="date-text">今天是 {{ dateLabel }}</p>
        </div>

        <div class="topbar-right">
          <div class="expire-box">
            <span>{{ expiringCount }} 件物品需要关注</span>
            <small>含已过期及 3 天内到期物品</small>
          </div>

          <TopbarNoticePanel
            title="消息提醒"
            empty-text="暂无提醒消息"
            button-label="通知"
            :show-dot="hasNotifications"
            :groups="notificationGroups"
          >
            <template #item="{ item }">
              <div class="notice-item-main">
                <span class="notice-item-name">{{ item.title }}</span>
                <span v-if="item.tag" class="notice-item-tag" :class="{ danger: item.tagType === 'danger' }">{{ item.tag }}</span>
              </div>
              <p v-if="item.meta" class="notice-item-meta">{{ item.meta }}</p>
            </template>
          </TopbarNoticePanel>
        </div>
      </header>

      <section class="chat-section">
        <div ref="messagesHistory" class="chat-scroll">
          <div class="system-tip">已开启安全智能对话界面</div>

          <div
            v-for="entry in messages"
            :key="entry.id"
            class="message-line"
            :data-message-id="entry.id"
            :class="entry.role === 'user' ? 'line-user' : 'line-assistant'"
          >
            <div v-if="entry.role !== 'user'" class="bot-avatar">
              <img class="icon-img" src="https://api.iconify.design/solar/magic-stick-3-bold.svg?color=%23ffffff" alt="" aria-hidden="true">
            </div>

            <div class="bubble" :class="entry.role === 'user' ? 'bubble-user' : 'bubble-assistant'">
              <div v-if="entry.isLoading" class="bubble-loading" aria-live="polite">
                <span class="inline-spinner" aria-hidden="true"></span>
                <span class="bubble-loading-text">物灵正在思考中...</span>
              </div>
              <div v-else class="bubble-text" v-html="renderMessage(entry.text)"></div>
            </div>

            <div v-if="entry.role === 'user'" class="user-avatar">
              <img v-if="userAvatar" :src="userAvatar" alt="用户头像">
              <span v-else>{{ userInitial }}</span>
            </div>
          </div>
        </div>

        <div class="composer-area">
          <div class="composer-bar">
            <!-- <div class="composer-tools">
              <button type="button" aria-label="拍照">
                <img class="icon-img" src="https://api.iconify.design/solar/camera-bold.svg?color=%23D4B08C" alt="" aria-hidden="true">
              </button>
              <button type="button" aria-label="语音">
                <img class="icon-img" src="https://api.iconify.design/solar/microphone-large-bold.svg?color=%23D4B08C" alt="" aria-hidden="true">
              </button>
            </div>
            <div class="divider"></div> -->
            <textarea
              v-model="inputMessage"
              class="composer-input"
              placeholder="让物灵帮你找东西..."
              rows="1"
              @keydown="handleKeydown"
            ></textarea>
            <button class="send-btn" type="button" :disabled="isSending" :aria-busy="isSending" @click="sendMessage" aria-label="发送">
              <span v-if="isSending" class="inline-spinner inline-spinner-light btn-spinner" aria-hidden="true"></span>
              <img v-else class="icon-img" src="https://api.iconify.design/solar/plain-bold.svg?color=%23ffffff" alt="" aria-hidden="true">
            </button>
          </div>

          <div class="composer-hint">
            <span>
              <img class="icon-img" src="https://api.iconify.design/solar/check-circle-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
              物品位置实时同步
            </span>
            <span>
              <img class="icon-img" src="https://api.iconify.design/solar/shield-keyhole-bold.svg?color=%239ca3af" alt="" aria-hidden="true">
              端到端隐私加密保护
            </span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import request from '@/utils/request'
import TopbarNoticePanel from '@/components/TopbarNoticePanel.vue'

marked.setOptions({ breaks: true })

const router = useRouter()
const store = useStore()

function normalizeExpirationAlerts(payload) {
  return {
    expired_within_3_days: Array.isArray(payload?.expired_within_3_days) ? payload.expired_within_3_days : [],
    expiring_within_3_days: Array.isArray(payload?.expiring_within_3_days) ? payload.expiring_within_3_days : [],
    total_count: Number.isFinite(payload?.total_count) ? payload.total_count : 0
  }
}

const inputMessage = ref('')
const isSending = ref(false)
const messagesHistory = ref(null)
const expirationAlerts = ref(normalizeExpirationAlerts(store.state.expirationAlerts))
const invitationNotifications = ref([])

let messageIdSeed = 0

function createMessageId() {
  messageIdSeed += 1
  return `msg-${Date.now()}-${messageIdSeed}`
}

const defaultMessages = [
  {
    id: createMessageId(),
    role: 'assistant',
    text: '你好！我是物灵。随时准备好为你寻找、整理或提醒家庭物资。今天有什么可以帮你的？'
  }
]

const messages = ref([...defaultMessages])
const userDisplayName = computed(() => store.state.userInfo?.username || '苏先生')
const userInitial = computed(() => userDisplayName.value.slice(0, 1).toUpperCase())
const userAvatar = computed(() => store.state.userInfo?.avatar || '')

const dateLabel = computed(() => {
  const dateFormatter = new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
  const weekdayFormatter = new Intl.DateTimeFormat('zh-CN', {
    weekday: 'long'
  })

  const now = new Date()
  return `${dateFormatter.format(now)} · ${weekdayFormatter.format(now)}`
})

const expiringCount = computed(() => expirationAlerts.value.total_count)
const invitationCount = computed(() => invitationNotifications.value.length)

const notificationGroups = computed(() => {
  const expiredItems = expirationAlerts.value.expired_within_3_days.map((item) => ({
    id: `expired-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, true),
    tagType: 'danger',
    meta: `${item.location} · 到期于 ${formatDateTime(item.expiration_date)}`
  }))

  const expiringItems = expirationAlerts.value.expiring_within_3_days.map((item) => ({
    id: `expiring-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, false),
    meta: `${item.location} · 到期于 ${formatDateTime(item.expiration_date)}`
  }))

  const invitationItems = invitationNotifications.value.map((item, index) => ({
    id: item.id || `invitation-${index}`,
    title: item.title || '家庭邀请提醒',
    meta: item.meta || ''
  }))

  return [
    { key: 'expired', title: '已过期（3天内）', items: expiredItems },
    { key: 'expiring', title: '即将过期（3天内）', items: expiringItems },
    { key: 'invitation', title: '家庭邀请', items: invitationItems }
  ]
})

const hasNotifications = computed(() => (expiringCount.value + invitationCount.value) > 0)

watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

watch(
  () => store.state.expirationAlerts,
  (nextAlerts) => {
    expirationAlerts.value = normalizeExpirationAlerts(nextAlerts)
  },
  { deep: true }
)

onMounted(() => {
  if (store.state.token) {
    loadCurrentUser()
    loadHistoryMessages()
    loadExpirationAlerts()
    return
  }

  scrollToBottom()
})

async function loadCurrentUser() {
  try {
    const userInfoResponse = await request.get('/user/me')
    store.commit('SET_USER_INFO', userInfoResponse)

  } catch (error) {
    console.error('Failed to load user profile:', error)

  }
}

async function loadHistoryMessages() {
  try {
    const response = await request.get('/ai/messages', { params: { limit: 20 } })

    if (Array.isArray(response) && response.length > 0) {
      messages.value = response.map((item) => ({
        id: createMessageId(),
        role: item.role === 'user' ? 'user' : 'assistant',
        text: item.content
      }))
      return
    }

    messages.value = [...defaultMessages]
  } catch (error) {
    console.error('Failed to load history messages:', error)
    messages.value = [...defaultMessages]
  }
}

async function loadExpirationAlerts() {
  try {
    const response = await request.get('/item/items/expiration-alerts')
    const normalized = normalizeExpirationAlerts(response)
    expirationAlerts.value = normalized
    store.commit('SET_EXPIRATION_ALERTS', normalized)
  } catch (error) {
    console.error('Failed to load expiration alerts:', error)
    const fallback = normalizeExpirationAlerts(null)
    expirationAlerts.value = fallback
    store.commit('SET_EXPIRATION_ALERTS', fallback)
  }
}

function scrollToBottom() {
  const container = messagesHistory.value

  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

function scrollToMessageStart(messageId) {
  const container = messagesHistory.value

  if (!container || !messageId) {
    return
  }

  const target = container.querySelector(`[data-message-id="${messageId}"]`)

  if (!target) {
    scrollToBottom()
    return
  }

  const offset = 12
  const applyScroll = () => {
    const top = Math.max(target.offsetTop - offset, 0)
    container.scrollTop = top
  }

  applyScroll()
  requestAnimationFrame(applyScroll)
  setTimeout(applyScroll, 120)
}

function renderMessage(text) {
  return marked.parse(text || '')
}

function formatDateTime(value) {
  if (!value) {
    return '-'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function formatDaysOffset(daysOffset, isExpired) {
  const days = Math.abs(Number(daysOffset) || 0)

  if (isExpired) {
    return `已过期 ${days} 天`
  }

  if (days === 0) {
    return '今天到期'
  }

  return `${days} 天后到期`
}


function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

async function sendMessage() {
  const content = inputMessage.value.trim()

  if (!content || isSending.value) {
    return
  }

  const userMessage = {
    id: createMessageId(),
    role: 'user',
    text: content
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  isSending.value = true
  const loadingReply = {
    id: createMessageId(),
    role: 'assistant',
    text: '',
    isLoading: true
  }
  messages.value.push(loadingReply)

  try {
    const response = await request.post('/ai/chat', { message: content })
    loadingReply.isLoading = false
    loadingReply.text = response.message || '物灵已经收到你的问题，但暂时没有返回内容。'
    await nextTick()
    scrollToMessageStart(userMessage.id)
  } catch (error) {
    console.error('Failed to send message:', error)
    loadingReply.isLoading = false
    loadingReply.text = '抱歉，刚刚没有成功连上物灵服务。你可以稍后再试，或者换一种说法继续问我。'
    await nextTick()
    scrollToMessageStart(userMessage.id)
  } finally {
    isSending.value = false
  }
}

function handleLogout() {
  store.commit('CLEAR_TOKEN')
  router.push('/')
}

function goToSettings() {
  router.push('/settings')
}
</script>

<style scoped>
.dashboard-page {
  background: #fdfbf9;
  color: #374151;
  display: flex;
  height: 100vh;
  overflow: hidden;
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

.sidebar {
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
}

.nav-icon.active {
  background: rgba(212, 176, 140, 0.05);
}

.nav-icon:hover {
  background: rgba(212, 176, 140, 0.08);
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
  padding-bottom: 4px;
}

.logout-trigger {
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
  transition: background-color 0.2s ease;
}

.logout-btn:hover {
  background: rgba(212, 176, 140, 0.1);
}

.logout-btn .icon-img {
  width: 20px;
  height: 20px;
}

.logout-tooltip {
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

.logout-trigger:hover .logout-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.settings-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

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

.settings-btn:hover {
  background: rgba(212, 176, 140, 0.1);
}

.settings-btn .icon-img {
  width: 20px;
  height: 20px;
}

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

.settings-trigger:hover .settings-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
  height: 100%;
}

.topbar {
  position: relative;
  z-index: 25;
  overflow: visible;
  height: 80px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border-bottom: 1px solid #f3f4f6;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hello-text {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #111827;
}

.hello-muted {
  color: #9ca3af;
  font-weight: 400;
}

.date-text {
  margin: 4px 0 0;
  color: #9ca3af;
  font-size: 12px;
  line-height: 1.2;
}

.topbar-right {
  min-width: 140px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.expire-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-right: 16px;
}

.expire-box span {
  color: #d4b08c;
  font-size: 12px;
  font-weight: 700;
}

.expire-box small {
  color: #9ca3af;
  font-size: 10px;
}

.notice-item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.notice-item-name {
  color: #111827;
  font-size: 13px;
  font-weight: 700;
}

.notice-item-tag {
  color: #8f6746;
  background: rgba(212, 176, 140, 0.16);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  white-space: nowrap;
}

.notice-item-tag.danger {
  color: #b91c1c;
  background: rgba(248, 113, 113, 0.16);
}

.notice-item-meta {
  margin: 6px 0 0;
  color: #9ca3af;
  font-size: 11px;
}

.chat-section {
  flex: 1;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.chat-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 32px;
  padding-bottom: 128px;
}

.system-tip {
  width: fit-content;
  margin: 0 auto 24px;
  background: #f3f4f6;
  color: #9ca3af;
  font-size: 12px;
  padding: 6px 16px;
  border-radius: 999px;
}

.message-line {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.line-user {
  justify-content: flex-end;
}

.bot-avatar,
.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bot-avatar {
  background: #d4b08c;
  box-shadow: 0 10px 24px rgba(212, 176, 140, 0.22);
}

.user-avatar {
  background: #e5e7eb;
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bubble {
  width: fit-content;
  max-width: min(33.333vw, 100%);
  padding: 20px;
  border-radius: 16px;
  line-height: 1.7;
  font-size: 16px;
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}

.bubble-assistant {
  background: #ffffff;
  border: 1px solid #f3f4f6;
  border-top-left-radius: 0;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
  color: #374151;
}

.bubble-user {
  background: #d4b08c;
  color: #ffffff;
  border-top-right-radius: 0;
  box-shadow: 0 10px 24px rgba(212, 176, 140, 0.26);
}

.bubble-text :deep(*) {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.bubble-text :deep(p) {
  margin: 0;
}

.bubble-text :deep(p + p) {
  margin-top: 10px;
}

.bubble-loading {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.bubble-loading-text {
  color: #9ca3af;
  font-size: 14px;
}

.inline-spinner {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 2px solid rgba(212, 176, 140, 0.35);
  border-top-color: #d4b08c;
  animation: spin 0.8s linear infinite;
}

.inline-spinner-light {
  border-color: rgba(255, 255, 255, 0.38);
  border-top-color: #ffffff;
}

.btn-spinner {
  width: 18px;
  height: 18px;
}

.composer-area {
  position: absolute;
  inset-inline: 0;
  bottom: 40px;
  padding: 0 32px;
}

.composer-bar {
  max-width: 896px;
  margin: 0 auto;
  border-radius: 24px;
  border: 1px solid rgba(212, 176, 140, 0.2);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 40px rgba(17, 24, 39, 0.12);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.composer-tools {
  display: flex;
  gap: 2px;
  padding: 0 8px;
}

.composer-tools button {
  border: 0;
  background: transparent;
  padding: 8px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.composer-tools button:hover {
  background: rgba(212, 176, 140, 0.1);
}

.divider {
  width: 1px;
  height: 24px;
  background: #e5e7eb;
}

.composer-input {
  border: 0;
  background: transparent;
  resize: none;
  outline: none;
  flex: 1;
  min-height: 24px;
  max-height: 120px;
  margin-left: 0;
  padding: 16px 0;
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

.send-btn {
  width: 48px;
  height: 48px;
  border: 0;
  border-radius: 16px;
  background: #d4b08c;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(212, 176, 140, 0.3);
  transition: background-color 0.2s ease;
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  background: #c39d7a;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.composer-hint {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 24px;
}

.composer-hint span {
  color: #9ca3af;
  font-size: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.composer-hint .icon-img {
  width: 12px;
  height: 12px;
}

.chat-scroll::-webkit-scrollbar {
  width: 8px;
}

.chat-scroll::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.45);
  border-radius: 999px;
}

@media (min-width: 1024px) {
  .sidebar {
    width: 96px;
  }
}

@media (max-width: 1024px) {
  .sidebar {
    width: 72px;
  }

  .topbar {
    padding: 0 20px;
  }

  .chat-scroll {
    padding: 22px;
    padding-bottom: 128px;
  }

  .composer-area {
    padding: 0 20px;
  }

  .bubble {
    max-width: min(44vw, 100%);
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    flex-direction: column;
  }

  .sidebar {
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

  .logout-tooltip {
    left: auto;
    right: 0;
    top: auto;
    bottom: calc(100% + 8px);
    transform: translateY(8px);
  }

  .logout-trigger:hover .logout-tooltip {
    transform: translateY(0);
  }

  .settings-tooltip {
    left: auto;
    right: 0;
    top: auto;
    bottom: calc(100% + 8px);
    transform: translateY(8px);
  }

  .settings-trigger:hover .settings-tooltip {
    transform: translateY(0);
  }

  .topbar {
    height: auto;
    padding: 14px 16px;
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .topbar-right {
    width: 100%;
    justify-content: flex-end;
    min-width: 0;
  }

  .message-line {
    margin-bottom: 16px;
  }

  .bubble {
    max-width: min(80vw, 100%);
  }

  .composer-area {
    bottom: 20px;
    padding: 0 12px;
  }

  .composer-bar {
    padding: 8px 10px;
  }

  .composer-hint {
    flex-wrap: wrap;
    gap: 10px;
  }
}
</style>
