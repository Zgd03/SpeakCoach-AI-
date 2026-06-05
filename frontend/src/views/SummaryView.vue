<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchSession, fetchSummary } from "../services/api";

const route = useRoute();
const router = useRouter();
const sessionId = route.params.sessionId;

const summary = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // Try to get the summary; if not generated yet, it will use session data
    let data;
    try {
      data = await fetchSummary(sessionId);
    } catch {
      // If summary endpoint not implemented yet, use session info
      const session = await fetchSession(sessionId);
      data = {
        overall_score: session.overall_score || 0,
        dimensions: { grammar: 0, fluency: 0, vocabulary: 0, pronunciation: 0 },
        strengths: [],
        weaknesses: [],
        tips: [],
        corrected_dialogue: [],
        scenario_name: session.scenario_name || "对话练习",
      };
    }
    summary.value = data;
  } catch (e) {
    error.value = "无法加载总结数据";
  } finally {
    loading.value = false;
  }
});

function goHome() {
  router.push({ name: "Home" });
}

function goToHistory() {
  router.push({ name: "History" });
}

function scoreColor(score) {
  if (score >= 80) return "#059669";
  if (score >= 60) return "#d97706";
  return "#dc2626";
}

function dimensionLabel(key) {
  const labels = {
    grammar: "语法",
    fluency: "流利度",
    vocabulary: "词汇",
    pronunciation: "发音",
  };
  return labels[key] || key;
}
</script>

<template>
  <div class="summary-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>生成总结中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-primary" @click="goHome">返回首页</button>
    </div>

    <div v-else-if="summary" class="summary-content">
      <div class="summary-header">
        <h2>📊 课后总结</h2>
        <p class="scenario-name">{{ summary.scenario_name }}</p>
      </div>

      <!-- Overall Score -->
      <div class="score-section card">
        <div class="overall-score" :style="{ color: scoreColor(summary.overall_score) }">
          <span class="score-number">{{ Math.round(summary.overall_score) }}</span>
          <span class="score-unit">/100</span>
        </div>
        <p class="score-label-text">综合评分</p>
      </div>

      <!-- Dimension Scores -->
      <div class="dimensions card">
        <h3>各维度评分</h3>
        <div class="dimension-grid">
          <div
            v-for="(value, key) in summary.dimensions"
            :key="key"
            class="dimension-item"
          >
            <span class="dim-label">{{ dimensionLabel(key) }}</span>
            <div class="dim-bar-bg">
              <div
                class="dim-bar-fill"
                :style="{ width: value + '%', background: scoreColor(value) }"
              />
            </div>
            <span class="dim-value" :style="{ color: scoreColor(value) }">{{
              Math.round(value)
            }}</span>
          </div>
        </div>
      </div>

      <!-- Strengths & Weaknesses -->
      <div class="strength-weakness-grid">
        <div class="strengths card">
          <h3>✅ 优势</h3>
          <ul v-if="summary.strengths.length > 0">
            <li v-for="(s, i) in summary.strengths" :key="i">{{ s }}</li>
          </ul>
          <p v-else class="empty-text">暂无数据</p>
        </div>

        <div class="weaknesses card">
          <h3>💪 待改进</h3>
          <ul v-if="summary.weaknesses.length > 0">
            <li v-for="(w, i) in summary.weaknesses" :key="i">{{ w }}</li>
          </ul>
          <p v-else class="empty-text">暂无数据</p>
        </div>
      </div>

      <!-- Tips -->
      <div v-if="summary.tips && summary.tips.length > 0" class="tips card">
        <h3>📌 改进建议</h3>
        <ol>
          <li v-for="(t, i) in summary.tips" :key="i">{{ t }}</li>
        </ol>
      </div>

      <!-- Corrected Dialogue -->
      <div v-if="summary.corrected_dialogue && summary.corrected_dialogue.length > 0" class="corrected-dialogue card">
        <h3>📝 对话校正</h3>
        <div v-for="(item, i) in summary.corrected_dialogue" :key="i" class="dialogue-item">
          <div class="dialogue-original">
            <span class="label">原文：</span>
            <span class="text">{{ item.original }}</span>
          </div>
          <div class="dialogue-corrected">
            <span class="label">校正：</span>
            <span class="text">{{ item.corrected }}</span>
          </div>
          <p class="dialogue-explain">{{ item.explanation }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="summary-actions">
        <button class="btn btn-primary" @click="goHome">继续练习</button>
        <button class="btn btn-secondary" @click="goToHistory">查看历史</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-view {
  max-width: 640px;
  margin: 0 auto;
  padding: 20px 0;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
}

.summary-header {
  text-align: center;
  margin-bottom: 24px;
}

.summary-header h2 {
  font-size: 26px;
  font-weight: 700;
}

.scenario-name {
  color: #6b7280;
  margin-top: 4px;
}

.score-section {
  text-align: center;
  margin-bottom: 16px;
}

.overall-score {
  font-size: 48px;
  font-weight: 800;
  line-height: 1;
}

.score-unit {
  font-size: 18px;
  font-weight: 400;
  opacity: 0.5;
}

.score-label-text {
  color: #6b7280;
  margin-top: 4px;
  font-size: 14px;
}

.card {
  margin-bottom: 16px;
}

.card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.dimension-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dim-label {
  width: 50px;
  font-size: 14px;
  color: #374151;
  flex-shrink: 0;
}

.dim-bar-bg {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s;
}

.dim-value {
  width: 30px;
  text-align: right;
  font-weight: 700;
  font-size: 14px;
}

.strength-weakness-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.strengths ul,
.weaknesses ul {
  padding-left: 20px;
}

.strengths li,
.weaknesses li {
  margin-bottom: 6px;
  font-size: 14px;
  color: #374151;
}

.empty-text {
  color: #9ca3af;
  font-size: 14px;
}

.tips ol {
  padding-left: 20px;
}

.tips li {
  margin-bottom: 8px;
  font-size: 14px;
  color: #374151;
}

.corrected-dialogue .dialogue-item {
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.corrected-dialogue .dialogue-item:last-child {
  border-bottom: none;
}

.dialogue-original,
.dialogue-corrected {
  margin-bottom: 4px;
}

.label {
  font-weight: 600;
  font-size: 13px;
  color: #6b7280;
}

.text {
  font-size: 14px;
}

.dialogue-original .text {
  color: #ef4444;
  text-decoration: line-through;
}

.dialogue-corrected .text {
  color: #059669;
  font-weight: 600;
}

.dialogue-explain {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

.summary-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
</style>
