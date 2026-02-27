const { request } = require('../../utils/request.js')

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onLoad() {
    const token = wx.getStorageSync('token')
    if (token) {
      wx.reLaunch({
        url: '/pages/home/home'
      })
    }
  },

  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    })
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  async handleLogin() {
    const { username, password } = this.data
    
    if (!username || !password) {
      wx.showToast({
        title: '请输入用户名和密码',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      const res = await request({
        url: '/user/login',
        method: 'POST',
        data: {
          username,
          password
        }
      })

      if (res.access_token) {
        wx.setStorageSync('token', res.access_token)
        
        const userInfo = await request({
          url: '/user/me',
          method: 'GET'
        })
        
        wx.setStorageSync('userInfo', userInfo)
        
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })

        setTimeout(() => {
          wx.reLaunch({
            url: '/pages/home/home'
          })
        }, 1000)
      }
    } catch (error) {
      console.error('登录失败:', error)
    } finally {
      this.setData({ loading: false })
    }
  },

  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
  }
})
