const { request } = require('../../utils/request.js')

Page({
  data: {
    userInfo: {},
    userDisplayName: '苏先生',
    userInitial: '苏',
    statusBarHeight: 24
  },

  onLoad() {
    this.ensureLogin()
    this.initSystemMetrics()
    this.loadUserProfile()
  },

  onShow() {
    this.ensureLogin()
    this.loadUserProfile()
  },

  ensureLogin() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return false
    }
    return true
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

  async loadUserProfile() {
    try {
      const userInfo = await request({
        url: '/user/me',
        method: 'GET'
      })
      wx.setStorageSync('userInfo', userInfo)
      this.applyUserInfo(userInfo)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      const cached = wx.getStorageSync('userInfo') || {}
      this.applyUserInfo(cached)
    }
  },

  applyUserInfo(userInfo) {
    const username = (userInfo && userInfo.username) || '苏先生'
    this.setData({
      userInfo,
      userDisplayName: username,
      userInitial: username.slice(0, 1).toUpperCase()
    })
  },

  goBackHome() {
    const pages = getCurrentPages()
    if (Array.isArray(pages) && pages.length > 1) {
      wx.navigateBack()
      return
    }

    wx.reLaunch({
      url: '/pages/home/home'
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
