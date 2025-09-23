<!-- 通用表格组件 -->
<template>
  <div class="common-table">
    <!-- 表格主体 -->
    <el-table
      ref="tableRef"
      :data="data"
      :loading="loading"
      :border="border"
      :stripe="stripe"
      :highlight-current-row="highlightCurrentRow"
      :row-key="rowKey"
      :height="height"
      :max-height="maxHeight"
      :show-header="showHeader"
      :show-summary="showSummary"
      :summary-method="summaryMethod"
      :empty-text="emptyText"
      @selection-change="handleSelectionChange"
      @current-change="handleCurrentChange"
      @row-click="handleRowClick"
      @row-dblclick="handleRowDblclick"
      @sort-change="handleSortChange"
      @filter-change="handleFilterChange"
      @cell-click="handleCellClick"
      @cell-dblclick="handleCellDblclick"
      @row-contextmenu="handleRowContextmenu"
      @header-click="handleHeaderClick"
      @header-contextmenu="handleHeaderContextmenu"
      v-bind="$attrs"
    >
      <!-- 选择框列 -->
      <el-table-column 
        v-if="showSelection" 
        type="selection" 
        width="55" 
        align="center" 
        :selectable="selectable"
        :reserve-selection="reserveSelection"
      />
      
      <!-- 序号列 -->
      <el-table-column 
        v-if="showIndex" 
        type="index" 
        :label="indexLabel"
        :width="indexWidth"
        align="center"
        :index="indexMethod"
      />
      
      <!-- 动态列 -->
      <template v-for="(column, index) in processedColumns" :key="column.prop || index">
        <el-table-column
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :fixed="column.fixed"
          :sortable="column.sortable"
          :sort-method="column.sortMethod"
          :sort-by="column.sortBy"
          :sort-orders="column.sortOrders"
          :resizable="column.resizable"
          :formatter="column.formatter"
          :show-overflow-tooltip="column.showOverflowTooltip"
          :align="column.align || 'left'"
          :header-align="column.headerAlign || column.align || 'left'"
          :class-name="column.className"
          :label-class-name="column.labelClassName"
          :filters="column.filters"
          :filter-placement="column.filterPlacement"
          :filter-multiple="column.filterMultiple"
          :filter-method="column.filterMethod"
          :filtered-value="column.filteredValue"
        >
          <!-- 自定义列头 -->
          <template v-if="column.headerSlot" #header="scope">
            <slot 
              :name="column.headerSlot" 
              :column="scope.column" 
              :$index="scope.$index"
            />
          </template>
          
          <!-- 自定义列内容 -->
          <template #default="scope">
            <!-- 使用插槽 -->
            <slot 
              v-if="column.slot" 
              :name="column.slot" 
              :row="scope.row" 
              :column="scope.column" 
              :$index="scope.$index"
            />
            <!-- 使用formatter函数 -->
            <template v-else-if="column.formatter">
              {{ column.formatter(scope.row, scope.column, getCellValue(scope.row, column.prop), scope.$index) }}
            </template>
            <!-- 使用render函数 -->
            <component 
              v-else-if="column.render" 
              :is="column.render" 
              :row="scope.row" 
              :column="scope.column" 
              :index="scope.$index"
            />
            <!-- 默认显示 -->
            <template v-else>
              {{ getCellValue(scope.row, column.prop) }}
            </template>
          </template>
        </el-table-column>
      </template>
      
      <!-- 操作列 -->
      <el-table-column 
        v-if="$slots.actions"
        label="操作" 
        :width="actionWidth"
        :min-width="actionMinWidth"
        :fixed="actionFixed"
        align="center"
        class-name="table-action-column"
      >
        <template #default="scope">
          <slot 
            name="actions" 
            :row="scope.row" 
            :column="scope.column" 
            :$index="scope.$index"
          />
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页器 -->
    <div v-if="showPagination" class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="currentPageSize"
        :page-sizes="pageSizes"
        :total="pagination.total"
        :layout="paginationLayout"
        :background="paginationBackground"
        :small="paginationSmall"
        :hide-on-single-page="hideOnSinglePage"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { TableColumnCtx } from 'element-plus'

// 定义接口
export interface TableColumn {
  prop?: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: boolean | string
  sortable?: boolean | string
  sortMethod?: Function
  sortBy?: string | string[] | Function
  sortOrders?: string[]
  resizable?: boolean
  formatter?: Function
  showOverflowTooltip?: boolean
  align?: string
  headerAlign?: string
  className?: string
  labelClassName?: string
  filters?: Array<{ text: string; value: any }>
  filterPlacement?: string
  filterMultiple?: boolean
  filterMethod?: Function
  filteredValue?: any[]
  slot?: string
  headerSlot?: string
  render?: any
}

export interface PaginationData {
  page: number
  size: number
  total: number
}

// Props定义
interface Props {
  // 表格数据
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  
  // 表格配置
  border?: boolean
  stripe?: boolean
  highlightCurrentRow?: boolean
  rowKey?: string | Function
  height?: string | number
  maxHeight?: string | number
  showHeader?: boolean
  showSummary?: boolean
  summaryMethod?: Function
  emptyText?: string
  
  // 选择配置
  showSelection?: boolean
  selectable?: Function
  reserveSelection?: boolean
  
  // 序号配置
  showIndex?: boolean
  indexLabel?: string
  indexWidth?: number
  indexMethod?: Function
  
  // 操作列配置
  actionWidth?: string | number
  actionMinWidth?: string | number
  actionFixed?: boolean | string
  
  // 分页配置
  showPagination?: boolean
  pagination?: PaginationData
  pageSizes?: number[]
  paginationLayout?: string
  paginationBackground?: boolean
  paginationSmall?: boolean
  hideOnSinglePage?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  border: true,
  stripe: true,
  highlightCurrentRow: true,
  showHeader: true,
  showSummary: false,
  emptyText: '暂无数据',
  showSelection: false,
  reserveSelection: false,
  showIndex: false,
  indexLabel: '序号',
  indexWidth: 60,
  actionWidth: 150,
  actionMinWidth: 120,
  actionFixed: 'right',
  showPagination: true,
  pageSizes: () => [10, 20, 50, 100],
  paginationLayout: 'total, sizes, prev, pager, next, jumper',
  paginationBackground: true,
  paginationSmall: false,
  hideOnSinglePage: false,
  pagination: () => ({ page: 1, size: 10, total: 0 })
})

// Emits定义
const emit = defineEmits<{
  // 分页事件
  pageChange: [page: number]
  sizeChange: [size: number]
  
  // 选择事件
  selectionChange: [selection: any[]]
  currentChange: [currentRow: any, oldCurrentRow: any]
  
  // 行事件
  rowClick: [row: any, column: TableColumnCtx<any>, event: Event]
  rowDblclick: [row: any, column: TableColumnCtx<any>, event: Event]
  rowContextmenu: [row: any, column: TableColumnCtx<any>, event: Event]
  
  // 单元格事件
  cellClick: [row: any, column: TableColumnCtx<any>, cell: any, event: Event]
  cellDblclick: [row: any, column: TableColumnCtx<any>, cell: any, event: Event]
  
  // 表头事件
  headerClick: [column: TableColumnCtx<any>, event: Event]
  headerContextmenu: [column: TableColumnCtx<any>, event: Event]
  
  // 排序和筛选事件
  sortChange: [data: { column: TableColumnCtx<any>, prop: string, order: string }]
  filterChange: [filters: Record<string, any>]
}>()

// 引用
const tableRef = ref()

// 响应式数据
const currentPage = ref(props.pagination?.page || 1)
const currentPageSize = ref(props.pagination?.size || 10)

// 计算属性
const processedColumns = computed(() => {
  return props.columns.filter(column => column.label) // 过滤掉无效列
})

// 监听分页数据变化
watch(() => props.pagination, (newVal) => {
  if (newVal) {
    currentPage.value = newVal.page
    currentPageSize.value = newVal.size
  }
}, { deep: true })

// 工具函数
const getCellValue = (row: any, prop?: string) => {
  if (!prop) return ''
  return prop.split('.').reduce((obj, key) => obj?.[key], row) ?? ''
}

// 事件处理函数
const handlePageChange = (page: number) => {
  currentPage.value = page
  emit('pageChange', page)
}

const handleSizeChange = (size: number) => {
  currentPageSize.value = size
  currentPage.value = 1 // 重置到第一页
  emit('sizeChange', size)
}

const handleSelectionChange = (selection: any[]) => {
  emit('selectionChange', selection)
}

const handleCurrentChange = (currentRow: any, oldCurrentRow: any) => {
  emit('currentChange', currentRow, oldCurrentRow)
}

const handleRowClick = (row: any, column: TableColumnCtx<any>, event: Event) => {
  emit('rowClick', row, column, event)
}

const handleRowDblclick = (row: any, column: TableColumnCtx<any>, event: Event) => {
  emit('rowDblclick', row, column, event)
}

const handleRowContextmenu = (row: any, column: TableColumnCtx<any>, event: Event) => {
  emit('rowContextmenu', row, column, event)
}

const handleCellClick = (row: any, column: TableColumnCtx<any>, cell: any, event: Event) => {
  emit('cellClick', row, column, cell, event)
}

const handleCellDblclick = (row: any, column: TableColumnCtx<any>, cell: any, event: Event) => {
  emit('cellDblclick', row, column, cell, event)
}

const handleHeaderClick = (column: TableColumnCtx<any>, event: Event) => {
  emit('headerClick', column, event)
}

const handleHeaderContextmenu = (column: TableColumnCtx<any>, event: Event) => {
  emit('headerContextmenu', column, event)
}

const handleSortChange = (data: { column: TableColumnCtx<any>, prop: string, order: string }) => {
  emit('sortChange', data)
}

const handleFilterChange = (filters: Record<string, any>) => {
  emit('filterChange', filters)
}

// 暴露方法
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

const toggleRowSelection = (row: any, selected?: boolean) => {
  tableRef.value?.toggleRowSelection(row, selected)
}

const toggleAllSelection = () => {
  tableRef.value?.toggleAllSelection()
}

const toggleRowExpansion = (row: any, expanded?: boolean) => {
  tableRef.value?.toggleRowExpansion(row, expanded)
}

const setCurrentRow = (row: any) => {
  tableRef.value?.setCurrentRow(row)
}

const clearSort = () => {
  tableRef.value?.clearSort()
}

const clearFilter = (columnKeys?: string[]) => {
  tableRef.value?.clearFilter(columnKeys)
}

const doLayout = () => {
  tableRef.value?.doLayout()
}

const sort = (prop: string, order: string) => {
  tableRef.value?.sort(prop, order)
}

defineExpose({
  clearSelection,
  toggleRowSelection,
  toggleAllSelection,
  toggleRowExpansion,
  setCurrentRow,
  clearSort,
  clearFilter,
  doLayout,
  sort,
  tableRef
})
</script>

<style scoped lang="scss">
.common-table {
  .table-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  :deep(.table-action-column) {
    .cell {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      
      .el-button {
        margin: 0;
      }
    }
  }
  
  :deep(.el-table) {
    .el-table__empty-block {
      min-height: 200px;
    }
  }
}
</style>