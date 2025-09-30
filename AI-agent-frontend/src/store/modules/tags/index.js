import { defineStore } from 'pinia'

export const useTagsStore = defineStore('tags', {
  state() {
    return {
      tags: [],
      activeTag: null,
    }
  },
  
  getters: {
    // 获取所有标签
    allTags: (state) => state.tags,
    
    // 获取当前激活的标签
    currentTag: (state) => state.activeTag,
    
    // 判断是否存在某个标签
    hasTag: (state) => (path) => {
      return state.tags.some(tag => tag.path === path)
    },
  },
  
  actions: {
    // 添加标签
    addTag(tag) {
      if (!this.hasTag(tag.path)) {
        this.tags.push({
          name: tag.name,
          path: tag.path,
          title: tag.title || tag.name,
          icon: tag.icon,
          closable: tag.closable !== false,
        })
      }
      this.setActiveTag(tag.path)
    },
    
    // 移除标签
    removeTag(path) {
      const index = this.tags.findIndex(tag => tag.path === path)
      if (index > -1) {
        this.tags.splice(index, 1)
        
        // 如果移除的是当前激活的标签，需要激活其他标签
        if (this.activeTag?.path === path) {
          const newActiveTag = this.tags[index] || this.tags[index - 1]
          this.setActiveTag(newActiveTag?.path)
        }
      }
    },
    
    // 移除其他标签
    removeOtherTags(path) {
      this.tags = this.tags.filter(tag => tag.path === path || !tag.closable)
      this.setActiveTag(path)
    },
    
    // 移除所有标签
    removeAllTags() {
      this.tags = this.tags.filter(tag => !tag.closable)
      this.activeTag = null
    },
    
    // 设置激活标签
    setActiveTag(path) {
      this.activeTag = this.tags.find(tag => tag.path === path) || null
    },
    
    // 重置标签
    resetTags() {
      this.tags = []
      this.activeTag = null
    },
  },
  
  persist: {
    key: 'tags-store',
    storage: sessionStorage,
    paths: ['tags'],
  },
})
