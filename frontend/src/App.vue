<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <router-link to="/" class="app-logo">
        <span class="logo-icon">🗣️</span>
        <h1>SpeakCoach AI</h1>
      </router-link>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: inherit;
}

.logo-icon {
  font-size: 28px;
}

.app-logo h1 {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.app-main {
  flex: 1;
  padding: 24px;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
}
</style>
