const { request } = require('../../utils/request.js')

Page({
  data: {
    username: '',
    email: '',
    phone: '',
    password: '',
    agreed: false,
    loading: false,
    statusBarHeight: 24
  },

  onLoad() {
    this.initSystemMetrics()
  },

  initSystemMetrics() {
    try {
      const sysInfo = wx.getSystemInfoSync()
      this.setData({
        statusBarHeight: sysInfo.statusBarHeight || 24
      })
    } catch (error) {
      console.error('获取设备信息失败:', error)
    }
  },

  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    })
  },

  onEmailInput(e) {
    this.setData({
      email: e.detail.value
    })
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    })
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  toggleAgreement() {
    this.setData({
      agreed: !this.data.agreed
    })
  },

  async handleRegister() {
    const username = (this.data.username || '').trim()
    const email = (this.data.email || '').trim()
    const phone = (this.data.phone || '').trim()
    const password = this.data.password || ''

    if (!username || !email || !phone || !password) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      })
      return
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      wx.showToast({
        title: '请输入正确的邮箱格式',
        icon: 'none'
      })
      return
    }

    if (password.length < 8) {
      wx.showToast({
        title: '密码至少 8 位字符',
        icon: 'none'
      })
      return
    }

    if (!this.data.agreed) {
      wx.showToast({
        title: '请先同意服务协议',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      await request({
        url: '/user/register',
        method: 'POST',
        data: {
          username,
          email,
          phone,
          password
        }
      })

      wx.showToast({
        title: '注册成功，请登录',
        icon: 'success'
      })

      setTimeout(() => {
        wx.redirectTo({
          url: '/pages/login/login'
        })
      }, 1000)
    } catch (error) {
      console.error('注册失败:', error)
    } finally {
      this.setData({ loading: false })
    }
  },

  goToLogin() {
    wx.redirectTo({
      url: '/pages/login/login'
    })
  }
})
