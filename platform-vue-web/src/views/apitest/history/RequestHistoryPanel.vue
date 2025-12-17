<template>
  <div class="history-panel">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="history-tabs">
      <el-tab-pane label="最近请求" name="recent">
        <div class="history-list">
          <div
            v-for="item in recentList"
            :key="item.id"
            class="history-item"
            @click="handleSelect(item)"
          >
            <div class="item-header">
              <span class="method-tag" :class="getMethodClass(item.request_method)">
                {{ item.request_method }}
              </span>
              <span class="status-code" :class="getStatusClass(item.response_status)">
                {{ item.response_status || '-' }}
              </span>
              <span class="response-time">{{ item.response_time }}ms</span>
              <el-icon
                class="favorite-icon"
                :class="{ active: item.is_favorite === 1 }"
                @click.stop="handleToggleFavorite(item)"
              >
                <StarFilled v-if="item.is_favorite === 1" />
                <Star v-else />
              </el-icon>
            </div>
            <div class="item-url" :title="item.request_url">{{ item.request_url }}</div>
            <div class="item-time">{{ formatTime(item.create_time) }}</div>
          </div>
          <el-empty v-if="recentList.length === 0" description="暂无请求历史" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="收藏" name="favorites">
        <div class="history-list">
          <div
            v-for="item in favoriteList"
            :key="item.id"
            class="history-item"
            @click="handleSelect(item)"
          >
            <div class="item-header">
              <span class="method-tag" :class="getMethodClass(item.request_method)">
                {{ item.request_method }}
              </span>
              <span class="api-name">{{ item.api_name || '未命名' }}</span>
              <el-icon
                class="favorite-icon active"
                @click.stop="handleToggleFavorite(item)"
              >
                <StarFilled />
              </el-icon>
            </div>
            <div class="item-url" :title="item.request_url">{{ item.request_url }}</div>
          </div>
          <el-empty v-if="favoriteList.length === 0" description="暂无收藏" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 底部操作 -->
    <div class="panel-footer">
      <el-button link size="small" @click="handleClear">清空历史</el-button>
      <el-button link size="small" @click="handleViewAll">查看全部</el-button>
    </div>

    <!-- 清空确认对话框 -->
    <el-dialog v-model="clearDialogVisible" title="清空历史" width="400px">
      <el-form label-width="100px">
        <el-form-item label="保留收藏">
          <el-switch v-model="clearOptions.keep_favorites" />
        </el-form-item>
        <el-form-item label="保留天数">
          <el-input-number v-model="clearOptions.days" :min="0" :max="365" />
          <span class="ml-2">天（0表示全部清空）</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleClearConfirm">确认清空</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { queryRecent, queryFavorites, toggleFavorite, clearHistory } from './apiRequestHistory'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['select', 'view-all'])

const activeTab = ref('recent')
const recentList = ref([])
const favoriteList = ref([])

// 清空选项
const clearDialogVisible = ref(false)
const clearOptions = reactive({
  keep_favorites: true,
  days: 7
})

// 加载最近请求
const loadRecent = async () => {
  if (!props.projectId) return
  try {
    const res = await queryRecent(props.projectId, 20)
    if (res.data.code === 200) {
      recentList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载最近请求失败:', error)
  }
}

// 加载收藏
const loadFavorites = async () => {
  if (!props.projectId) return
  try {
    const res = await queryFavorites(props.projectId)
    if (res.data.code === 200) {
      favoriteList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载收藏失败:', error)
  }
}

// 加载数据
const loadData = () => {
  loadRecent()
  loadFavorites()
}

// 获取方法类名
const getMethodClass = (method) => {
  const classMap = {
    GET: 'method-get',
    POST: 'method-post',
    PUT: 'method-put',
    DELETE: 'method-delete',
    PATCH: 'method-patch'
  }
  return classMap[method?.toUpperCase()] || 'method-get'
}

// 获取状态码类名
const getStatusClass = (status) => {
  if (!status) return ''
  if (status >= 200 && status < 300) return 'status-success'
  if (status >= 400) return 'status-error'
  return 'status-warning'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString()
}

// 选择历史记录
const handleSelect = (item) => {
  emit('select', item)
}

// 切换收藏
const handleToggleFavorite = async (item) => {
  try {
    const res = await toggleFavorite(item.id)
    if (res.data.code === 200) {
      item.is_favorite = item.is_favorite === 1 ? 0 : 1
      ElMessage.success(res.data.msg)
      loadFavorites()
    }
  } catch (error) {
    console.error('切换收藏失败:', error)
  }
}

// 清空历史
const handleClear = () => {
  clearDialogVisible.value = true
}

const handleClearConfirm = async () => {
  try {
    const res = await clearHistory({
      project_id: props.projectId,
      ...clearOptions
    })
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
      clearDialogVisible.value = false
      loadData()
    }
  } catch (error) {
    console.error('清空历史失败:', error)
  }
}

// 查看全部
const handleViewAll = () => {
  emit('view-all')
}

// 监听项目变化
watch(() => props.projectId, () => {
  loadData()
})

onMounted(() => {
  loadData()
})

// 暴露方法
defineExpose({
  reload: loadData
})
</script>

<style scoped>
.history-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-tabs {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.history-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.history-list {
  padding: 8px;
}

.history-item {
  padding: 10px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.method-tag {
  font-size: 11px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 3px;
  color: white;
}

.method-get { background: #67C23A; }
.method-post { background: #E6A23C; }
.method-put { background: #409EFF; }
.method-delete { background: #F56C6C; }
.method-patch { background: #909399; }

.status-code {
  font-size: 12px;
  font-weight: bold;
}

.status-success { color: #67C23A; }
.status-error { color: #F56C6C; }
.status-warning { color: #E6A23C; }

.response-time {
  font-size: 12px;
  color: #909399;
}

.api-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.favorite-icon {
  cursor: pointer;
  color: #C0C4CC;
  margin-left: auto;
}

.favorite-icon.active {
  color: #E6A23C;
}

.item-url {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.item-time {
  font-size: 11px;
  color: #909399;
}

.panel-footer {
  padding: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
}

.ml-2 {
  margin-left: 8px;
}
</style>
