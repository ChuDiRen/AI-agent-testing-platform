<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="message-list-container">
    <el-card>
      <template #header>
        <div class="header">
          <h3>消息通知</h3>
          <div>
            <el-button @click="handleMarkAllRead">全部标记已读</el-button>
            <el-button type="danger" @click="handleClearAll">清空消息</el-button>
          </div>
        </div>
      </template>

      <!-- 过滤器 -->
      <div class="filter-bar">
        <el-radio-group v-model="filterType" @change="handleFilterChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="unread">未读</el-radio-button>
          <el-radio-button label="read">已读</el-radio-button>
          <el-radio-button label="system">系统通知</el-radio-button>
          <el-radio-button label="test">测试通知</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 消息列表 -->
      <el-timeline style="margin-top: 20px">
        <el-timeline-item
          v-for="msg in filteredMessages"
          :key="msg.id"
          :timestamp="msg.created_at"
          placement="top"
          :type="msg.is_read ? 'default' : 'primary'"
        >
          <el-card :class="{ 'unread-message': !msg.is_read }">
            <div class="message-content">
              <div class="message-header">
                <span class="message-title">{{ msg.title }}</span>
                <el-tag :type="getMessageTypeColor(msg.type)" size="small">{{ getMessageTypeName(msg.type) }}</el-tag>
              </div>
              <div class="message-body">{{ msg.content }}</div>
              <div class="message-actions">
                <el-button v-if="!msg.is_read" link type="primary" @click="handleMarkRead(msg.id)">标记已读</el-button>
                <el-button link type="danger" @click="handleDelete(msg.id)">删除</el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 空状态 -->
      <el-empty v-if="filteredMessages.length === 0" description="暂无消息" />

      <!-- 分页 -->
      <div class="pagination" v-if="filteredMessages.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Message {
  id: number
  title: string
  content: string
  type: string // system | test | error | info
  is_read: boolean
  created_at: string
}

// 模拟数据
const messages = ref<Message[]>([
  {
    id: 1,
    title: '系统通知',
    content: '系统将于今晚22:00进行维护，预计维护时间1小时。',
    type: 'system',
    is_read: false,
    created_at: '2025-10-03 10:30:00'
  },
  {
    id: 2,
    title: '测试报告生成完成',
    content: 'API测试报告"用户模块测试"已生成完成，通过率85%。',
    type: 'test',
    is_read: false,
    created_at: '2025-10-03 09:15:00'
  },
  {
    id: 3,
    title: '测试用例执行失败',
    content: '测试用例"登录功能测试"执行失败，请查看详细信息。',
    type: 'error',
    is_read: true,
    created_at: '2025-10-02 16:45:00'
  },
  {
    id: 4,
    title: '权限变更通知',
    content: '您的系统权限已更新，新增"测试报告导出"权限。',
    type: 'info',
    is_read: true,
    created_at: '2025-10-02 14:20:00'
  }
])

const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// 过滤后的消息
const filteredMessages = computed(() => {
  let result = messages.value
  
  if (filterType.value === 'unread') {
    result = result.filter(msg => !msg.is_read)
  } else if (filterType.value === 'read') {
    result = result.filter(msg => msg.is_read)
  } else if (filterType.value !== 'all') {
    result = result.filter(msg => msg.type === filterType.value)
  }
  
  return result
})

const total = computed(() => filteredMessages.value.length)

// 获取消息类型颜色
const getMessageTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    system: '',
    test: 'success',
    error: 'danger',
    info: 'info'
  }
  return colorMap[type] || ''
}

// 获取消息类型名称
const getMessageTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    system: '系统',
    test: '测试',
    error: '错误',
    info: '信息'
  }
  return nameMap[type] || type
}

// 标记已读
const handleMarkRead = (id: number) => {
  const msg = messages.value.find(m => m.id === id)
  if (msg) {
    msg.is_read = true
    ElMessage.success('标记成功')
  }
}

// 全部标记已读
const handleMarkAllRead = () => {
  messages.value.forEach(msg => {
    msg.is_read = true
  })
  ElMessage.success('全部消息已标记为已读')
}

// 删除消息
const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = messages.value.findIndex(m => m.id === id)
    if (index !== -1) {
      messages.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  })
}

// 清空所有消息
const handleClearAll = () => {
  ElMessageBox.confirm('确定要清空所有消息吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    messages.value = []
    ElMessage.success('已清空所有消息')
  })
}

// 过滤器变化
const handleFilterChange = () => {
  currentPage.value = 1
}
</script>

<style scoped>
.message-list-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
}

.filter-bar {
  margin-top: 20px;
}

.message-content {
  padding: 10px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.message-title {
  font-weight: bold;
  font-size: 16px;
}

.message-body {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.6;
}

.message-actions {
  display: flex;
  gap: 10px;
}

.unread-message {
  border-left: 3px solid #409eff;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>


