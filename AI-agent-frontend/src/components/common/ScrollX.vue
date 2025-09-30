<template>
  <div class="scroll-x-container" ref="containerRef">
    <div 
      class="scroll-x-content" 
      ref="contentRef"
      @wheel="handleWheel"
    >
      <slot />
    </div>
    
    <!-- 左右滚动按钮 -->
    <div v-if="showButtons" class="scroll-buttons">
      <NButton
        v-show="canScrollLeft"
        quaternary
        circle
        size="small"
        class="scroll-btn scroll-btn-left"
        @click="scrollLeft"
      >
        <template #icon>
          <Icon name="mdi:chevron-left" />
        </template>
      </NButton>
      
      <NButton
        v-show="canScrollRight"
        quaternary
        circle
        size="small"
        class="scroll-btn scroll-btn-right"
        @click="scrollRight"
      >
        <template #icon>
          <Icon name="mdi:chevron-right" />
        </template>
      </NButton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'

defineProps({
  showButtons: {
    type: Boolean,
    default: true,
  },
})

const containerRef = ref()
const contentRef = ref()
const canScrollLeft = ref(false)
const canScrollRight = ref(false)

// 滚动到指定位置
const handleScroll = (targetX, width = 0) => {
  if (!contentRef.value) return
  
  const container = contentRef.value
  const containerWidth = container.offsetWidth
  const scrollLeft = container.scrollLeft
  const maxScrollLeft = container.scrollWidth - containerWidth
  
  let newScrollLeft = targetX - containerWidth / 2 + width / 2
  newScrollLeft = Math.max(0, Math.min(newScrollLeft, maxScrollLeft))
  
  container.scrollTo({
    left: newScrollLeft,
    behavior: 'smooth',
  })
}

// 向左滚动
const scrollLeft = () => {
  if (!contentRef.value) return
  const scrollAmount = contentRef.value.offsetWidth * 0.8
  contentRef.value.scrollBy({
    left: -scrollAmount,
    behavior: 'smooth',
  })
}

// 向右滚动
const scrollRight = () => {
  if (!contentRef.value) return
  const scrollAmount = contentRef.value.offsetWidth * 0.8
  contentRef.value.scrollBy({
    left: scrollAmount,
    behavior: 'smooth',
  })
}

// 处理鼠标滚轮
const handleWheel = (event) => {
  if (!contentRef.value) return
  
  // 阻止垂直滚动，转为水平滚动
  if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
    event.preventDefault()
    contentRef.value.scrollBy({
      left: event.deltaY,
      behavior: 'auto',
    })
  }
}

// 更新滚动按钮状态
const updateScrollButtons = () => {
  if (!contentRef.value) return
  
  const container = contentRef.value
  const scrollLeft = container.scrollLeft
  const maxScrollLeft = container.scrollWidth - container.offsetWidth
  
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < maxScrollLeft
}

// 监听滚动事件
const handleScrollEvent = () => {
  updateScrollButtons()
}

// 监听窗口大小变化
const handleResize = () => {
  nextTick(() => {
    updateScrollButtons()
  })
}

onMounted(() => {
  if (contentRef.value) {
    contentRef.value.addEventListener('scroll', handleScrollEvent)
    window.addEventListener('resize', handleResize)
    updateScrollButtons()
  }
})

onUnmounted(() => {
  if (contentRef.value) {
    contentRef.value.removeEventListener('scroll', handleScrollEvent)
  }
  window.removeEventListener('resize', handleResize)
})

// 暴露方法给父组件
defineExpose({
  handleScroll,
  scrollLeft,
  scrollRight,
})
</script>

<style scoped>
.scroll-x-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.scroll-x-content {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
  display: flex;
  align-items: center;
}

.scroll-x-content::-webkit-scrollbar {
  display: none;
}

.scroll-buttons {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
}

.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: auto;
  background: var(--card-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.scroll-btn-left {
  left: 8px;
}

.scroll-btn-right {
  right: 8px;
}

.scroll-btn:hover {
  background: var(--primary-color);
  color: white;
}
</style>
