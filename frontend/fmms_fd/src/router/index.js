// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import store from '../store' // 引入store以检查token

const Login = () => import('@/views/LoginView.vue')
const Register = () => import('@/views/RegisterView.vue')
const Home = () => import('@/views/HomeView.vue')

const routes = [
  {
    path: '/',
    redirect: '/home' // 默认重定向到首页
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresNoAuth: true } // 标记此路由不需要认证
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresNoAuth: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const token = store.state.token;
  const requiresNoAuth = to.matched.some(record => record.meta.requiresNoAuth);

  if (!requiresNoAuth && !token) {
    // 如果访问的是需要认证的页面且没有token，则跳转到登录页
    next('/login');
  } else {
    next(); // 否则，继续导航
  }
})

export default router