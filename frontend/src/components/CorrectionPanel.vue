<script setup>
defineProps({
  corrections: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div v-if="corrections.length > 0" class="correction-panel">
    <h4 class="panel-title">📝 实时纠错</h4>
    <div v-for="(c, i) in corrections" :key="i" class="correction-row">
      <span class="error-type-badge" :class="c.error_type">{{ errorTypeLabel(c.error_type) }}</span>
      <div class="correction-detail">
        <span class="from-text">{{ c.original }}</span>
        <span class="arrow">→</span>
        <span class="to-text">{{ c.corrected }}</span>
        <p class="explanation">{{ c.explanation }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    errorTypeLabel(type) {
      const labels = {
        grammar: "语法",
        pronunciation: "发音",
        expression: "表达",
        word_choice: "用词",
      };
      return labels[type] || type;
    },
  },
};
</script>

<style scoped>
.correction-panel {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 12px;
}

.correction-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: flex-start;
}

.correction-row:last-child {
  margin-bottom: 0;
}

.error-type-badge {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.error-type-badge.grammar {
  background: #fef3c7;
  color: #92400e;
}

.error-type-badge.pronunciation {
  background: #dbeafe;
  color: #1e40af;
}

.error-type-badge.expression {
  background: #fce7f3;
  color: #9d174d;
}

.error-type-badge.word_choice {
  background: #d1fae5;
  color: #065f46;
}

.correction-detail {
  flex: 1;
}

.from-text {
  text-decoration: line-through;
  color: #ef4444;
  margin-right: 4px;
}

.arrow {
  color: #6b7280;
  margin-right: 4px;
}

.to-text {
  color: #059669;
  font-weight: 600;
}

.explanation {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}
</style>
