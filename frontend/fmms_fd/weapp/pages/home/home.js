const { request } = require('../../utils/request.js')

function markdownToRichText(text) {
  let html = text
  
  html = html.replace(/`([^`]+)`/g, '<code style="background-color: #f5f5f5; padding: 4rpx 8rpx; border-radius: 8rpx; font-family: monospace;">$1</code>')
  
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  
  html = html.replace(/^### (.+)$/gm, '<h3 style="font-size: 32rpx; font-weight: bold; margin: 20rpx 0;">$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2 style="font-size: 36rpx; font-weight: bold; margin: 24rpx 0;">$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1 style="font-size: 40rpx; font-weight: bold; margin: 28rpx 0;">$1</h1>')
  
  html = html.replace(/^- (.+)$/gm, '<div style="margin: 8rpx 0; padding-left: 20rpx;">• $1</div>')
  
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color: #1890ff;">$1</a>')
  
  html = html.replace(/\n/g, '<br/>')
  
  return html
}

Page({
  data: {
    messages: [],
    inputText: '',
    sending: false,
    showUserMenu: false,
    userInfo: {},
    firstChar: '',
    scrollIntoView: ''
  },

  onLoad() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }

    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      const firstChar = userInfo.username ? userInfo.username.charAt(0) : 'U'
      this.setData({ 
        userInfo,
        firstChar: firstChar.toUpperCase()
      })
    }

    this.loadHistoryMessages()
  },

  async loadHistoryMessages() {
    try {
      const res = await request({
        url: '/ai/messages?limit=20',
        method: 'GET'
      })

      if (res && res.length > 0) {
        const messages = res.map(item => ({
          role: item.role,
          content: item.content,
          richText: markdownToRichText(item.content)
        }))
        this.setData({ messages })
        this.scrollToBottom()
      } else {
        this.setData({
          messages: [{
            role: 'assistant',
            content: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？',
            richText: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？'
          }]
        })
      }
    } catch (error) {
      console.error('加载历史消息失败:', error)
      this.setData({
        messages: [{
          role: 'assistant',
          content: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？',
          richText: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？'
        }]
      })
    }
  },

  onInputChange(e) {
    this.setData({
      inputText: e.detail.value
    })
  },

  async handleSend() {
    const { inputText, messages, sending } = this.data
    
    if (sending) {
      return
    }
    
    if (!inputText.trim()) {
      wx.showToast({
        title: '请输入消息',
        icon: 'none'
      })
      return
    }

    const userMessage = {
      role: 'user',
      content: inputText,
      richText: inputText
    }

    const newMessages = [...messages, userMessage]
    this.setData({
      messages: newMessages,
      inputText: '',
      sending: true
    })
    
    setTimeout(() => {
      this.setData({
        scrollIntoView: 'msg-typing'
      })
    }, 100)

    try {
      const res = await request({
        url: '/ai/chat',
        method: 'POST',
        data: {
          message: inputText
        }
      })

      const aiMessage = {
        role: 'assistant',
        content: res.response || res.message || res.content || JSON.stringify(res),
        richText: markdownToRichText(res.response || res.message || res.content || JSON.stringify(res))
      }

      const updatedMessages = [...this.data.messages, aiMessage]
      const aiMsgIndex = updatedMessages.length - 1
      
      this.setData({
        messages: updatedMessages,
        sending: false
      })
      
      setTimeout(() => {
        this.setData({
          scrollIntoView: `msg-${aiMsgIndex}`
        })
      }, 100)
    } catch (error) {
      console.error('发送消息失败:', error)
      const errorMessage = {
        role: 'assistant',
        content: '抱歉，发送失败，请稍后重试',
        richText: '抱歉，发送失败，请稍后重试'
      }
      
      const updatedMessages = [...this.data.messages, errorMessage]
      const aiMsgIndex = updatedMessages.length - 1
      
      this.setData({
        messages: updatedMessages,
        sending: false
      })
      
      setTimeout(() => {
        this.setData({
          scrollIntoView: `msg-${aiMsgIndex}`
        })
      }, 100)
    }
  },

  scrollToBottom() {
    const len = this.data.messages.length
    this.setData({
      scrollIntoView: `msg-${len}`
    })
  },

  goToProfile() {
    wx.navigateTo({
      url: '/pages/profile/profile'
    })
  }
})
