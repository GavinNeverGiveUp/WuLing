// src/store/index.js
import { createStore } from 'vuex'

export default createStore({
  state: {
    token: localStorage.getItem('token') || null, // 初始化时从localStorage获取token
    userInfo: JSON.parse(localStorage.getItem('userInfo')) || null, // 初始化时从localStorage获取用户信息
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
      localStorage.setItem('token', token); // 将token存入localStorage
    },
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo;
      localStorage.setItem('userInfo', JSON.stringify(userInfo)); // 将用户信息存入localStorage
    },
    CLEAR_TOKEN(state) {
      state.token = null;
      state.userInfo = null;
      localStorage.removeItem('token'); // 清除localStorage中的token
      localStorage.removeItem('userInfo'); // 清除localStorage中的用户信息
    }
  },
  actions: {
  },
  modules: {
  }
})