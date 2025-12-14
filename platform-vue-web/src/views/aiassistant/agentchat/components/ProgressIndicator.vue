<template>
  <div class="progress-indicator" v-if="isGenerating">
    <div class="progress-header">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>AI正在生成测试用例...</span>
    </div>
    <div class="stages">
      <div 
        v-for="stage in stages" 
        :key="stage.name"
        class="stage-item"
        :class="{ 
          active: stage.name === currentStage,
          completed: isStageCompleted(stage.name)
        }"
      >
        <el-icon :class="stage.iconClass">
          <component :is="stage.icon" />
        </el-icon>
        <span class="stage-label">{{ stage.label }}</span>
        <el-progress 
          v-if="stage.name === currentStage" 
          :percentage="progress" 
          :show-text="false"
          :stroke-width="4"
          class="stage-progress"
        />
        <el-icon v-if="isStageCompleted(stage.name)" class="check-icon">
          <Check />
        </el-icon>
      </div>
    </div>
    <div class="progress-footer" v-if="message">
      <span>{{ message }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading, Check, Search, Edit, Document, CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  isGenerating: { type: Boolean, default: false },
  currentStage: { type: String, default: 'init' },
  progress: { type: Number, default: 0 },
  message: { type: String, default: '' },
  completedStages: { type: Array, default: () => [] }
})

const stages = [
  { name: 'analyzing', label: '需求分析', icon: Search, iconClass: 'icon-blue' },
  { name: 'designing', label: '测试点设计', icon: Edit, iconClass: 'icon-purple' },
  { name: 'writing', label: '用例编写', icon: Document, iconClass: 'icon-green' },
  { name: 'reviewing', label: '质量评审', icon: CircleCheck, iconClass: 'icon-orange' }
]


const isStageCompleted = (stageName) => {
  return props.completedStages.includes(stageName)
}
</script>

<style scoped>
.progress-indicator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 12px 0;
  color: white;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 500;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.stages {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.stage-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.stage-item.active {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.02);
}

.stage-item.completed {
  background: rgba(255, 255, 255, 0.2);
}

.stage-label {
  font-size: 12px;
  text-align: center;
}

.stage-progress {
  width: 100%;
  margin-top: 4px;
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: #67c23a;
}

.icon-blue { color: #409eff; }
.icon-purple { color: #9b59b6; }
.icon-green { color: #67c23a; }
.icon-orange { color: #e6a23c; }

.progress-footer {
  margin-top: 12px;
  font-size: 12px;
  opacity: 0.9;
  text-align: center;
}
</style>
