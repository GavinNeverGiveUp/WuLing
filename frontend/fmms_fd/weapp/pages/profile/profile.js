Page({
  data: {
    userInfo: {},
    firstChar: ''
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
  },

  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
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
          }, 1000)
        }
      }
    })
  }
})
