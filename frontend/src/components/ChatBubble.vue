<script setup>
defineProps({
  role: {
    type: String,
    required: true, // "user" or "assistant"
  },
  content: {
    type: String,
    required: true,
  },
  corrections: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div class="chat-bubble" :class="role">
    <div class="bubble-avatar">
      {{ role === "user" ? "🧑" : "🤖" }}
    </div>
    <div class="bubble-content">
      <div class="bubble-text">{{ content }}</div>
      <div v-if="corrections.length > 0" class="bubble-corrections">
        <div v-for="(c, i) in corrections" :key="i" class="correction-item">
          <span class="correction-tag" :class="c.severity">{{ c.error_type }}</span>
          <span class="correction-original">{{ c.original }}</span>
          <span class="correction-arrow">→</span>
          <span class="correction-corrected">{{ c.corrected }}</span>
          <p class="correction-explain">{{ c.explanation }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  max-width: 85%;
}

.chat-bubble.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.bubble-avatar {
  font-size: 28px;
  flex-shrink: 0;
}

.bubble-text {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.user .bubble-text {
  background: #4f46e5;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.assistant .bubble-text {
  background: #f3f4f6;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.bubble-corrections {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
}

.correction-item {
  margin-bottom: 6px;
}

.correction-item:last-child {
  margin-bottom: 0;
}

.correction-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  margin-right: 6px;
}

.correction-tag.minor {
  background: #fef3c7;
  color: #92400e;
}

.correction-tag.major {
  background: #fce7f3;
  color: #9d174d;
}

.correction-original {
  text-decoration: line-through;
  color: #ef4444;
  margin-right: 4px;
}

.correction-arrow {
  color: #6b7280;
  margin-right: 4px;
}

.correction-corrected {
  color: #059669;
  font-weight: 600;
}

.correction-explain {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}
</style>
