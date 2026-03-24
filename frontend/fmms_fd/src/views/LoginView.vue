<template>
  <div class="auth-page">
    <div class="auth-backdrop"></div>

    <div class="auth-shell">
      <section class="auth-story">
        <span class="story-badge">AI 驱动的家庭秩序</span>
        <h1>你的家，<span>物灵</span>都记得</h1>
        <p>
          “让整理不再是负担，而是生活的诗意。物灵通过全息感知与智能理解，
          为你建立家中万物的数字映射。”
        </p>

        <div class="story-points">
          <article>
            <strong>智能寻物</strong>
            <span>一句话就能定位相机、药箱、备用钥匙和常用物资</span>
          </article>
          <article>
            <strong>临期提醒</strong>
            <span>药品、食品和个护用品的有效期状态统一掌握</span>
          </article>
        </div>
      </section>

      <section class="auth-card">
        <router-link class="home-link" to="/">返回首页</router-link>

        <div class="brand-lockup">
          <img
            class="brand-icon-image"
            src="https://api.iconify.design/solar/home-smile-bold-duotone.svg?color=%23D4B08C"
            alt=""
            aria-hidden="true"
          >
          <span class="brand-name">物灵<span class="brand-dot">.</span></span>
        </div>

        <div class="auth-copy">
          <h2>登录物灵</h2>
          <p>连接你的家庭物资视图，继续使用物灵。</p>
        </div>

        <form class="auth-form" @submit.prevent="onSubmit">
          <label>
            <span>用户名</span>
            <input v-model="formState.username" type="text" placeholder="请输入用户名">
          </label>

          <label>
            <span>访问密码</span>
            <input v-model="formState.password" type="password" placeholder="请输入密码">
          </label>

          <button class="submit-button" type="submit" :disabled="isLoading">
            {{ isLoading ? '登录中...' : '登录物灵' }}
          </button>
        </form>

        <p class="auth-switch">
          还没有账号？
          <router-link to="/register">立即免费注册</router-link>
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import request from '@/utils/request'

const router = useRouter()
const store = useStore()
const isLoading = ref(false)
const formState = reactive({
  username: '',
  password: ''
})

async function onSubmit() {
  if (!formState.username.trim() || !formState.password.trim()) {
    message.warning('请输入用户名和密码')
    return
  }

  isLoading.value = true

  try {
    const response = await request.post('/user/login', {
      username: formState.username.trim(),
      password: formState.password
    })

    store.commit('SET_TOKEN', response.access_token)

    const userInfoResponse = await request.get('/user/me')
    store.commit('SET_USER_INFO', userInfoResponse)

    router.push('/home')
    message.success('登录成功')
  } catch (error) {
    console.error('Login failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  font-family: 'Inter', 'Noto Serif SC', serif;
  display: grid;
  place-items: center;
  padding: 32px 20px;
  background:
    linear-gradient(rgba(248, 243, 238, 0.24), rgba(248, 243, 238, 0.12)),
    url('https://modao.cc/agent-py/media/generated_images/2026-03-19/a16a5570182a42cc9e6fcda0b92460b1.jpg') center/cover;
}

.auth-backdrop {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(212, 176, 140, 0.22), transparent 24%),
    rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(14px);
}

.auth-shell {
  position: relative;
  z-index: 1;
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(360px, 460px);
  gap: 24px;
  align-items: stretch;
}

.auth-story,
.auth-card {
  border-radius: 36px;
  border: 1px solid rgba(255, 255, 255, 0.42);
  background: rgba(255, 255, 255, 0.64);
  backdrop-filter: blur(22px);
  box-shadow: 0 24px 60px rgba(36, 26, 20, 0.12);
}

.auth-story {
  padding: 42px;
  color: #261c16;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.story-badge {
  width: fit-content;
  padding: 0.42rem 0.82rem;
  border-radius: 999px;
  background: rgba(199, 159, 125, 0.18);
  color: #946b4a;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.auth-story h1 {
  margin: 18px 0 14px;
  font-size: clamp(2.2rem, 4vw, 3.5rem);
  line-height: 1.15;
}

.auth-story h1 span {
  color: #d4b08c;
}

.auth-story p {
  max-width: 540px;
  margin: 0;
  color: #655951;
  line-height: 1.85;
}

.story-points {
  display: grid;
  gap: 16px;
  margin-top: 34px;
}

.story-points article {
  padding: 18px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.56);
}

.story-points strong {
  display: block;
  margin-bottom: 6px;
}

.story-points span {
  color: #786b62;
  line-height: 1.7;
}

.auth-card {
  padding: 28px;
  color: #261c16;
}

.home-link {
  color: #7d6f65;
  text-decoration: none;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
}

.brand-icon-image {
  width: 30px;
  height: 30px;
  display: block;
  flex-shrink: 0;
}

.brand-name {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.08em;
  color: #111827;
}

.brand-dot {
  color: #d4b08c;
}

.auth-copy {
  margin: 28px 0 24px;
}

.auth-copy h2 {
  margin: 0 0 8px;
  font-size: 2rem;
}

.auth-copy p {
  margin: 0;
  color: #7d6f65;
}

.auth-form {
  display: grid;
  gap: 16px;
}

.auth-form label {
  display: grid;
  gap: 8px;
}

.auth-form span {
  font-size: 0.88rem;
  font-weight: 600;
  color: #6c5f56;
}

.auth-form input {
  width: 100%;
  font-family: inherit;
  padding: 1rem 1.1rem;
  border-radius: 18px;
  border: 1px solid rgba(145, 106, 74, 0.12);
  background: rgba(255, 255, 255, 0.78);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.auth-form input:focus {
  border-color: rgba(171, 127, 91, 0.42);
  box-shadow: 0 0 0 4px rgba(212, 176, 140, 0.14);
}

.submit-button {
  margin-top: 8px;
  font-family: inherit;
  border: 0;
  border-radius: 18px;
  padding: 1rem 1.2rem;
  background: linear-gradient(135deg, #d4b08c, #b28059);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 18px 34px rgba(178, 128, 89, 0.24);
}

.submit-button:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.auth-switch {
  margin: 22px 0 0;
  text-align: center;
  color: #7d6f65;
}

.auth-switch a {
  color: #9a6f4f;
  font-weight: 700;
  text-decoration: none;
}

@media (max-width: 920px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-story {
    min-height: 280px;
  }
}

@media (max-width: 560px) {
  .auth-page {
    padding: 18px 12px;
  }

  .auth-story,
  .auth-card {
    padding: 22px;
    border-radius: 26px;
  }
}
</style>
