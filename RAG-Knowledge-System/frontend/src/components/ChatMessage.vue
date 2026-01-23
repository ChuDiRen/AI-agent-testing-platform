<template>
  <div :class="['message', message.role]">
    <div class="avatar">
      <el-avatar v-if="message.role === 'user'" :icon="UserFilled" />
      <el-avatar v-else :icon="Avatar" />
    </div>
    <div class="content">
      <div class="text" v-html="formattedContent"></div>
      <div v-if="message.citations?.length" class="citations">
        <h4>参考文档：</h4>
        <div class="citation-list">
          <div
            v-for="citation in message.citations"
            :key="citation.chunk_id"
            class="citation-item"
          >
            <el-tag type="info" size="small">
              {{ citation.doc_name }}
            </el-tag>
            <span class="confidence">
              置信度: {{ (citation.confidence * 100).toFixed(0) }}%
            </span>
          </div>
        </div>
      </div>
      <div v-if="message.role === 'assistant'" class="feedback">
        <el-button
          size="small"
          :type="message.feedback === 'like' ? 'success' : ''"
          @click="handleFeedback('like')"
          :icon="Star"
        >
          有帮助
        </el-button>
        <el-button
          size="small"
          :type="message.feedback === 'dislike' ? 'danger' : ''"
          @click="handleFeedback('dislike')"
          :icon="Close"
        >
          没帮助
        </el-button>
      </div>
    </div>
    <div class="time">{{ formatTime(message.timestamp) }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserFilled, Avatar, Star, Close } from '@element-plus/icons-vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['feedback'])

const formattedContent = computed(() => {
  // 简单的markdown格式化
  let content = props.message.content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  return content
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFeedback = (type) => {
  emit('feedback', {
    messageId: props.message.id,
    feedback: type
  })
}
</script>

<style scoped>
.message {
  display: flex;
  margin-bottom: 20px;
  padding: 0 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .content {
  background: #409eff;
  color: white;
  margin-right: 12px;
}

.message.assistant .content {
  background: white;
  color: #333;
  margin-left: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar {
  flex-shrink: 0;
}

.content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.text {
  line-height: 1.5;
  word-wrap: break-word;
}

.citations {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.citations h4 {
  font-size: 12px;
  margin-bottom: 8px;
  color: #666;
}

.citation-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.confidence {
  font-size: 12px;
  color: #999;
}

.feedback {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.message.user .time {
  text-align: right;
  margin-right: 12px;
}

.message.assistant .time {
  margin-left: 12px;
}
</style>
