<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="virtual-table-wrapper" v-loading="loading">
    <div class="virtual-table" ref="containerRef" @scroll="handleScroll">
      <div class="virtual-table-phantom" :style="{ height: phantomHeight + 'px' }"></div>
      <div class="virtual-table-content" :style="{ transform: `translateY(${offsetY}px)` }">
        <table class="table">
          <thead>
            <tr>
              <th v-if="showSelection" style="width: 55px">
                <input type="checkbox" @change="handleSelectAll" :checked="isAllSelected" />
              </th>
              <th v-for="column in columns" :key="column.prop" :style="{ width: column.width }">
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(item, index) in visibleData" 
              :key="getRowKey(item, startIndex + index)" 
              @click="handleRowClick(item)"
              :class="{ 'selected-row': isRowSelected(item) }"
            >
              <td v-if="showSelection" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="isRowSelected(item)" 
                  @change="handleRowSelect(item)"
                />
              </td>
              <td v-for="column in columns" :key="column.prop">
                <slot :name="column.prop" :row="item" :index="startIndex + index">
                  {{ item[column.prop] }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Column {
  prop: string
  label: string
  width?: string
}

interface Props {
  data: any[]
  columns: Column[]
  rowHeight?: number
  buffer?: number
  showSelection?: boolean
  rowKey?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  rowHeight: 50,
  buffer: 10,
  showSelection: false,
  rowKey: 'id',
  loading: false
})

const emit = defineEmits<{
  'row-click': [row: any]
  'selection-change': [rows: any[]]
}>()

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)
const containerHeight = ref(0)
const selectedRows = ref<Set<any>>(new Set())

// 计算可见区域的数据
const visibleCount = computed(() => Math.ceil(containerHeight.value / props.rowHeight) + props.buffer * 2)
const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / props.rowHeight) - props.buffer))
const endIndex = computed(() => Math.min(props.data.length, startIndex.value + visibleCount.value))
const visibleData = computed(() => props.data.slice(startIndex.value, endIndex.value))

// 幽灵元素高度（用于撑开滚动条）
const phantomHeight = computed(() => props.data.length * props.rowHeight)

// 偏移量
const offsetY = computed(() => startIndex.value * props.rowHeight)

// 是否全选
const isAllSelected = computed(() => {
  return props.data.length > 0 && selectedRows.value.size === props.data.length
})

// 获取行的唯一键
const getRowKey = (row: any, index: number) => {
  return props.rowKey ? row[props.rowKey] : index
}

// 判断行是否被选中
const isRowSelected = (row: any) => {
  const key = getRowKey(row, 0)
  return selectedRows.value.has(key)
}

// 处理滚动事件
const handleScroll = (e: Event) => {
  const target = e.target as HTMLElement
  scrollTop.value = target.scrollTop
}

// 处理行点击
const handleRowClick = (row: any) => {
  emit('row-click', row)
}

// 处理行选择
const handleRowSelect = (row: any) => {
  const key = getRowKey(row, 0)
  if (selectedRows.value.has(key)) {
    selectedRows.value.delete(key)
  } else {
    selectedRows.value.add(key)
  }
  emitSelectionChange()
}

// 处理全选
const handleSelectAll = (e: Event) => {
  const checked = (e.target as HTMLInputElement).checked
  if (checked) {
    props.data.forEach(row => {
      const key = getRowKey(row, 0)
      selectedRows.value.add(key)
    })
  } else {
    selectedRows.value.clear()
  }
  emitSelectionChange()
}

// 触发选择变化事件
const emitSelectionChange = () => {
  const selected = props.data.filter(row => {
    const key = getRowKey(row, 0)
    return selectedRows.value.has(key)
  })
  emit('selection-change', selected)
}

// 更新容器高度
const updateContainerHeight = () => {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
  }
}

// 清空选择
const clearSelection = () => {
  selectedRows.value.clear()
  emitSelectionChange()
}

// 暴露方法
defineExpose({
  clearSelection
})

// 监听窗口大小变化
let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  updateContainerHeight()
  
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateContainerHeight()
    })
    resizeObserver.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
  }
})

// 监听数据变化，重置滚动位置
watch(() => props.data.length, () => {
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
    scrollTop.value = 0
  }
  // 清理无效的选择
  const validKeys = new Set(props.data.map(row => getRowKey(row, 0)))
  selectedRows.value.forEach(key => {
    if (!validKeys.has(key)) {
      selectedRows.value.delete(key)
    }
  })
})
</script>

<style scoped>
.virtual-table-wrapper {
  height: 100%;
  position: relative;
}

.virtual-table {
  height: 100%;
  overflow-y: auto;
  position: relative;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.virtual-table-phantom {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  z-index: -1;
}

.virtual-table-content {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
}

.table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f5f7fa;
}

.table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #909399;
  border-bottom: 1px solid #ebeef5;
  white-space: nowrap;
}

.table th input[type="checkbox"] {
  cursor: pointer;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.table td input[type="checkbox"] {
  cursor: pointer;
}

.table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.table tbody tr:hover {
  background-color: #f5f7fa;
}

.table tbody tr.selected-row {
  background-color: #ecf5ff;
}

.table tbody tr.selected-row:hover {
  background-color: #d9ecff;
}

.virtual-table::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.virtual-table::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 4px;
}

.virtual-table::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

.virtual-table::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}
</style>

