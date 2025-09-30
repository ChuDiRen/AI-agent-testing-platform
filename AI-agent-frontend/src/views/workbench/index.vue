<template>
  <AppPage :show-footer="false">
    <div class="workbench">
      <!-- 欢迎区域 -->
      <NCard class="welcome-card">
        <div class="welcome-content">
          <div class="welcome-info">
            <NAvatar
              round
              :size="60"
              :src="userStore.avatar || 'https://avatars.githubusercontent.com/u/54677442?v=4'"
              class="welcome-avatar"
            />
            <div class="welcome-text">
              <h2 class="welcome-title">
                欢迎回来，{{ userStore.name || 'admin' }}！
              </h2>
              <p class="welcome-subtitle">
                今天是 {{ currentDate }}，让我们开始高效的工作吧！
              </p>
            </div>
          </div>
          <NSpace :size="12" :wrap="false" class="welcome-stats">
            <NStatistic v-for="item in statisticData" :key="item.id" v-bind="item" />
          </NSpace>
        </div>
      </NCard>

      <!-- 项目区域 -->
      <NCard
        title="项目"
        size="small"
        :segmented="true"
        class="project-card"
      >
        <template #header-extra>
          <NButton text type="primary">更多</NButton>
        </template>
        <div class="project-grid">
          <NCard
            v-for="i in 9"
            :key="i"
            class="project-item"
            hoverable
            title="AI Agent Testing Platform"
            size="small"
          >
            <p class="project-description">
              一个基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台
            </p>
          </NCard>
        </div>
      </NCard>
    </div>
  </AppPage>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store'
import { AppPage } from '@/components'
import { formatDate } from '@/utils'

defineOptions({ name: '工作台' })

const userStore = useUserStore()

// 当前日期
const currentDate = computed(() => {
  return formatDate(new Date(), 'YYYY年MM月DD日')
})

// 统计数据
const statisticData = computed(() => [
  {
    id: 0,
    label: '项目数量',
    value: '25',
  },
  {
    id: 1,
    label: '即将到期',
    value: '4/16',
  },
  {
    id: 2,
    label: '系统消息',
    value: '12',
  },
  {
    id: 3,
    label: '待处理',
    value: '5',
  },
])
</script>

<style scoped>
.workbench {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.welcome-card {
  border-radius: 10px;
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

.welcome-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-avatar {
  flex-shrink: 0;
}

.welcome-text {
  min-width: 0;
}

.welcome-title {
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-1);
}

.welcome-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-color-2);
  opacity: 0.8;
}

.welcome-stats {
  flex-shrink: 0;
}

.project-card {
  margin-top: 15px;
  border-radius: 10px;
}

.project-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
}

.project-item {
  width: 300px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.project-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-color-2);
  opacity: 0.8;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .welcome-stats {
    align-self: stretch;
  }

  .welcome-stats .n-space {
    justify-content: space-between;
  }

  .project-grid {
    justify-content: center;
  }

  .project-item {
    width: 100%;
    max-width: 400px;
  }
}

@media (max-width: 480px) {
  .welcome-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 12px;
  }

  .welcome-stats .n-space {
    flex-wrap: wrap;
    gap: 8px;
  }

  .project-item {
    width: 100%;
  }
}
</style>
