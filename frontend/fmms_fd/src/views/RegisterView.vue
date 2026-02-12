<!-- src/views/Register.vue -->
<template>
  <div class="register-container">
    <a-card class="register-card" title="用户注册">
      <a-form :model="formState" layout="vertical" @submit.prevent="onSubmit">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名!' }]">
          <a-input v-model:value="formState.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" name="email" :rules="[{ required: true, message: '请输入邮箱!' }, { type: 'email', message: '请输入有效的邮箱地址!' }]">
          <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="手机号" name="phone" :rules="[{ required: true, message: '请输入手机号!' }]">
          <a-input v-model:value="formState.phone" placeholder="请输入手机号" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码!' }]">
          <a-input-password v-model:value="formState.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="isLoading">注册</a-button>
          <a-button @click="$router.push('/login')" style="margin-top: 10px;" block>返回登录</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import { message } from 'ant-design-vue';

const router = useRouter();
const isLoading = ref(false);
const formState = ref({
  username: '',
  email: '',
  phone: '',
  password: ''
});

async function onSubmit() {
  isLoading.value = true;
  try {
    await request.post('/user/register', formState.value);
    router.push('/login');
    message.success('注册成功，请登录');
  } catch (error) {
    // 注册失败，错误已在request.js的拦截器中处理并提示
    console.error('Registration failed:', error);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.register-card {
  width: 360px;
}
</style>