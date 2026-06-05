<script setup>
defineProps({
  scenario: {
    type: Object,
    required: true,
  },
});

defineEmits(["select"]);
</script>

<template>
  <div class="scene-card" @click="$emit('select', scenario.id)">
    <div class="scene-icon">{{ scenario.icon }}</div>
    <div class="scene-info">
      <h3 class="scene-name">{{ scenario.name }}</h3>
      <p class="scene-desc">{{ scenario.description }}</p>
      <span class="scene-difficulty" :class="scenario.difficulty">
        {{ scenario.difficulty }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.scene-card {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.scene-card:hover {
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
  transform: translateY(-2px);
}

.scene-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.scene-info {
  flex: 1;
}

.scene-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #1f2937;
}

.scene-desc {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 10px;
  line-height: 1.5;
}

.scene-difficulty {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.scene-difficulty.初级 {
  background: #d1fae5;
  color: #065f46;
}

.scene-difficulty.中级 {
  background: #fef3c7;
  color: #92400e;
}

.scene-difficulty.高级 {
  background: #fce7f3;
  color: #9d174d;
}
</style>
