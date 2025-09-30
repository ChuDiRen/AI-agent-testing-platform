<template>
  <div class="tags-wrapper">
    <ScrollX ref="scrollXRef" class="tags-scroll">
      <NTag
        v-for="tag in tagsStore.tags"
        :key="tag.path"
        :type="isActive(tag.path) ? 'primary' : 'default'"
        :closable="tag.closable && tagsStore.tags.length > 1"
        class="tag-item"
        @click="handleTagClick(tag)"
        @close="handleTagClose(tag)"
        @contextmenu.prevent="handleContextMenu($event, tag)"
      >
        <Icon v-if="tag.icon" :name="tag.icon" class="tag-icon" />
        {{ tag.title }}
      </NTag>
    </ScrollX>

    <!-- 右键菜单 -->
    <NDropdown
      placement="bottom-start"
      trigger="manual"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :options="contextMenuOptions"
      :show="contextMenu.show"
      :on-clickoutside="hideContextMenu"
      @select="handleContextMenuSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTagsStore } from '@/store'
import { Icon } from '@iconify/vue'
import ScrollX from '@/components/common/ScrollX.vue'

const route = useRoute()
const router = useRouter()
const tagsStore = useTagsStore()

const scrollXRef = ref()
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  currentTag: null,
})

// 判断是否为当前激活标签
const isActive = (path) => {
  return route.path === path
}

// 右键菜单选项
const contextMenuOptions = computed(() => [
  {
    label: '刷新页面',
    key: 'refresh',
    icon: () => h(Icon, { name: 'mdi:refresh' }),
  },
  {
    type: 'divider',
  },
  {
    label: '关闭当前',
    key: 'close',
    icon: () => h(Icon, { name: 'mdi:close' }),
    disabled: !contextMenu.value.currentTag?.closable || tagsStore.tags.length <= 1,
  },
  {
    label: '关闭其他',
    key: 'close-others',
    icon: () => h(Icon, { name: 'mdi:close-circle-multiple' }),
    disabled: tagsStore.tags.length <= 1,
  },
  {
    label: '关闭所有',
    key: 'close-all',
    icon: () => h(Icon, { name: 'mdi:close-circle-multiple-outline' }),
    disabled: tagsStore.tags.filter(tag => tag.closable).length === 0,
  },
])

// 点击标签
const handleTagClick = (tag) => {
  if (route.path !== tag.path) {
    router.push(tag.path)
  }
}

// 关闭标签
const handleTagClose = (tag) => {
  const index = tagsStore.tags.findIndex(t => t.path === tag.path)
  tagsStore.removeTag(tag.path)
  
  // 如果关闭的是当前页面，跳转到其他页面
  if (route.path === tag.path) {
    const nextTag = tagsStore.tags[index] || tagsStore.tags[index - 1] || tagsStore.tags[0]
    if (nextTag) {
      router.push(nextTag.path)
    }
  }
}

// 右键菜单
const handleContextMenu = (event, tag) => {
  event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    currentTag: tag,
  }
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenu.value.show = false
}

// 右键菜单选择
const handleContextMenuSelect = (key) => {
  const { currentTag } = contextMenu.value
  
  switch (key) {
    case 'refresh':
      if (route.path === currentTag.path) {
        window.location.reload()
      } else {
        router.push(currentTag.path).then(() => {
          window.location.reload()
        })
      }
      break
      
    case 'close':
      handleTagClose(currentTag)
      break
      
    case 'close-others':
      tagsStore.removeOtherTags(currentTag.path)
      if (route.path !== currentTag.path) {
        router.push(currentTag.path)
      }
      break
      
    case 'close-all':
      tagsStore.removeAllTags()
      const firstTag = tagsStore.tags[0]
      if (firstTag) {
        router.push(firstTag.path)
      }
      break
  }
  
  hideContextMenu()
}

// 滚动到当前激活的标签
const scrollToActiveTag = async () => {
  await nextTick()
  const activeTag = scrollXRef.value?.$el?.querySelector('.tag-item.n-tag--primary')
  if (activeTag && scrollXRef.value) {
    const { offsetLeft: x, offsetWidth: width } = activeTag
    scrollXRef.value.handleScroll(x + width / 2, width)
  }
}

// 监听路由变化，滚动到激活标签
watch(() => route.path, scrollToActiveTag, { flush: 'post' })
</script>

<style scoped>
.tags-wrapper {
  height: 100%;
  display: flex;
  align-items: center;
  background: var(--card-color);
}

.tags-scroll {
  flex: 1;
  height: 100%;
}

.tags-scroll :deep(.scroll-x-content) {
  gap: 8px;
  padding: 0 16px;
}

.tag-item {
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
  border-radius: 6px;
  font-size: 12px;
}

.tag-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-icon {
  margin-right: 4px;
  font-size: 12px;
}

/* 标签关闭按钮样式优化 */
:deep(.n-tag__close) {
  margin-left: 6px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

:deep(.n-tag__close:hover) {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}
</style>
