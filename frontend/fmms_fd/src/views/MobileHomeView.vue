<template>
  <div ref="mobileRootRef" class="mobile-chat-page">
    <MobileTopbar>
      <template #title>
        <h1 class="hello-text">
          <span class="hello-muted">你好，</span>
          <span>{{ userDisplayName }}</span>
        </h1>
        <p class="date-text">今天是 {{ dateLabel }}</p>
      </template>

      <template #actions>
        <TopbarNoticePanel
          class="mobile-notice-trigger"
          title="待关注事项"
          empty-text="暂无待关注事项"
          button-label="待关注事项"
          :show-dot="hasNotifications"
          :groups="notificationGroups"
        >
          <template #button-icon>
            <span class="expire-pill-btn">{{ expiringCount }} 件需关注</span>
          </template>

          <template #item="{ item }">
            <div class="notice-item-main">
              <span class="notice-item-name">{{ item.title }}</span>
              <span v-if="item.tag" class="notice-item-tag" :class="{ danger: item.tagType === 'danger' }">{{ item.tag }}</span>
            </div>
            <p v-if="item.meta" class="notice-item-meta">{{ item.meta }}</p>
          </template>
        </TopbarNoticePanel>

        <button class="icon-btn" type="button" aria-label="管理" @click="goToMgmt">
          <img class="icon-img" src="https://api.iconify.design/solar/box-minimalistic-bold.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
        <button class="icon-btn" type="button" aria-label="设置" @click="goToSettings">
          <img class="icon-img" src="https://api.iconify.design/solar/settings-bold.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
        <button class="icon-btn" type="button" aria-label="退出登录" @click="handleLogout">
          <img class="icon-img" src="https://api.iconify.design/solar/logout-2-bold.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
      </template>
    </MobileTopbar>

    <main ref="messagesHistory" class="messages-scroll" aria-live="polite">
      <div class="system-tip">已开启安全智能对话界面</div>

      <article
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
      </article>
    </main>

    <footer ref="composerRef" class="mobile-composer">
      <div class="composer-shell">
        <textarea
          ref="composerInputRef"
          v-model="inputMessage"
          class="composer-input"
          placeholder="让物灵帮你找东西..."
          rows="1"
          @input="handleInput"
          @keydown="handleKeydown"
        ></textarea>

        <button class="send-btn" type="button" :disabled="isSending" :aria-busy="isSending" @click="sendMessage" aria-label="发送">
          <span v-if="isSending" class="inline-spinner inline-spinner-light" aria-hidden="true"></span>
          <img v-else class="icon-img" src="https://api.iconify.design/solar/plain-bold.svg?color=%23ffffff" alt="" aria-hidden="true">
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import request from '@/utils/request'
import MobileTopbar from '@/components/MobileTopbar.vue'
import TopbarNoticePanel from '@/components/TopbarNoticePanel.vue'

marked.setOptions({ breaks: true })

const router = useRouter()
const store = useStore()

const messagesHistory = ref(null)
const mobileRootRef = ref(null)
const composerRef = ref(null)
const composerInputRef = ref(null)
const inputMessage = ref('')
const isSending = ref(false)
const expirationAlerts = ref(normalizeExpirationAlerts(store.state.expirationAlerts))
const invitationNotifications = ref([])

let messageIdSeed = 0
let composerResizeObserver = null
let frameId = 0

function normalizeExpirationAlerts(payload) {
  return {
    expired_within_3_days: Array.isArray(payload?.expired_within_3_days) ? payload.expired_within_3_days : [],
    expiring_within_3_days: Array.isArray(payload?.expiring_within_3_days) ? payload.expiring_within_3_days : [],
    total_count: Number.isFinite(payload?.total_count) ? payload.total_count : 0
  }
}

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
const expiringCount = computed(() => expirationAlerts.value.total_count)
const invitationCount = computed(() => invitationNotifications.value.length)
const hasNotifications = computed(() => (expiringCount.value + invitationCount.value) > 0)

const notificationGroups = computed(() => {
  const expiredItems = expirationAlerts.value.expired_within_3_days.map((item) => ({
    id: `expired-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, true),
    tagType: 'danger',
    meta: `${item.location || '-'} · 到期于 ${formatDateTime(item.expiration_date)}`
  }))

  const expiringItems = expirationAlerts.value.expiring_within_3_days.map((item) => ({
    id: `expiring-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, false),
    meta: `${item.location || '-'} · 到期于 ${formatDateTime(item.expiration_date)}`
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

watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      scrollToBottom()
      syncViewportVars()
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
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', syncViewportVars)
    window.addEventListener('orientationchange', syncViewportVars)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', syncViewportVars)
      window.visualViewport.addEventListener('scroll', syncViewportVars)
    }
  }

  if (typeof ResizeObserver !== 'undefined' && composerRef.value) {
    composerResizeObserver = new ResizeObserver(() => {
      syncViewportVars()
    })
    composerResizeObserver.observe(composerRef.value)
  }

  nextTick(() => {
    syncViewportVars()
    autoResizeInput()
  })

  if (store.state.token) {
    loadCurrentUser()
    loadHistoryMessages()
    loadExpirationAlerts()
    return
  }

  scrollToBottom()
})

onBeforeUnmount(() => {
  if (frameId) {
    cancelAnimationFrame(frameId)
    frameId = 0
  }

  if (composerResizeObserver) {
    composerResizeObserver.disconnect()
    composerResizeObserver = null
  }

  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', syncViewportVars)
    window.removeEventListener('orientationchange', syncViewportVars)
    if (window.visualViewport) {
      window.visualViewport.removeEventListener('resize', syncViewportVars)
      window.visualViewport.removeEventListener('scroll', syncViewportVars)
    }
  }
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

function syncViewportVars() {
  if (frameId) {
    cancelAnimationFrame(frameId)
  }

  frameId = requestAnimationFrame(() => {
    frameId = 0

    const root = mobileRootRef.value
    const composer = composerRef.value
    if (!root || !composer) {
      return
    }

    const vv = typeof window !== 'undefined' ? window.visualViewport : null
    const windowHeight = window.innerHeight || 0
    const visualHeight = vv ? vv.height : windowHeight
    const visualOffsetTop = vv ? vv.offsetTop : 0
    const bottomOffset = Math.max(Math.round(windowHeight - (visualHeight + visualOffsetTop)), 0)

    root.style.setProperty('--composer-height', `${Math.ceil(composer.offsetHeight || 0)}px`)
    root.style.setProperty('--vv-bottom-offset', `${bottomOffset}px`)
    root.style.setProperty('--app-height', `${Math.round(visualHeight || windowHeight)}px`)
  })
}

function autoResizeInput() {
  const input = composerInputRef.value
  if (!input) {
    return
  }

  input.style.height = 'auto'
  const height = Math.min(input.scrollHeight, 140)
  input.style.height = `${height}px`
  syncViewportVars()
}

function handleInput() {
  autoResizeInput()
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

  const offset = 10
  const applyScroll = () => {
    const top = Math.max(target.offsetTop - offset, 0)
    container.scrollTop = top
  }

  applyScroll()
  requestAnimationFrame(applyScroll)
  setTimeout(applyScroll, 140)
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
  autoResizeInput()
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

function goToMgmt() {
  router.push('/m/mgmt')
}
</script>

<style scoped>
.mobile-chat-page {
  --composer-height: 96px;
  --vv-bottom-offset: 0px;
  --app-height: 100dvh;
  --notice-panel-top: calc(env(safe-area-inset-top, 0px) + 78px);
  background: radial-gradient(circle at 12% 0%, #f8f2eb 0%, #f7f5f2 36%, #f4f4f5 100%);
  color: #374151;
  position: fixed;
  inset: 0;
  height: 100vh;
  height: 100dvh;
  height: var(--app-height);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.hello-text {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
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
  line-height: 1.25;
}

.expire-pill-btn {
  color: #8f6746;
  background: rgba(212, 176, 140, 0.16);
  border: 1px solid rgba(212, 176, 140, 0.32);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  padding: 8px 10px;
  white-space: nowrap;
}

.mobile-notice-trigger :deep(.topbar-notice-btn) {
  padding: 0;
  border-radius: 999px;
  background: transparent;
}

.mobile-notice-trigger :deep(.topbar-notice-btn:hover) {
  background: transparent;
}

.mobile-notice-trigger :deep(.topbar-notice-dot) {
  top: -2px;
  right: -2px;
}

.mobile-notice-trigger :deep(.topbar-notice-panel) {
  position: fixed;
  top: var(--notice-panel-top);
  left: 10px;
  right: 10px;
  width: auto;
  max-width: none;
  max-height: min(56vh, 420px);
}

.icon-btn {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 11px;
  background: #ffffff;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-img {
  width: 20px;
  height: 20px;
  display: block;
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

.messages-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding: 14px 12px;
  padding-bottom: calc(var(--composer-height) + var(--vv-bottom-offset) + env(safe-area-inset-bottom, 0px) + 14px);
}

.system-tip {
  width: fit-content;
  margin: 0 auto 14px;
  background: #ebeef3;
  color: #808995;
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 999px;
}

.message-line {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 14px;
}

.line-user {
  justify-content: flex-end;
}

.bot-avatar,
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 11px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bot-avatar {
  background: #d4b08c;
  box-shadow: 0 8px 18px rgba(212, 176, 140, 0.22);
}

.user-avatar {
  background: #e5e7eb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bubble {
  width: fit-content;
  max-width: min(82vw, 100%);
  border-radius: 14px;
  line-height: 1.62;
  font-size: 16px;
  padding: 12px 14px;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.bubble-assistant {
  background: #ffffff;
  border: 1px solid #e9edf2;
  border-top-left-radius: 4px;
  color: #374151;
  box-shadow: 0 8px 16px rgba(15, 23, 42, 0.04);
}

.bubble-user {
  background: linear-gradient(135deg, #d4b08c 0%, #c59a72 100%);
  color: #ffffff;
  border-top-right-radius: 4px;
  box-shadow: 0 10px 20px rgba(212, 176, 140, 0.24);
}

.bubble-text :deep(*) {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.bubble-text :deep(p) {
  margin: 0;
}

.bubble-text :deep(p + p) {
  margin-top: 8px;
}

.bubble-loading {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.bubble-loading-text {
  color: #9ca3af;
  font-size: 13px;
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
  border-color: rgba(255, 255, 255, 0.35);
  border-top-color: #ffffff;
}

.mobile-composer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: calc(var(--vv-bottom-offset) + env(safe-area-inset-bottom, 0px));
  padding: 8px 10px 10px;
  z-index: 30;
}

.composer-shell {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.14);
}

.composer-input {
  flex: 1;
  border: 0;
  outline: none;
  resize: none;
  overflow-y: auto;
  max-height: 140px;
  min-height: 40px;
  font-size: 16px;
  line-height: 1.45;
  color: #374151;
  background: transparent;
  padding: 10px 6px 8px;
}

.send-btn {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 13px;
  background: #d4b08c;
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(212, 176, 140, 0.24);
  flex-shrink: 0;
}

.send-btn:disabled {
  opacity: 0.65;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 380px) {
  .mobile-chat-page {
    --notice-panel-top: calc(env(safe-area-inset-top, 0px) + 72px);
  }

  .expire-pill-btn {
    font-size: 10px;
    padding: 7px 8px;
  }

  .messages-scroll {
    padding: 12px 10px;
  }
}
</style>
