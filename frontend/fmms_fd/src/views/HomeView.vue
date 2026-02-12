<!-- src/views/HomeView.vue -->
<template>
  <div class="home-wrapper">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-brand">
          <h2>FMMS</h2>
          <span class="navbar-subtitle">家庭物资管理系统</span>
        </div>
        <div class="navbar-actions">
          <div class="user-info">
            <a-dropdown>
              <div class="user-info-content">
                <div class="user-avatar">
                  <a-avatar>{{ store.state.userInfo?.username?.charAt(0) || 'U' }}</a-avatar>
                </div>
                <span class="user-name">{{ store.state.userInfo?.username || '未知用户' }}</span>
              </div>
              <template #overlay>
                <a-menu>
                  <a-menu-item>
                    <div class="user-detail-item">
                      <span class="user-detail-label">邮箱：</span>
                      <span class="user-detail-value">{{ store.state.userInfo?.email || '未知' }}</span>
                    </div>
                  </a-menu-item>
                  <a-menu-item>
                    <div class="user-detail-item">
                      <span class="user-detail-label">手机号：</span>
                      <span class="user-detail-value">{{ store.state.userInfo?.phone || '未知' }}</span>
                    </div>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
          <a-button type="primary" danger @click="handleLogout">退出登录</a-button>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="home-container">
      <div class="hero-section">
        <h1 class="hero-title">欢迎使用家庭物资管理系统</h1>
        <p class="hero-subtitle">智能助手随时为您解答关于家庭物资管理的问题</p>
      </div>

      <div class="chat-container">
        <!-- 消息历史区域 -->
        <div class="messages-history" ref="messagesHistory">
          <div v-for="(message, index) in messages" :key="index" class="message-wrapper" :class="{ 'user-message': message.sender === '我', 'ai-message': message.sender === 'AI助手' }">
            <div class="message-content">
              <div class="message-sender">{{ message.sender }}</div>
              <div class="message-text" v-html="parseMarkdown(message.text)"></div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <a-input-search
            v-model:value="inputMessage"
            placeholder="请输入消息..."
            enter-button="发送"
            @search="sendMessage"
            size="large"
            :loading="isSending"
            class="input-search"
          />
        </div>
      </div>

      <footer class="footer">
        <div class="footer-content">
          <div class="footer-left">
            <p class="footer-by">BY PURELAND</p>
            <p class="footer-copyright">@2026 pureland</p>
          </div>
          <div class="footer-right">
            <p class="footer-email">开发者邮箱：sandman1997@outlook.com</p>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import request from '@/utils/request';
import { message } from 'ant-design-vue';

const router = useRouter();
const store = useStore();

const inputMessage = ref('');
const isSending = ref(false);
const messages = ref([
  { sender: 'AI助手', text: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？' }
]);
const messagesHistory = ref(null);

onMounted(() => {
  // 如果用户已登录，加载历史消息
  if (store.state.token) {
    loadHistoryMessages();
  } else {
    scrollToBottom();
  }
});

async function loadHistoryMessages() {
  try {
    const response = await request.get('/ai/messages', {
      params: {
        limit: 20
      }
    });
    
    // 处理历史消息
    if (response && response.length > 0) {
      // 清空现有消息
      messages.value = [];
      response.forEach(item => {
        messages.value.push({
          sender: item.role === 'user' ? '我' : 'AI助手',
          text: item.content
        });
      });
    } 
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });
  } catch (error) {
    console.error('Failed to load history messages:', error);
    // 加载失败时显示默认欢迎消息
    messages.value = [
      { sender: 'AI助手', text: '您好！我是您的家庭物资管理AI助手，请问有什么可以帮助您的吗？' }
    ];
    nextTick(() => {
      scrollToBottom();
    });
  }
}

watch(messages, () => {
  nextTick(() => {
    scrollToBottom();
  });
});

function scrollToBottom() {
  const container = messagesHistory.value;
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

async function sendMessage(inputValue) {
  const content = inputValue ? inputValue.trim() : inputMessage.value.trim();
  if (!content || isSending.value) return;

  messages.value.push({ sender: '我', text: content });
  // 清空输入框
  inputMessage.value = '';
  // 滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
  
  isSending.value = true;

  try {
    const response = await request.post('/ai/chat', { message: content });
    messages.value.push({ sender: 'AI助手', text: response.message });
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });

  } catch (error) {
    console.error('Failed to send message:', error);
    // 如果需要在这里显示错误信息，再取消注释并导入 message
    // message.error('发送消息失败');
  } finally {
    isSending.value = false;
  }
}

function parseMarkdown(text) {
  // 简单的markdown解析，处理常见的markdown语法
  if (!text) return '';
  
  // 替换标题
  text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');
  text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
  text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
  
  // 替换粗体和斜体
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // 替换链接
  text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
  
  // 替换换行
  text = text.replace(/\n/g, '<br>');
  
  return text;
}

function handleLogout() {
  // 清除token
  store.commit('CLEAR_TOKEN');
  // 跳转到登录页
  router.push('/login');
  // 显示成功消息
  message.success('退出登录成功');
}
</script>

<style scoped>
/* 全局样式 */
.home-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
}

/* 导航栏样式 */
.navbar {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  width: 80%;
  margin: 0 auto;
  padding: 16px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.navbar-brand h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

.navbar-subtitle {
  font-size: 14px;
  color: #666;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  position: relative;
}

.user-info-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-info-content:hover {
  background-color: #f0f0f0;
}

.user-avatar {
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.user-detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 16px;
}

.user-detail-label {
  font-size: 14px;
  color: #666;
  min-width: 60px;
}

.user-detail-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 主要内容样式 */
.home-container {
  padding: 40px 20px;
  width: 80%;
  margin: 0 auto;
  flex: 1;
}

/* 英雄区域样式 */
.hero-section {
  margin-bottom: 40px;
  text-align: center;
}

.hero-title {
  font-size: 32px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.hero-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 聊天容器样式 */
.chat-container {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  height: 70vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chat-container:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
}

/* 消息历史区域样式 */
.messages-history {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background-color: #fafafa;
}

/* 消息样式 */
.message-wrapper {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-message {
  justify-content: flex-start;
}

.user-message {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 14px 18px;
  border-radius: 20px;
  word-wrap: break-word;
  position: relative;
}

.ai-message .message-content {
  background-color: white;
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.user-message .message-content {
  background-color: #1890ff;
  border-bottom-right-radius: 6px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}

.user-message .message-sender,
.user-message .message-text {
  color: white;
}

.message-sender {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
  font-weight: 500;
}

.message-text {
  font-size: 14px;
  line-height: 1.5;
}

/* Markdown 样式 */
.message-text h1 {
  font-size: 18px;
  margin: 10px 0;
}

.message-text h2 {
  font-size: 16px;
  margin: 8px 0;
}

.message-text h3 {
  font-size: 14px;
  margin: 6px 0;
}

.message-text strong {
  font-weight: bold;
}

.message-text em {
  font-style: italic;
}

.message-text a {
  color: #1890ff;
  text-decoration: none;
}

.message-text a:hover {
  text-decoration: underline;
}

.user-message .message-text a {
  color: #e6f7ff;
}

/* 输入区域样式 */
.input-area {
  padding: 20px 30px;
  border-top: 1px solid #e8e8e8;
  background-color: white;
}

.input-search {
  width: 100%;
}

/* 底部样式 */
.footer {
  margin-top: 60px;
  padding: 30px 0;
  border-top: 1px solid #f0f0f0;
  background-color: white;
}

.footer-content {
  width: 80%;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.footer-right {
  text-align: right;
}

.footer-by {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.footer-copyright {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.footer-email {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* 滚动条样式 */
.messages-history::-webkit-scrollbar {
  width: 6px;
}

.messages-history::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-history::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-history::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container,
  .navbar-container,
  .footer-content {
    width: 95%;
  }

  .home-container {
    padding: 20px 10px;
  }

  .hero-title {
    font-size: 24px;
  }

  .chat-container {
    height: 60vh;
  }

  .messages-history {
    padding: 20px;
  }

  .input-area {
    padding: 16px 20px;
  }
}
</style>