<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import SceneCard from "../components/SceneCard.vue";
import { fetchScenarios, createSession, createScenario, deleteScenario } from "../services/api";

const router = useRouter();
const scenarios = ref([]);
const loading = ref(true);
const error = ref(null);
const showModal = ref(false);
const creating = ref(false);
const deletingId = ref(null);
const formData = ref({
  name: "",
  description: "",
  icon: "🎯",
  difficulty: "中级",
  system_prompt: "",
});
const BUILTIN_COUNT = 3;

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

function openCreateModal() {
  formData.value = { name: "", description: "", icon: "🎯", difficulty: "中级", system_prompt: "" };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

async function submitCreate() {
  if (!formData.value.name.trim()) return;
  creating.value = true;
  try {
    const newScenario = await createScenario(formData.value);
    scenarios.value.push(newScenario);
    showModal.value = false;
  } catch (e) {
    alert("创建场景失败，请重试。");
  } finally {
    creating.value = false;
  }
}

async function confirmDelete(scenarioId) {
  if (!confirm("确定要删除这个场景吗？关联的所有练习记录也会被删除。")) return;
  deletingId.value = scenarioId;
  try {
    await deleteScenario(scenarioId);
    scenarios.value = scenarios.value.filter((s) => s.id !== scenarioId);
  } catch {
    alert("删除失败，请重试。");
  } finally {
    deletingId.value = null;
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
        :show-delete="s.id > BUILTIN_COUNT"
        @select="selectScenario"
        @delete="confirmDelete"
      />
      <!-- Add custom scene card -->
      <div class="scene-card add-card" @click="openCreateModal">
        <div class="add-icon">＋</div>
        <div class="scene-info">
          <h3 class="scene-name">自定义场景</h3>
          <p class="scene-desc">创建你自己的口语练习场景</p>
        </div>
      </div>
    </div>

    <div class="home-footer">
      <router-link to="/history" class="btn btn-secondary">📋 历史记录</router-link>
    </div>

    <!-- Create modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <h3>创建自定义场景</h3>
          <div class="form-group">
            <label>场景名称 *</label>
            <input v-model="formData.name" type="text" placeholder="例如：酒店入住" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="formData.description" placeholder="简单描述这个场景..." rows="2" />
          </div>
          <div class="form-row">
            <div class="form-group form-group-sm">
              <label>图标</label>
              <input v-model="formData.icon" type="text" placeholder="🎯" />
            </div>
            <div class="form-group form-group-sm">
              <label>难度</label>
              <select v-model="formData.difficulty">
                <option>初级</option>
                <option>中级</option>
                <option>高级</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>AI 角色设定</label>
            <textarea
              v-model="formData.system_prompt"
              placeholder="用英文描述 AI 应该扮演的角色和行为。例如：You are a hotel receptionist. Greet the user, ask about their reservation, help them check in, and answer questions about the hotel facilities."
              rows="4"
            />
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button class="btn btn-primary" :disabled="creating || !formData.name.trim()" @click="submitCreate">
              {{ creating ? "创建中..." : "确认创建" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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

/* Add card */
.add-card {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d1d5db;
  background: #f9fafb;
  min-height: 100px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-card:hover {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.add-icon {
  font-size: 36px;
  color: #4f46e5;
  font-weight: 300;
  flex-shrink: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-card h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #4f46e5;
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group-sm {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
