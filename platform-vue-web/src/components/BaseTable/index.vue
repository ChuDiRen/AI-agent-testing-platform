<template>
  <div class="base-table">
    <!-- Header / Toolbar -->
    <div v-if="$slots.header || title || showExpandToggle" class="table-header">
      <div class="header-title">{{ title }}</div>
      <div class="header-actions">
        <el-button v-if="showExpandToggle" @click="toggleExpandAll">
          <el-icon><Sort /></el-icon>
          {{ isExpanded ? '折叠' : '展开' }}
        </el-button>
        <slot name="header" />
      </div>
    </div>

    <!-- Table -->
    <el-table
      ref="elTableRef"
      v-loading="loading"
      :data="data"
      :row-key="rowKey"
      style="width: 100%"
      border
      v-bind="$attrs"
    >
      <slot />
      <template #empty>
        <el-empty description="暂无数据" />
      </template>
    </el-table>

    <!-- Pagination -->
    <BasePagination
      v-if="showPagination"
      v-model="paginationInfo"
      :total="total"
      @change="handlePaginationChange"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import BasePagination from '@/components/BasePagination/index.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  data: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  pagination: {
    type: Object,
    default: () => ({ page: 1, limit: 10 })
  },
  showExpandToggle: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:pagination', 'refresh'])

const paginationInfo = computed({
  get: () => props.pagination,
  set: (val) => emit('update:pagination', val)
})

const handlePaginationChange = () => {
  emit('refresh')
}

// 展开/折叠逻辑
const elTableRef = ref(null)
const isExpanded = ref(false)

const toggleRowExpansion = (children, expanded) => {
  children.forEach(item => {
    if (elTableRef.value) {
      elTableRef.value.toggleRowExpansion(item, expanded)
    }
    if (item.children && item.children.length > 0) {
      toggleRowExpansion(item.children, expanded)
    }
  })
}

const toggleExpandAll = () => {
  isExpanded.value = !isExpanded.value
  toggleRowExpansion(props.data, isExpanded.value)
}
</script>

<style scoped>
.base-table {
  background: var(--bg-card);
  padding: 20px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 大屏幕适配 */
@media (min-width: 1920px) {
  .base-table {
    padding: 24px;
  }
  
  .header-title {
    font-size: 18px;
  }
}

/* 超大屏幕适配 */
@media (min-width: 2560px) {
  .base-table {
    padding: 32px;
  }
  
  .header-title {
    font-size: 20px;
  }
}
</style>
