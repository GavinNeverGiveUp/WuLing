// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Antd from 'ant-design-vue'

// 尝试引入 dist 目录下的标准 CSS 文件
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)
app.use(router)
app.use(store)
app.use(Antd)
app.mount('#app')