<template>
  <div class="landing-page">
    <nav class="site-nav">
      <div class="nav-inner">
        <div class="brand">
          <img
            class="brand-icon-image"
            src="https://api.iconify.design/solar/home-smile-bold-duotone.svg?color=%23D4B08C"
            alt=""
            aria-hidden="true"
          >
          <div class="brand-text">
            <span class="brand-name">物灵<span class="brand-dot">.</span></span>
          </div>
        </div>

        <div class="nav-links">
          <a href="#features">核心技术</a>
          <a href="#scenarios">场景方案</a>
          <a href="#voices">关于我们</a>
          <a href="#footer">订阅计划</a>
        </div>

        <div class="nav-actions">
          <router-link class="primary-action" :to="primaryRoute">开始使用</router-link>
        </div>
      </div>
    </nav>

    <header class="hero-section">
      <div class="hero-inner">
        <div class="hero-copy">
          <div class="hero-badge">AI 驱动的家庭秩序</div>
          <h1>
            你的家，<br>
            <span>物灵</span>都记得
          </h1>
          <p class="hero-subcopy">
            “让整理不再是负担，而是生活的诗意。物灵通过全息感知与智能理解，
            为你建立家中万物的数字映射。”
          </p>

          <div class="hero-actions">
            <router-link class="dark-action" to="/home">立即体验</router-link>
          </div>
        </div>

        <div class="hero-visual">
          <div class="hero-card">
            <img
              src="https://modao.cc/agent-py/media/generated_images/2026-03-19/a16a5570182a42cc9e6fcda0b92460b1.jpg"
              alt="物灵家庭物资管理首页主视觉"
            >
            <div class="floating-note top-note">
              <span class="note-label">AI 识别</span>
              <span class="note-value">已同步客厅、书房与厨房物资布局</span>
            </div>
            <div class="floating-note bottom-note">
              <span class="note-label">今日提醒</span>
              <span class="note-value">3 件物资即将到期，建议今日处理</span>
            </div>
          </div>
          <div class="hero-orb"></div>
        </div>
      </div>
    </header>

    <section id="features" class="feature-section">
      <div class="feature-section-inner">
        <div class="section-heading">
          <h2>为什么选择物灵？</h2>
          <p>连接物理世界与数字管理的最后一步</p>
        </div>

        <div class="feature-grid">
          <article class="feature-card">
            <div class="feature-icon-wrap">
              <img
                class="feature-icon-image"
                src="https://api.iconify.design/solar/users-group-rounded-bold-duotone.svg?color=%23D4B08C"
                alt=""
                aria-hidden="true"
              >
            </div>
            <h3>共享家庭</h3>
            <p>多用户协作，让每一位家庭成员都能实时同步物资状态，共同守护家的秩序。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon-wrap">
              <img
                class="feature-icon-image"
                src="https://api.iconify.design/solar/chat-line-bold-duotone.svg?color=%23D4B08C"
                alt=""
                aria-hidden="true"
              >
            </div>
            <h3>自然语言寻物</h3>
            <p>“我的相机在哪？”像问家人一样问物灵，它会精确告诉你物品在哪间房、哪个柜子。</p>
          </article>
          <article class="feature-card">
            <div class="feature-icon-wrap">
              <img
                class="feature-icon-image"
                src="https://api.iconify.design/solar/bell-bing-bold-duotone.svg?color=%23D4B08C"
                alt=""
                aria-hidden="true"
              >
            </div>
            <h3>智能过期提醒</h3>
            <p>药品、食物、护肤品，物灵会全天候监控保质期，在临期前为您推送最优处理建议。</p>
          </article>
        </div>
      </div>
    </section>

    <section id="scenarios" class="scenario-section">
      <div class="section-heading left-aligned">
        <span>场景方案</span>
        <h2>把“找不到”和“忘了管”变成过去式</h2>
      </div>

      <div class="scenario-grid">
        <article class="scenario-card">
          <p class="scenario-tag">家庭收纳</p>
          <h3>搬家后仍能快速找回熟悉秩序</h3>
          <p>物灵持续记录位置变化，让钥匙、相机、药箱、备用充电器都有可追踪的归属。</p>
        </article>
        <article class="scenario-card">
          <p class="scenario-tag">老人关怀</p>
          <h3>重点药品临期提醒更早一步</h3>
          <p>给父母常备药设置独立关注，重要物资变动和有效期状态一目了然。</p>
        </article>
        <article class="scenario-card">
          <p class="scenario-tag">家庭协作</p>
          <h3>孩子、伴侣、长辈都能使用同一套系统</h3>
          <p>从对话式寻物到补货提醒，所有人都在同一份家庭物资视图中协同。</p>
        </article>
      </div>
    </section>

    <section id="voices" class="voice-section">
      <div class="section-heading left-aligned">
        <span>听听物灵用户的声音</span>
        <h2>已经有很多家庭，用它开启更有序的生活</h2>
      </div>

      <div class="voice-grid">
        <article class="voice-card">
          <p>“搬新家后用上物灵，再也不会为了找备用钥匙把客厅翻一遍。”</p>
          <strong>苏女士 · 资深收纳达人</strong>
        </article>
        <article class="voice-card">
          <p>“AI 对话很自然，像一个知道家里细节的管家，问一句就能找到。”</p>
          <strong>张先生 · 数码博主</strong>
        </article>
        <article class="voice-card">
          <p>“过期提醒功能太实用了，茶叶、保健品和药品终于不会放到忘记。”</p>
          <strong>李阿姨 · 家庭采购负责人</strong>
        </article>
        <article class="voice-card">
          <p>“视觉很温和，但不是空壳设计，信息密度和使用效率都在线。”</p>
          <strong>陈小姐 · 设计从业者</strong>
        </article>
      </div>
    </section>

    <footer id="footer" class="site-footer">
      <div class="footer-inner">
        <div class="footer-main">
          <div class="footer-brand">
            <div class="footer-brand-lockup">
              <img
                class="brand-icon-image footer-brand-icon"
                src="https://api.iconify.design/solar/home-smile-bold-duotone.svg?color=%23D4B08C"
                alt=""
                aria-hidden="true"
              >
              <span class="footer-brand-name">物灵<span class="brand-dot">.</span></span>
            </div>
            <p>
              我们致力于用科技温暖家庭的每一个角落。物灵，懂你的家，也懂你的生活。
            </p>
          </div>

          <div class="footer-links-grid">
            <div>
              <h4>产品</h4>
              <a href="#features">功能地图</a>
              <a href="#">桌面客户端</a>
              <a href="#">智能配件</a>
            </div>
            <div>
              <h4>联系我们</h4>
              <a class="footer-contact" href="mailto:sandman1997@outlook.com">
                <img src="https://api.iconify.design/solar/letter-bold.svg?color=%23ffffff" alt="" aria-hidden="true">
                <span>sandman1997@outlook.com</span>
              </a>
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <p>© 2026 PURELAND - 版权所有</p>
          <div class="footer-socials">
            <a href="#" aria-label="微信">
              <img src="https://api.iconify.design/bi/wechat.svg?color=%23ffffff" alt="" aria-hidden="true">
            </a>
            <a href="#" aria-label="微博">
              <img src="https://api.iconify.design/bi/sina-weibo.svg?color=%23ffffff" alt="" aria-hidden="true">
            </a>
            <a href="#" aria-label="Twitter X">
              <img src="https://api.iconify.design/bi/twitter-x.svg?color=%23ffffff" alt="" aria-hidden="true">
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const primaryRoute = computed(() => (store.state.token ? '/home' : '/login'))
</script>

<style scoped>
.landing-page {
  --bg: #f9f6f2;
  --primary: #d4b08c;
  --primary-deep: #8f6746;
  --ink: #221a15;
  --muted: #7f7770;
  --border: rgba(143, 103, 70, 0.12);
  min-height: 100vh;
  font-family: 'Inter', 'Noto Serif SC', serif;
  background: var(--bg);
  color: var(--ink);
}

.scenario-section,
.voice-section,
.site-footer {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
}

.feature-section {
  width: 100%;
  margin: 0;
  background: #ffffff;
}

.site-nav {
  position: fixed;
  inset: 0 0 auto 0;
  z-index: 20;
  width: 100%;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  width: min(1180px, 100%);
  min-height: 80px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon-image {
  width: 30px;
  height: 30px;
  display: block;
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.brand-name {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.08em;
  color: #111827;
}

.brand-dot {
  color: var(--primary);
}

.brand-subtitle {
  font-size: 0.82rem;
  color: var(--muted);
}

.nav-links,
.nav-actions,
.hero-actions,
.footer-links {
  display: flex;
  align-items: center;
}

.nav-links {
  gap: 28px;
}

.nav-links a,
.footer-links a {
  color: #6d625b;
  font-size: 0.92rem;
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-links a:hover,
.footer-links a:hover {
  color: var(--primary-deep);
}

.primary-action,
.dark-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 116px;
  padding: 0.9rem 1.45rem;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.primary-action {
  background: linear-gradient(135deg, #cfab8a, #a77752);
  color: #fff;
  box-shadow: 0 16px 32px rgba(167, 119, 82, 0.28);
}

.dark-action {
  background: #1f1a17;
  color: #fff;
  box-shadow: 0 20px 40px rgba(31, 26, 23, 0.18);
}

.primary-action:hover,
.dark-action:hover {
  transform: translateY(-2px);
}

.hero-section {
  min-height: 100vh;
  padding: 112px 24px 52px;
  display: flex;
  align-items: center;
}

.hero-inner {
  width: min(1180px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(400px, 0.98fr);
  gap: 56px;
  align-items: center;
}

.hero-copy h1 {
  margin: 18px 0 24px;
  font-size: clamp(3.75rem, 6vw, 6rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: 0;
  color: #111827;
}

.hero-copy h1 span {
  color: var(--primary);
}

.hero-subcopy {
  max-width: 620px;
  margin: 0;
  font-size: 1.18rem;
  line-height: 1.95;
  color: #6b7280;
  font-style: italic;
}

.hero-badge,
.section-heading span,
.scenario-tag {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  background: rgba(212, 176, 140, 0.12);
  color: var(--primary-deep);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.hero-actions {
  margin-top: 34px;
}

.hero-visual {
  position: relative;
  min-height: 600px;
}

.hero-card {
  position: relative;
  min-height: 600px;
  height: 100%;
  overflow: hidden;
  border-radius: 42px;
  box-shadow: 0 28px 60px rgba(55, 38, 22, 0.18);
}

.hero-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.floating-note {
  position: absolute;
  max-width: 290px;
  padding: 18px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(20px);
  box-shadow: 0 18px 38px rgba(34, 26, 21, 0.1);
  animation: floatNote 3.8s ease-in-out infinite;
}

.note-label {
  display: block;
  margin-bottom: 8px;
  color: var(--primary-deep);
  font-size: 0.8rem;
  font-weight: 700;
}

.note-value {
  font-size: 0.95rem;
  line-height: 1.6;
  color: rgba(34, 26, 21, 0.88);
}

.top-note {
  top: 28px;
  left: 28px;
  animation-delay: 0s;
}

.bottom-note {
  right: 28px;
  bottom: 28px;
  animation-delay: 1.2s;
}

.hero-orb {
  position: absolute;
  inset: auto -22px -24px auto;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(210, 176, 139, 0.55), rgba(210, 176, 139, 0));
  filter: blur(8px);
}

@keyframes floatNote {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-10px);
  }
}

.feature-section,
.scenario-section,
.voice-section {
  padding: 88px 0;
}

.feature-section-inner {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
  padding: 96px 0;
}

.section-heading {
  text-align: center;
  margin-bottom: 42px;
}

.section-heading.left-aligned {
  text-align: left;
}

.section-heading h2 {
  margin: 0 0 12px;
  font-size: clamp(2rem, 3.3vw, 3.1rem);
  font-weight: 700;
  line-height: 1.2;
  color: #111827;
}

.section-heading p {
  max-width: 720px;
  margin: 0 auto;
  color: #6b7280;
  line-height: 1.8;
}

.section-heading.left-aligned p {
  margin-left: 0;
}

.feature-grid,
.scenario-grid,
.voice-grid {
  display: grid;
  gap: 22px;
}

.feature-grid,
.scenario-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.voice-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.feature-card,
.scenario-card,
.voice-card {
  padding: 30px;
  border-radius: 30px;
  border: 1px solid var(--border);
  box-shadow: 0 18px 34px rgba(34, 26, 21, 0.05);
}

.feature-card {
  background: #f9f6f2;
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
}

.feature-icon-wrap {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: rgba(212, 176, 140, 0.2);
  margin-bottom: 24px;
}

.feature-icon-image {
  width: 32px;
  height: 32px;
  display: block;
}

.scenario-card,
.voice-card {
  background: rgba(255, 255, 255, 0.86);
}

.feature-card h3,
.scenario-card h3 {
  margin: 0 0 12px;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.35;
}

.feature-card p,
.scenario-card p,
.voice-card p,
.footer-brand p {
  margin: 0;
  color: #6d625b;
  line-height: 1.8;
}

.scenario-section {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.46));
  border-radius: 48px;
}

.scenario-tag {
  margin-bottom: 18px;
}

.voice-card strong {
  display: inline-block;
  margin-top: 20px;
  font-size: 0.95rem;
}

.site-footer {
  width: 100%;
  margin: 0;
  padding: 80px 24px 40px;
  background: #111827;
  color: #ffffff;
}

.footer-inner {
  width: min(1180px, 100%);
  margin: 0 auto;
}

.footer-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 48px;
}

.footer-brand {
  max-width: 300px;
}

.footer-brand-lockup {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.footer-brand-icon {
  width: 30px;
  height: 30px;
}

.footer-brand-name {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.08em;
  color: #ffffff;
}

.footer-brand p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.8;
}

.footer-links-grid {
  display: grid;
  grid-template-columns: repeat(2, max-content);
  justify-content: end;
  gap: 64px;
}

.footer-links-grid div {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.footer-links-grid h4 {
  margin: 0 0 8px;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 700;
}

.footer-links-grid a {
  color: rgba(255, 255, 255, 0.62);
  text-decoration: none;
  font-size: 0.92rem;
}

.footer-links-grid a:hover {
  color: #d4b08c;
}

.footer-contact {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.footer-contact img {
  width: 16px;
  height: 16px;
}

.footer-bottom {
  margin-top: 80px;
  padding-top: 40px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
}

.footer-bottom p {
  margin: 0;
}

.footer-socials {
  display: flex;
  align-items: center;
  gap: 24px;
}

.footer-socials a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.footer-socials img {
  width: 20px;
  height: 20px;
  opacity: 0.86;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.footer-socials a:hover img {
  opacity: 1;
  transform: translateY(-1px);
}

@media (max-width: 1080px) {
  .hero-inner {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    min-height: 520px;
  }

  .feature-grid,
  .scenario-grid,
  .voice-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .footer-main {
    flex-direction: column;
  }

  .footer-links-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    justify-content: stretch;
    gap: 32px;
  }
}

@media (max-width: 820px) {
  .nav-inner {
    flex-wrap: wrap;
    justify-content: center;
    padding: 12px 0;
  }

  .nav-links {
    order: 2;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .footer-links-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 32px;
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
  }

  .feature-grid,
  .scenario-grid,
  .voice-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .feature-section,
  .scenario-section,
  .voice-section {
    width: min(1180px, calc(100% - 24px));
  }

  .site-footer {
    padding: 64px 12px 32px;
  }

  .site-nav {
    padding: 0 12px;
  }

  .nav-actions {
    order: 3;
  }

  .hero-section {
    padding: 118px 16px 42px;
  }

  .hero-card,
  .hero-visual {
    min-height: 420px;
  }

  .top-note,
  .bottom-note {
    inset: auto 16px 16px 16px;
    max-width: none;
  }

  .top-note {
    top: 16px;
    bottom: auto;
  }

  .bottom-note {
    top: auto;
  }

  .feature-card,
  .scenario-card,
  .voice-card {
    padding: 24px;
    border-radius: 24px;
  }

  .footer-links-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}
</style>








