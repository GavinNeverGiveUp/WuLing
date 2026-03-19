import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const Landing = () => import('@/views/LandingView.vue')
const Login = () => import('@/views/LoginView.vue')
const Register = () => import('@/views/RegisterView.vue')
const Home = () => import('@/views/HomeView.vue')
const Setting = () => import('@/views/SettingView.vue')

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing,
    meta: { requiresNoAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresNoAuth: true }
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
  },
  {
    path: '/settings',
    name: 'Setting',
    component: Setting
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const token = store.state.token
  const requiresNoAuth = to.matched.some((record) => record.meta.requiresNoAuth)

  if (!requiresNoAuth && !token) {
    next('/login')
    return
  }

  if (token && ['Login', 'Register'].includes(to.name)) {
    next('/home')
    return
  }

  next()
})

export default router

