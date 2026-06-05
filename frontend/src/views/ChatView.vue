<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import ChatBubble from "../components/ChatBubble.vue";
import VoiceRecorder from "../components/VoiceRecorder.vue";
import CorrectionPanel from "../components/CorrectionPanel.vue";
import { useSpeechRecognition } from "../composables/useSpeechRecognition";
import { useWebSocket } from "../composables/useWebSocket";
import { endSession, fetchSession } from "../services/api";

const route = useRoute();
const router = useRouter();
const sessionId = route.params.sessionId;

const { isListening, transcript, error: speechError, start: startSpeech, stop: stopSpeech } = useSpeechRecognition();
const {
  connected,
  messages,
  currentScores,
  error: wsError,
  connect,
  sendMessage,
  sendStart,
  disconnect,
} = useWebSocket();

const inputText = ref("");
const isProcessing = ref(false);
const messagesEnd = ref(null);
const sessionLoaded = ref(false);

// Start screen state
const hasStarted = ref(false);
const isWaitingForAI = ref(false);
const scenarioName = ref("");
const startError = ref("");
let startTimeoutId = null;

function clearStartTimeout() {
  if (startTimeoutId) {
    clearTimeout(startTimeoutId);
    startTimeoutId = null;
  }
}

// Load existing messages + scenario info on mount
onMounted(async () => {
  connect(`/api/ws/${sessionId}`);

  try {
    const session = await fetchSession(sessionId);
    scenarioName.value = session.scenario_name || "";

    if (session.messages && session.messages.length > 0) {
      hasStarted.value = true;
      session.messages.forEach((msg) => {
        if (!messages.value.find((m) => m.content === msg.content && m.role === msg.role)) {
          messages.value.push({
            role: msg.role,
            content: msg.content,
            corrections: [],
          });
        }
      });
    }
    // else: hasStarted stays false → show start screen
  } catch (e) {
    // New session, no messages yet
  }
  sessionLoaded.value = true;
});

onUnmounted(() => {
  clearStartTimeout();
  disconnect();
});

// Auto-scroll on new messages
watch(
  () => messages.value.length,
  async () => {
    await nextTick();
    messagesEnd.value?.scrollIntoView({ behavior: "smooth" });
  }
);

// When the first AI message arrives (the opening line), switch to chat mode
watch(messages, (msgs) => {
  if (!hasStarted.value && msgs.length === 1 && msgs[0].role === "assistant") {
    clearStartTimeout();
    hasStarted.value = true;
    isWaitingForAI.value = false;
    startError.value = "";
  }
}, { deep: true });

// When speech recognition returns transcript, send it
watch(transcript, (val) => {
  if (val) {
    isProcessing.value = true;
    sendMessage(val);
    setTimeout(() => {
      isProcessing.value = false;
    }, 1000);
  }
});

function handleStart() {
  isWaitingForAI.value = true;
  startError.value = "";
  sendStart();
  // Timeout: if no AI reply within 25 seconds, show error
  clearStartTimeout();
  startTimeoutId = setTimeout(() => {
    if (isWaitingForAI.value) {
      isWaitingForAI.value = false;
      startError.value = "AI 响应超时，请检查后端日志确认 DeepSeek API 是否正常。";
    }
  }, 25000);
}

function sendTextMessage() {
  const text = inputText.value.trim();
  if (!text) return;
  isProcessing.value = true;
  sendMessage(text);
  inputText.value = "";
  setTimeout(() => {
    isProcessing.value = false;
  }, 1000);
}

function handleRecordStart() {
  startSpeech();
}

function handleRecordStop() {
  stopSpeech();
}

async function handleEndSession() {
  try {
    await endSession(sessionId);
    router.push({ name: "Summary", params: { sessionId } });
  } catch (e) {
    alert("结束会话失败");
  }
}

function handleKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendTextMessage();
  }
}
</script>

<template>
  <div class="chat-view">
    <!-- ── Header bar ── -->
    <div class="chat-header">
      <h2>💬 {{ scenarioName || "对话练习" }}</h2>
      <div class="header-actions">
        <span v-if="!connected" class="status disconnected">未连接</span>
        <span v-else class="status connected">已连接</span>
        <button
          v-if="hasStarted"
          class="btn btn-secondary btn-sm"
          @click="handleEndSession"
        >
          结束练习
        </button>
      </div>
    </div>

    <!-- ── START SCREEN (before user clicks "开始练习") ── -->
    <div v-if="!hasStarted && sessionLoaded" class="start-screen">
      <div class="start-card">
        <div class="start-icon">🎙️</div>
        <h2>{{ scenarioName || "对话练习" }}</h2>
        <p class="start-hint">
          准备好了吗？点击下方按钮，AI 教练将先和您打招呼，
          然后您就可以开始英语口语对话了。
        </p>
        <button
          class="btn btn-primary btn-start"
          :disabled="!connected || isWaitingForAI"
          @click="handleStart"
        >
          <span v-if="isWaitingForAI" class="spinner"></span>
          <span v-else>🎯 开始练习</span>
        </button>
        <p v-if="!connected" class="connecting-hint">正在连接服务器...</p>
        <p v-if="startError" class="start-error">{{ startError }}</p>
      </div>
    </div>

    <!-- ── CHAT INTERFACE (after start) ── -->

    <!-- Score bar -->
    <template v-if="hasStarted">
      <div v-if="currentScores" class="score-bar">
        <div class="score-item">
          <span class="score-label">语法</span>
          <span class="score-value">{{ Math.round(currentScores.grammar) }}</span>
        </div>
        <div class="score-item">
          <span class="score-label">流利度</span>
          <span class="score-value">{{ Math.round(currentScores.fluency) }}</span>
        </div>
        <div class="score-item">
          <span class="score-label">词汇</span>
          <span class="score-value">{{ Math.round(currentScores.vocabulary) }}</span>
        </div>
      </div>

      <!-- Error messages -->
      <div v-if="speechError || wsError" class="error-banner">
        {{ speechError || wsError }}
      </div>

      <!-- Chat messages -->
      <div class="chat-messages">
        <div v-if="messages.length === 0" class="empty-chat">
          <p>等待 AI 开场...</p>
        </div>
        <ChatBubble
          v-for="(msg, i) in messages"
          :key="i"
          :role="msg.role"
          :content="msg.content"
          :corrections="msg.corrections || []"
        />
        <div ref="messagesEnd" />
      </div>

      <!-- Corrections panel (shows real-time corrections above input) -->
      <CorrectionPanel :corrections="[]" />

      <!-- Input area -->
      <div class="input-area">
        <VoiceRecorder
          :is-recording="isListening"
          :is-processing="isProcessing"
          @start="handleRecordStart"
          @stop="handleRecordStop"
        />
        <div class="text-input-row">
          <input
            v-model="inputText"
            type="text"
            class="text-input"
            placeholder="或输入文字..."
            @keydown="handleKeydown"
            :disabled="isProcessing"
          />
          <button
            class="btn btn-primary"
            :disabled="isProcessing || !inputText.trim()"
            @click="sendTextMessage"
          >
            发送
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

/* ── Header ── */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chat-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.status.connected {
  background: #d1fae5;
  color: #065f46;
}

.status.disconnected {
  background: #fce7f3;
  color: #9d174d;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
}

/* ── Start Screen ── */
.start-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.start-card {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  padding: 48px 40px;
  text-align: center;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.start-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.start-card h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #1f2937;
}

.start-hint {
  color: #6b7280;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 28px;
}

.btn-start {
  padding: 14px 40px;
  font-size: 18px;
  border-radius: 50px;
  min-width: 200px;
}

.connecting-hint {
  margin-top: 12px;
  font-size: 13px;
  color: #9ca3af;
}

.start-error {
  margin-top: 12px;
  font-size: 13px;
  color: #dc2626;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: 8px;
}

/* ── Score Bar ── */
.score-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 8px 16px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  color: #6b7280;
}

.score-value {
  font-size: 14px;
  font-weight: 700;
  color: #4f46e5;
}

.error-banner {
  background: #fef2f2;
  color: #dc2626;
  padding: 8px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

/* ── Chat Messages ── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 12px;
}

.empty-chat {
  text-align: center;
  color: #9ca3af;
  padding: 60px 20px;
}

/* ── Input Area ── */
.input-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.text-input-row {
  display: flex;
  width: 100%;
  gap: 8px;
}

.text-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.text-input:focus {
  border-color: #4f46e5;
}
</style>
