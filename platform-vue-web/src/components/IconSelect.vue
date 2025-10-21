<template>
  <el-popover
    placement="bottom-start"
    :width="540"
    trigger="click"
    popper-class="icon-select-popover"
  >
    <template #reference>
      <el-input
        :model-value="modelValue"
        placeholder="请选择图标"
        readonly
        style="cursor: pointer;"
      >
        <template #prefix>
          <el-icon v-if="modelValue" :size="18">
            <component :is="modelValue" />
          </el-icon>
        </template>
        <template #suffix>
          <el-icon>
            <ArrowDown />
          </el-icon>
        </template>
      </el-input>
    </template>

    <!-- 图标选择器内容 -->
    <div class="icon-select-container">
      <!-- 搜索框 -->
      <el-input
        v-model="searchText"
        placeholder="搜索图标名称"
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 图标列表 -->
      <div class="icon-list">
        <div
          v-for="icon in filteredIcons"
          :key="icon"
          class="icon-item"
          :class="{ active: modelValue === icon }"
          @click="selectIcon(icon)"
        >
          <el-icon :size="24">
            <component :is="icon" />
          </el-icon>
          <span class="icon-name">{{ icon }}</span>
        </div>
        <div v-if="filteredIcons.length === 0" class="no-data">
          未找到匹配的图标
        </div>
      </div>

      <!-- 清除按钮 -->
      <div class="icon-footer">
        <el-button size="small" @click="clearIcon">清除图标</el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  ArrowDown,
  Search,
  // 系统图标
  User,
  Lock,
  Setting,
  Menu,
  HomeFilled,
  Document,
  Folder,
  Files,
  Operation,
  Tools,
  Monitor,
  Management,
  // 功能图标
  Edit,
  Delete,
  Plus,
  Minus,
  Check,
  Close,
  Upload,
  Download,
  Share,
  View,
  Hide,
  Refresh,
  // 方向图标
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  Back,
  Right,
  Top,
  Bottom,
  // 数据图标
  DataLine,
  DataBoard,
  Grid,
  List,
  TrendCharts,
  PieChart,
  // 其他常用图标
  Star,
  StarFilled,
  Message,
  Bell,
  Calendar,
  Clock,
  Location,
  Phone,
  ChatDotRound,
  Warning,
  WarningFilled,
  InfoFilled,
  SuccessFilled,
  CircleClose,
  CircleCheck,
  QuestionFilled,
  Link,
  Loading,
  Key,
  House,
  OfficeBuilding,
  School,
  ShoppingCart,
  Box,
  Goods,
  Coin,
  Sunny,
  Moon,
  MagicStick,
  Picture,
  Camera,
  VideoCamera,
  Headset,
  Service,
  Promotion,
  SetUp
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// 搜索文本
const searchText = ref('')

// 所有可用图标列表
const iconList = [
  // 系统图标
  'User',
  'Lock',
  'Setting',
  'Menu',
  'HomeFilled',
  'Document',
  'Folder',
  'Files',
  'Operation',
  'Tools',
  'Monitor',
  'Management',
  // 功能图标
  'Edit',
  'Delete',
  'Plus',
  'Minus',
  'Check',
  'Close',
  'Upload',
  'Download',
  'Share',
  'View',
  'Hide',
  'Refresh',
  // 方向图标
  'ArrowLeft',
  'ArrowRight',
  'ArrowUp',
  'ArrowDown',
  'Back',
  'Right',
  'Top',
  'Bottom',
  // 数据图标
  'DataLine',
  'DataBoard',
  'Grid',
  'List',
  'TrendCharts',
  'PieChart',
  // 其他常用图标
  'Star',
  'StarFilled',
  'Message',
  'Bell',
  'Calendar',
  'Clock',
  'Location',
  'Phone',
  'ChatDotRound',
  'Warning',
  'WarningFilled',
  'InfoFilled',
  'SuccessFilled',
  'CircleClose',
  'CircleCheck',
  'QuestionFilled',
  'Link',
  'Loading',
  'Key',
  'House',
  'OfficeBuilding',
  'School',
  'ShoppingCart',
  'Box',
  'Goods',
  'Coin',
  'Sunny',
  'Moon',
  'MagicStick',
  'Picture',
  'Camera',
  'VideoCamera',
  'Headset',
  'Service',
  'Promotion',
  'SetUp'
]

// 过滤后的图标列表
const filteredIcons = computed(() => {
  if (!searchText.value) {
    return iconList
  }
  const search = searchText.value.toLowerCase()
  return iconList.filter(icon => icon.toLowerCase().includes(search))
})

// 选择图标
const selectIcon = (icon) => {
  emit('update:modelValue', icon)
}

// 清除图标
const clearIcon = () => {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.icon-select-container {
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.search-input {
  margin-bottom: 12px;
}

.icon-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
  margin-bottom: 12px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.icon-item:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.icon-item.active {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-8);
}

.icon-name {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  text-align: center;
  word-break: break-all;
  line-height: 1.2;
}

.icon-item:hover .icon-name {
  color: var(--el-color-primary);
}

.no-data {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
}

.icon-footer {
  border-top: 1px solid var(--el-border-color);
  padding-top: 12px;
  display: flex;
  justify-content: flex-end;
}

/* 自定义滚动条 */
.icon-list::-webkit-scrollbar {
  width: 6px;
}

.icon-list::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 3px;
}

.icon-list::-webkit-scrollbar-thumb:hover {
  background-color: var(--el-border-color-dark);
}

.icon-list::-webkit-scrollbar-track {
  background-color: var(--el-fill-color-light);
  border-radius: 3px;
}
</style>

<style>
/* 全局样式 - Popover容器 */
.icon-select-popover {
  padding: 12px !important;
}
</style>

