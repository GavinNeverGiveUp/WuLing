<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;700&display=swap');

html,
body,
#app {
  min-height: 100%;
}

body {
  margin: 0;
  background: #f8f3ee;
  color: #221a15;
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

* {
  box-sizing: border-box;
}

a,
button,
input,
textarea {
  font: inherit;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}
</style>
