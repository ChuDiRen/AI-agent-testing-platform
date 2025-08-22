<template>
  <div class="common-table">
    <el-table
      ref="tableRef"
      :data="tableData"
      :loading="loading"
      :stripe="stripe"
      :border="border"
      :height="height"
      :max-height="maxHeight"
      :empty-text="emptyText"
      :row-key="rowKey"
      :tree-props="treeProps"
      :expand-row-keys="expandRowKeys"
      :default-expand-all="defaultExpandAll"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
      @row-dblclick="handleRowDblClick"
      v-bind="$attrs"
      class="table-container"
    >
      <!-- 多选列 -->
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        :selectable="selectable"
        align="center"
      />

      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="80"
        align="center"
        :index="getIndex"
      />

      <!-- 数据列 -->
      <template v-for="column in columns" :key="column.prop">
        <el-table-column
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth || 120"
          :fixed="column.fixed"
          :sortable="column.sortable"
          :align="column.align || 'left'"
          :header-align="column.headerAlign || column.align || 'left'"
          :show-overflow-tooltip="column.showOverflowTooltip !== false"
        >
          <template #default="scope" v-if="column.slot">
            <slot
              :name="column.slot"
              :row="scope.row"
              :column="scope.column"
              :$index="scope.$index"
            />
          </template>
          
          <template #default="scope" v-else-if="column.formatter">
            <span v-html="column.formatter(scope.row, scope.column, scope.row[column.prop], scope.$index)" />
          </template>
          
          <template #default="scope" v-else-if="column.render">
            <component :is="column.render" :row="scope.row" :index="scope.$index" />
          </template>
        </el-table-column>
      </template>

      <!-- 操作列 -->
      <el-table-column
        v-if="showActions"
        label="操作"
        :width="actionWidth"
        :min-width="actionMinWidth"
        fixed="right"
        align="center"
      >
        <template #default="scope">
          <slot
            name="actions"
            :row="scope.row"
            :index="scope.$index"
          >
            <el-button
              v-if="!hideEdit"
              type="primary"
              size="small"
              @click="handleEdit(scope.row, scope.$index)"
            >
              编辑
            </el-button>
            <el-button
              v-if="!hideDelete"
              type="danger"
              size="small"
              @click="handleDelete(scope.row, scope.$index)"
            >
              删除
            </el-button>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <div v-if="showPagination && pagination" class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        :background="true"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { TableColumn } from '@/api/types'

export interface TableProps {
  // 表格数据
  data: any[]
  // 表格列配置
  columns: TableColumn[]
  // 加载状态
  loading?: boolean
  // 是否显示多选
  showSelection?: boolean
  // 是否显示序号
  showIndex?: boolean
  // 是否显示操作列
  showActions?: boolean
  // 操作列宽度
  actionWidth?: number | string
  actionMinWidth?: number | string
  // 是否隐藏编辑按钮
  hideEdit?: boolean
  // 是否隐藏删除按钮
  hideDelete?: boolean
  // 表格样式
  stripe?: boolean
  border?: boolean
  height?: number | string
  maxHeight?: number | string
  // 空数据文本
  emptyText?: string
  // 树形表格
  rowKey?: string
  treeProps?: object
  expandRowKeys?: any[]
  defaultExpandAll?: boolean
  // 分页配置
  showPagination?: boolean
  pagination?: {
    page: number
    size: number
    total: number
  }
  pageSizes?: number[]
  paginationLayout?: string
  // 多选函数
  selectable?: (row: any, index: number) => boolean
}

const props = withDefaults(defineProps<TableProps>(), {
  loading: false,
  showSelection: false,
  showIndex: false,
  showActions: true,
  actionWidth: 150,
  actionMinWidth: 150,
  hideEdit: false,
  hideDelete: false,
  stripe: true,
  border: true,
  emptyText: '暂无数据',
  showPagination: true,
  pageSizes: () => [10, 20, 50, 100],
  paginationLayout: 'total, sizes, prev, pager, next, jumper'
})

const emit = defineEmits<{
  // 多选变化
  selectionChange: [selection: any[]]
  // 排序变化
  sortChange: [sort: { column: any; prop: string; order: string }]
  // 行点击
  rowClick: [row: any, column: any, event: Event]
  rowDblClick: [row: any, column: any, event: Event]
  // 操作事件
  edit: [row: any, index: number]
  delete: [row: any, index: number]
  // 分页事件
  pageChange: [page: number]
  sizeChange: [size: number]
}>()

const tableRef = ref()

// 表格数据
const tableData = computed(() => props.data || [])

// 序号计算
const getIndex = (index: number) => {
  if (!props.pagination) return index + 1
  return (props.pagination.page - 1) * props.pagination.size + index + 1
}

// 事件处理
const handleSelectionChange = (selection: any[]) => {
  emit('selectionChange', selection)
}

const handleSortChange = (sort: { column: any; prop: string; order: string }) => {
  emit('sortChange', sort)
}

const handleRowClick = (row: any, column: any, event: Event) => {
  emit('rowClick', row, column, event)
}

const handleRowDblClick = (row: any, column: any, event: Event) => {
  emit('rowDblClick', row, column, event)
}

const handleEdit = (row: any, index: number) => {
  emit('edit', row, index)
}

const handleDelete = (row: any, index: number) => {
  emit('delete', row, index)
}

const handleCurrentChange = (page: number) => {
  emit('pageChange', page)
}

const handleSizeChange = (size: number) => {
  emit('sizeChange', size)
}

// 表格方法
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

const toggleRowSelection = (row: any, selected?: boolean) => {
  tableRef.value?.toggleRowSelection(row, selected)
}

const toggleAllSelection = () => {
  tableRef.value?.toggleAllSelection()
}

const setCurrentRow = (row: any) => {
  tableRef.value?.setCurrentRow(row)
}

const clearSort = () => {
  tableRef.value?.clearSort()
}

const doLayout = () => {
  tableRef.value?.doLayout()
}

// 暴露方法
defineExpose({
  clearSelection,
  toggleRowSelection,
  toggleAllSelection,
  setCurrentRow,
  clearSort,
  doLayout,
  tableRef
})
</script>

<style scoped lang="scss">
.common-table {
  .table-container {
    width: 100%;
    
    :deep(.el-table__header-wrapper) {
      th {
        background-color: #fafafa;
        color: #606266;
        font-weight: 500;
      }
    }
    
    :deep(.el-table__body-wrapper) {
      .el-table__row {
        &:hover {
          background-color: #f5f7fa;
        }
      }
    }
    
    :deep(.el-button) {
      margin: 0 4px;
    }
  }
  
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}
</style>