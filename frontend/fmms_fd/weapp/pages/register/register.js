const { request } = require('../../utils/request.js')

Page({
  data: {
    username: '',
    email: '',
    password: '',
    loading: false
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

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  async handleRegister() {
    const { username, email, password } = this.data
    
    if (!username || !email || !password) {
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

    this.setData({ loading: true })

    try {
      await request({
        url: '/user/register',
        method: 'POST',
        data: {
          username,
          email,
          phone: '12312341234',
          password
        }
      })

      wx.showToast({
        title: '注册成功，请登录',
        icon: 'success'
      })

      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      console.error('注册失败:', error)
    } finally {
      this.setData({ loading: false })
    }
  },

  goToLogin() {
    wx.navigateBack()
  }
})
