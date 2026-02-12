// src/utils/request.js
import axios from 'axios'
import store from '@/store'
import router from '@/router'
import { message } from 'ant-design-vue'; // 导入 antdv 的 message 组件

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // 设置API的基础URL
  timeout: 1000 * 60 * 5
});

// 请求拦截器，在请求头中加入token
service.interceptors.request.use(
  config => {
    if (store.state.token) {
      config.headers['Authorization'] = `Bearer ${store.state.token}`;
    }
    return config;
  },
  error => {
    console.error(error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response.data;
  },
  error => {
    console.error('API Error:', error.response);
    // 对响应错误做点什么
    if (error.response && [401, 403].includes(error.response.status)) {
      // 如果后端返回401或403，认为是未授权，清除本地token并跳转到登录页
      store.commit('CLEAR_TOKEN');
      router.push('/login');
      message.error('登录已过期，请重新登录');
    } else {
        // 处理其他非认证相关的错误
        message.error(error.response?.data?.message || '请求失败，请稍后再试');
    }
    return Promise.reject(error);
  }
);

export default service;