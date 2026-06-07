<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
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
  currentCorrections,
  currentScores,
  error: wsError,
  connect,
  sendMessage,
  disconnect,
} = useWebSocket();

const inputText = ref("");
const isProcessing = ref(false);
const messagesEnd = ref(null);
const sessionLoaded = ref(false);

// Load existing messages on mount
onMounted(async () => {
  connect(`/api/ws/${sessionId}`);

  try {
    const session = await fetchSession(sessionId);
    if (session.messages && session.messages.length > 0) {
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
  } catch (e) {
    // Session might be new, that's fine
  }
  sessionLoaded.value = true;
});

onUnmounted(() => {
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

// When speech recognition returns transcript, send it
watch(transcript, (val) => {
  if (val) {
    isProcessing.value = true;
    sendMessage(val);
    // Reset after a short delay
    setTimeout(() => {
      isProcessing.value = false;
    }, 1000);
  }
});

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
    <div class="chat-header">
      <h2>💬 对话练习</h2>
      <div class="header-actions">
        <span v-if="!connected" class="status disconnected">未连接</span>
        <span v-else class="status connected">已连接</span>
        <button class="btn btn-secondary btn-sm" @click="handleEndSession">
          结束练习
        </button>
      </div>
    </div>

    <!-- Score bar -->
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
      <div v-if="messages.length === 0 && sessionLoaded" class="empty-chat">
        <p>点击「开始录音」或输入文字开始对话吧！</p>
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

    <!-- Corrections panel -->
    <CorrectionPanel :corrections="currentCorrections" />

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
        <button class="btn btn-primary" @click="sendTextMessage" :disabled="isProcessing || !inputText.trim()">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

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
