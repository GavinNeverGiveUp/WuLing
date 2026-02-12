<!-- src/views/Login.vue -->
<template>
  <div class="login-container">
    <a-card class="login-card" title="家庭物资管理系统 (FMMS)">
      <a-form :model="formState" layout="vertical" @submit.prevent="onSubmit">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名!' }]">
          <a-input v-model:value="formState.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码!' }]">
          <a-input-password v-model:value="formState.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="isLoading">登录</a-button>
          <a-button @click="$router.push('/register')" style="margin-top: 10px;" block>注册</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import request from '@/utils/request';
import { message } from 'ant-design-vue';

const router = useRouter();
const store = useStore();
const isLoading = ref(false);
const formState = ref({
  username: '',
  password: ''
});

async function onSubmit() {
  isLoading.value = true;
  try {
    const response = await request.post('/user/login', formState.value);
    // 登录成功后，保存token到store和localStorage
    store.commit('SET_TOKEN', response.access_token);
    
    // 请求用户信息
    const userInfoResponse = await request.get('/user/me');
    // 保存用户信息到store和localStorage
    store.commit('SET_USER_INFO', userInfoResponse);
    
    router.push('/home');
    message.success('登录成功！');
  } catch (error) {
    // 登录失败，错误已在request.js的拦截器中处理并提示
    console.error('Login failed:', error);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.login-card {
  width: 360px;
}
</style>