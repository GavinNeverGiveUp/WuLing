const { request } = require('../../utils/request.js')

let messageIdSeed = 0

function createMessageId() {
  messageIdSeed += 1
  return `msg-${Date.now()}-${messageIdSeed}`
}

function normalizeExpirationAlerts(payload) {
  const source = payload || {}
  return {
    expired_within_3_days: Array.isArray(source.expired_within_3_days) ? source.expired_within_3_days : [],
    expiring_within_3_days: Array.isArray(source.expiring_within_3_days) ? source.expiring_within_3_days : [],
    total_count: Number.isFinite(source.total_count) ? source.total_count : 0
  }
}

function formatDateTime(value) {
  if (!value) {
    return '-'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  const hour = `${date.getHours()}`.padStart(2, '0')
  const minute = `${date.getMinutes()}`.padStart(2, '0')
  return `${month}/${day} ${hour}:${minute}`
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

function buildNotificationGroups(alerts, invitations) {
  const expiredItems = alerts.expired_within_3_days.map((item) => ({
    id: `expired-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, true),
    tagType: 'danger',
    meta: `${item.location || '-'} · 到期于 ${formatDateTime(item.expiration_date)}`
  }))

  const expiringItems = alerts.expiring_within_3_days.map((item) => ({
    id: `expiring-${item.id}`,
    title: item.name,
    tag: formatDaysOffset(item.days_offset, false),
    meta: `${item.location || '-'} · 到期于 ${formatDateTime(item.expiration_date)}`
  }))

  const invitationItems = invitations.map((item, index) => ({
    id: item.id || `invitation-${index}`,
    title: item.title || '家庭邀请提醒',
    meta: item.meta || ''
  }))

  return [
    { key: 'expired', title: '已过期（3天内）', items: expiredItems },
    { key: 'expiring', title: '即将过期（3天内）', items: expiringItems },
    { key: 'invitation', title: '家庭邀请', items: invitationItems }
  ]
}

function escapeHtml(raw) {
  return String(raw || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function markdownToRichText(text) {
  let html = escapeHtml(text)

  html = html.replace(/```([\s\S]*?)```/g, (_match, code) => {
    const rendered = String(code || '').replace(/\n/g, '<br/>')
    return `<pre style="background:#f3f4f6;border-radius:10rpx;padding:14rpx;line-height:1.5;overflow:auto;">${rendered}</pre>`
  })

  html = html.replace(/`([^`]+)`/g, '<code style="background:#f3f4f6;padding:2rpx 8rpx;border-radius:8rpx;font-family:monospace;">$1</code>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<div style="margin:6rpx 0;">• $1</div>')
  html = html.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<div style="margin:6rpx 0;">$1. $2</div>')

  html = html.replace(/\n/g, '<br/>')

  return `<div>${html}</div>`
}

function formatDateLabel() {
  const date = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const label = `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
  return `${label} · ${weekdays[date.getDay()]}`
}

function createMessage(role, text, isLoading) {
  return {
    id: createMessageId(),
    role,
    text,
    isLoading: Boolean(isLoading),
    richText: isLoading ? '' : markdownToRichText(text)
  }
}

Page({
  data: {
    messages: [createMessage('assistant', '你好！我是物灵。随时准备好为你寻找、整理或提醒家庭物资。今天有什么可以帮你的？')],
    inputText: '',
    sending: false,
    userInfo: {},
    userDisplayName: '苏先生',
    userInitial: '苏',
    dateLabel: '',
    scrollIntoView: '',

    expirationAlerts: normalizeExpirationAlerts(null),
    invitationNotifications: [],
    notificationGroups: [],
    hasNotifications: false,
    expiringCount: 0,
    showNoticePanel: false,

    statusBarHeight: 24,
    topSafeInset: 24,
    safeBottom: 0,
    composerBottom: 0,
    topbarHeight: 118,
    composerHeight: 112,
    chatTop: 118,
    chatBottom: 112
  },

  onLoad() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.reLaunch({ url: '/pages/login/login' })
      return
    }

    this.initSystemMetrics()
    this.refreshDateLabel()
    this.bootstrapPage()
  },

  onReady() {
    this.updateLayoutMetrics()
  },

  onShow() {
    this.refreshDateLabel()
    wx.nextTick(() => {
      this.updateLayoutMetrics()
    })
  },

  onPullDownRefresh() {
    this.bootstrapPage().finally(() => {
      wx.stopPullDownRefresh()
    })
  },

  onUnload() {
    if (this.measureTimer) {
      clearTimeout(this.measureTimer)
      this.measureTimer = null
    }
  },

  initSystemMetrics() {
    try {
      const sysInfo = wx.getSystemInfoSync()
      const safeArea = sysInfo.safeArea || null
      const safeBottom = safeArea ? Math.max(sysInfo.screenHeight - safeArea.bottom, 0) : 0
      const statusBarHeight = sysInfo.statusBarHeight || 24

      let topSafeInset = statusBarHeight
      if (typeof wx.getMenuButtonBoundingClientRect === 'function') {
        const menuButtonRect = wx.getMenuButtonBoundingClientRect()
        if (menuButtonRect && menuButtonRect.bottom) {
          topSafeInset = Math.max(statusBarHeight, Math.ceil(menuButtonRect.bottom + 6))
        }
      }

      this.setData({
        statusBarHeight,
        topSafeInset,
        safeBottom,
        composerBottom: safeBottom
      }, () => {
        this.syncChatBounds()
      })
    } catch (error) {
      console.error('读取设备信息失败:', error)
    }
  },

  refreshDateLabel() {
    this.setData({
      dateLabel: formatDateLabel()
    })
  },

  async bootstrapPage() {
    await this.loadCurrentUser()
    await Promise.all([
      this.loadHistoryMessages(),
      this.loadExpirationAlerts()
    ])
  },

  async loadCurrentUser() {
    try {
      const userInfoResponse = await request({
        url: '/user/me',
        method: 'GET'
      })

      wx.setStorageSync('userInfo', userInfoResponse)
      const username = (userInfoResponse && userInfoResponse.username) || '苏先生'
      this.setData({
        userInfo: userInfoResponse,
        userDisplayName: username,
        userInitial: username.slice(0, 1).toUpperCase()
      })
    } catch (error) {
      console.error('获取用户信息失败:', error)
      const cached = wx.getStorageSync('userInfo') || {}
      const username = (cached && cached.username) || '苏先生'
      this.setData({
        userInfo: cached,
        userDisplayName: username,
        userInitial: username.slice(0, 1).toUpperCase()
      })
    }
  },

  async loadHistoryMessages() {
    try {
      const response = await request({
        url: '/ai/messages?limit=20',
        method: 'GET'
      })

      if (Array.isArray(response) && response.length > 0) {
        const messages = response.map((item) => createMessage(item.role === 'user' ? 'user' : 'assistant', item.content || ''))
        this.setData({ messages }, () => {
          this.scrollToBottom()
        })
        return
      }

      const defaults = [createMessage('assistant', '你好！我是物灵。随时准备好为你寻找、整理或提醒家庭物资。今天有什么可以帮你的？')]
      this.setData({ messages: defaults }, () => {
        this.scrollToBottom()
      })
    } catch (error) {
      console.error('加载历史消息失败:', error)
      const defaults = [createMessage('assistant', '你好！我是物灵。随时准备好为你寻找、整理或提醒家庭物资。今天有什么可以帮你的？')]
      this.setData({ messages: defaults }, () => {
        this.scrollToBottom()
      })
    }
  },

  async loadExpirationAlerts() {
    try {
      const response = await request({
        url: '/item/items/expiration-alerts',
        method: 'GET'
      })
      const alerts = normalizeExpirationAlerts(response)
      this.applyNotificationState(alerts, this.data.invitationNotifications)
    } catch (error) {
      console.error('加载待关注事项失败:', error)
      const fallback = normalizeExpirationAlerts(null)
      this.applyNotificationState(fallback, this.data.invitationNotifications)
    }
  },

  applyNotificationState(alerts, invitations) {
    const groups = buildNotificationGroups(alerts, invitations)
    const hasNotifications = (alerts.total_count + invitations.length) > 0

    this.setData({
      expirationAlerts: alerts,
      invitationNotifications: invitations,
      notificationGroups: groups,
      hasNotifications,
      expiringCount: alerts.total_count
    })
  },

  toggleNoticePanel() {
    this.setData({
      showNoticePanel: !this.data.showNoticePanel
    })
  },

  closeNoticePanel() {
    if (!this.data.showNoticePanel) {
      return
    }

    this.setData({
      showNoticePanel: false
    })
  },

  noop() {
    return null
  },

  onInputChange(e) {
    this.setData({
      inputText: e.detail.value
    })
    this.scheduleMeasure()
  },

  onKeyboardHeightChange(e) {
    const detail = (e && e.detail) || {}
    const keyboardHeight = Math.max(Math.round(detail.height || 0), 0)
    const composerBottom = keyboardHeight > 0 ? keyboardHeight : this.data.safeBottom

    this.setData({
      composerBottom
    }, () => {
      this.syncChatBounds()
      this.scheduleMeasure()
      if (keyboardHeight > 0) {
        this.scrollToBottom()
      }
    })
  },

  scheduleMeasure() {
    if (this.measureTimer) {
      clearTimeout(this.measureTimer)
    }

    this.measureTimer = setTimeout(() => {
      this.updateLayoutMetrics()
    }, 60)
  },

  updateLayoutMetrics() {
    const query = this.createSelectorQuery()
    query.select('.mobile-topbar').boundingClientRect()
    query.select('.mobile-composer').boundingClientRect()
    query.exec((res) => {
      const topbarRect = Array.isArray(res) ? res[0] : null
      const composerRect = Array.isArray(res) ? res[1] : null

      const next = {}
      if (topbarRect && topbarRect.height) {
        next.topbarHeight = Math.ceil(topbarRect.height)
      }
      if (composerRect && composerRect.height) {
        next.composerHeight = Math.ceil(composerRect.height)
      }

      const hasUpdate = Object.keys(next).length > 0
      if (!hasUpdate) {
        return
      }

      this.setData(next, () => {
        this.syncChatBounds()
      })
    })
  },

  syncChatBounds() {
    const chatTop = this.data.topbarHeight
    const chatBottom = this.data.composerHeight + this.data.composerBottom

    this.setData({
      chatTop,
      chatBottom
    })
  },

  scrollToBottom() {
    this.scrollToAnchor('msg-bottom')
  },

  scrollToAnchor(anchorId) {
    this.setData({ scrollIntoView: '' })
    setTimeout(() => {
      this.setData({ scrollIntoView: anchorId })
    }, 50)
  },

  async handleSend() {
    const text = (this.data.inputText || '').trim()
    if (!text || this.data.sending) {
      return
    }

    const userMessage = createMessage('user', text)
    const loadingMessage = createMessage('assistant', '', true)
    const messages = [...this.data.messages, userMessage, loadingMessage]

    this.setData({
      inputText: '',
      sending: true,
      showNoticePanel: false,
      messages
    }, () => {
      this.scrollToBottom()
      this.scheduleMeasure()
    })

    try {
      const response = await request({
        url: '/ai/chat',
        method: 'POST',
        data: { message: text }
      })

      const replyText = (response && (response.message || response.response || response.content)) || '物灵已经收到你的问题，但暂时没有返回内容。'
      const nextMessages = this.data.messages.map((item) => {
        if (item.id !== loadingMessage.id) {
          return item
        }
        return {
          ...item,
          text: replyText,
          isLoading: false,
          richText: markdownToRichText(replyText)
        }
      })

      this.setData({
        messages: nextMessages,
        sending: false
      }, () => {
        this.scrollToAnchor(`msg-${userMessage.id}`)
      })
    } catch (error) {
      console.error('发送消息失败:', error)
      const fallbackText = '抱歉，刚刚没有成功连上物灵服务。你可以稍后再试，或者换一种说法继续问我。'
      const nextMessages = this.data.messages.map((item) => {
        if (item.id !== loadingMessage.id) {
          return item
        }
        return {
          ...item,
          text: fallbackText,
          isLoading: false,
          richText: markdownToRichText(fallbackText)
        }
      })

      this.setData({
        messages: nextMessages,
        sending: false
      }, () => {
        this.scrollToAnchor(`msg-${userMessage.id}`)
      })
    }
  },

  goToSettings() {
    wx.navigateTo({
      url: '/pages/profile/profile'
    })
  },

  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (!res.confirm) {
          return
        }

        wx.removeStorageSync('token')
        wx.removeStorageSync('userInfo')
        wx.showToast({
          title: '已退出登录',
          icon: 'success'
        })

        setTimeout(() => {
          wx.reLaunch({
            url: '/pages/login/login'
          })
        }, 800)
      }
    })
  }
})

