<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import SceneCard from "../components/SceneCard.vue";
import { fetchScenarios, createSession } from "../services/api";

const router = useRouter();
const scenarios = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    scenarios.value = await fetchScenarios();
  } catch (e) {
    error.value = "无法加载场景，请确保后端已启动。";
  } finally {
    loading.value = false;
  }
});

async function selectScenario(scenarioId) {
  try {
    const session = await createSession(scenarioId);
    router.push({ name: "Chat", params: { sessionId: session.id } });
  } catch (e) {
    error.value = "创建会话失败，请重试。";
  }
}
</script>

<template>
  <div class="home">
    <div class="hero">
      <h2>选择练习场景</h2>
      <p>选择一个场景开始英语口语对话练习</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载场景中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <p class="hint">请运行后端：<code>cd backend && uvicorn app.main:app --reload</code></p>
    </div>

    <div v-else class="scene-grid">
      <SceneCard
        v-for="s in scenarios"
        :key="s.id"
        :scenario="s"
        @select="selectScenario"
      />
    </div>

    <div class="home-footer">
      <router-link to="/history" class="btn btn-secondary">📋 历史记录</router-link>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding-top: 20px;
}

.hero {
  text-align: center;
  margin-bottom: 32px;
}

.hero h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.hero p {
  color: #6b7280;
  font-size: 16px;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.error-state code {
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.hint {
  margin-top: 8px;
  font-size: 14px;
  color: #9ca3af;
}

.scene-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.home-footer {
  text-align: center;
  margin-top: 32px;
}
</style>
