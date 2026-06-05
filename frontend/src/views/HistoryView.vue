<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { fetchSessions } from "../services/api";

const router = useRouter();
const sessions = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    sessions.value = await fetchSessions();
  } catch (e) {
    error.value = "无法加载历史记录";
  } finally {
    loading.value = false;
  }
});

function viewSummary(sessionId) {
  router.push({ name: "Summary", params: { sessionId } });
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleString("zh-CN");
}
</script>

<template>
  <div class="history-view">
    <div class="page-header">
      <h2>📋 历史记录</h2>
      <router-link to="/" class="btn btn-secondary">← 返回首页</router-link>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
    </div>

    <div v-else-if="sessions.length === 0" class="empty-state">
      <p>还没有练习记录，快去开始第一次练习吧！</p>
      <router-link to="/" class="btn btn-primary">开始练习</router-link>
    </div>

    <div v-else class="session-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="session-card card"
        @click="viewSummary(s.id)"
      >
        <div class="session-info">
          <h3>{{ s.scenario_name || "对话练习" }}</h3>
          <p class="session-date">{{ formatDate(s.start_time) }}</p>
        </div>
        <div class="session-score" v-if="s.overall_score">
          <span class="score">{{ Math.round(s.overall_score) }}</span>
          <span class="score-unit">分</span>
        </div>
        <div class="session-arrow">→</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-view {
  max-width: 640px;
  margin: 0 auto;
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
}

.empty-state p {
  margin-bottom: 16px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-card {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.session-card:hover {
  border-color: #4f46e5;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.08);
}

.session-info {
  flex: 1;
}

.session-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.session-date {
  font-size: 13px;
  color: #9ca3af;
}

.session-score {
  text-align: center;
}

.score {
  font-size: 24px;
  font-weight: 800;
  color: #4f46e5;
}

.score-unit {
  font-size: 14px;
  color: #6b7280;
}

.session-arrow {
  color: #d1d5db;
  font-size: 18px;
}
</style>
