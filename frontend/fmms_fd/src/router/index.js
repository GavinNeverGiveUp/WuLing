import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import { isLikelyMobile } from '@/utils/device'

const Landing = () => import('@/views/LandingView.vue')
const Login = () => import('@/views/LoginView.vue')
const Register = () => import('@/views/RegisterView.vue')
const Home = () => import('@/views/HomeView.vue')
const HomeMobile = () => import('@/views/MobileHomeView.vue')
const MobileMgmt = () => import('@/views/MobileMgmtView.vue')
const Setting = () => import('@/views/SettingView.vue')
const Mgmt = () => import('@/views/MgmtView.vue')

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
    path: '/m/home',
    name: 'HomeMobile',
    component: HomeMobile
  },
  {
    path: '/m/mgmt',
    name: 'MobileMgmt',
    component: MobileMgmt
  },
  {
    path: '/settings',
    name: 'Setting',
    component: Setting
  },
  {
    path: '/mgmt',
    name: 'Mgmt',
    component: Mgmt
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
  const isMobile = isLikelyMobile()

  if (!requiresNoAuth && !token) {
    next('/login')
    return
  }

  if (token && ['Login', 'Register'].includes(to.name)) {
    next(isMobile ? '/m/home' : '/home')
    return
  }

  if (token && to.name === 'Home' && isMobile) {
    next('/m/home')
    return
  }

  if (token && to.name === 'Mgmt' && isMobile) {
    next('/m/mgmt')
    return
  }

  if (token && to.name === 'HomeMobile' && !isMobile) {
    next('/home')
    return
  }

  if (token && to.name === 'MobileMgmt' && !isMobile) {
    next('/mgmt')
    return
  }

  next()
})

export default router
