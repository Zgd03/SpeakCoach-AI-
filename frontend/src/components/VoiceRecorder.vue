<script setup>
const emit = defineEmits(["start", "stop"]);
const props = defineProps({
  isRecording: {
    type: Boolean,
    default: false,
  },
  isProcessing: {
    type: Boolean,
    default: false,
  },
});

function toggle() {
  if (props.isProcessing) return;
  if (props.isRecording) {
    emit("stop");
  } else {
    emit("start");
  }
}
</script>

<template>
  <button
    class="voice-btn"
    :class="{ recording: isRecording, processing: isProcessing }"
    :disabled="isProcessing"
    @click="toggle"
  >
    <span v-if="isProcessing" class="spinner"></span>
    <span v-else class="mic-icon">{{ isRecording ? "🔴" : "🎤" }}</span>
    <span class="btn-label">
      {{ isProcessing ? "处理中..." : isRecording ? "点击停止" : "开始录音" }}
    </span>
  </button>
</template>

<style scoped>
.voice-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  max-width: 200px;
  padding: 14px 24px;
  border: 2px solid #e5e7eb;
  border-radius: 50px;
  background: #fff;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s;
  color: #374151;
}

.voice-btn:hover:not(:disabled) {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.voice-btn.recording {
  border-color: #ef4444;
  background: #fef2f2;
  color: #dc2626;
  animation: pulse 1.5s infinite;
}

.voice-btn.processing {
  border-color: #f59e0b;
  background: #fffbeb;
  color: #d97706;
}

.voice-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.mic-icon {
  font-size: 20px;
}

@keyframes pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 12px rgba(239, 68, 68, 0);
  }
}
</style>
