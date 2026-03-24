// src/store/index.js
import { createStore } from 'vuex'

const defaultExpirationAlerts = {
  expired_within_3_days: [],
  expiring_within_3_days: [],
  total_count: 0
}

function getStoredExpirationAlerts() {
  try {
    const raw = localStorage.getItem('expirationAlerts')
    if (!raw) {
      return { ...defaultExpirationAlerts }
    }

    const parsed = JSON.parse(raw)
    return {
      expired_within_3_days: Array.isArray(parsed?.expired_within_3_days) ? parsed.expired_within_3_days : [],
      expiring_within_3_days: Array.isArray(parsed?.expiring_within_3_days) ? parsed.expiring_within_3_days : [],
      total_count: Number.isFinite(parsed?.total_count) ? parsed.total_count : 0
    }
  } catch (error) {
    console.error('Failed to parse stored expiration alerts:', error)
    return { ...defaultExpirationAlerts }
  }
}

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
    expirationAlerts: getStoredExpirationAlerts()
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    SET_EXPIRATION_ALERTS(state, payload) {
      const normalized = {
        expired_within_3_days: Array.isArray(payload?.expired_within_3_days) ? payload.expired_within_3_days : [],
        expiring_within_3_days: Array.isArray(payload?.expiring_within_3_days) ? payload.expiring_within_3_days : [],
        total_count: Number.isFinite(payload?.total_count) ? payload.total_count : 0
      }
      state.expirationAlerts = normalized
      localStorage.setItem('expirationAlerts', JSON.stringify(normalized))
    },
    CLEAR_TOKEN(state) {
      state.token = null
      state.userInfo = null
      state.expirationAlerts = { ...defaultExpirationAlerts }
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('expirationAlerts')
    }
  },
  actions: {
  },
  modules: {
  }
})
