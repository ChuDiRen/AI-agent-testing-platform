<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="markdown-renderer" v-html="renderedHtml"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

interface Props {
  content: string
}

const props = defineProps<Props>()

const renderedHtml = computed(() => {
  return renderMarkdown(props.content)
})
</script>

<style scoped lang="scss">
.markdown-renderer {
  line-height: 1.6;
  color: #333;
  
  :deep(h1) {
    font-size: 2em;
    font-weight: bold;
    margin: 0.67em 0;
    border-bottom: 2px solid #eee;
    padding-bottom: 0.3em;
  }
  
  :deep(h2) {
    font-size: 1.5em;
    font-weight: bold;
    margin: 0.75em 0 0.5em;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
  }
  
  :deep(h3) {
    font-size: 1.25em;
    font-weight: bold;
    margin: 0.83em 0 0.5em;
  }
  
  :deep(p) {
    margin: 0.5em 0;
  }
  
  :deep(strong) {
    font-weight: bold;
    color: #000;
  }
  
  :deep(em) {
    font-style: italic;
  }
  
  :deep(del) {
    text-decoration: line-through;
    color: #999;
  }
  
  :deep(a) {
    color: #409eff;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  :deep(code.inline-code) {
    background: #f5f7fa;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
    color: #e96900;
  }
  
  :deep(pre.code-block) {
    background: #282c34;
    color: #abb2bf;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1em 0;
    position: relative;
    
    code {
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      font-size: 0.9em;
      line-height: 1.5;
      display: block;
      
      .keyword {
        color: #c678dd;
        font-weight: bold;
      }
      
      .string {
        color: #98c379;
      }
      
      .comment {
        color: #5c6370;
        font-style: italic;
      }
      
      .number {
        color: #d19a66;
      }
    }
  }
  
  :deep(ul), :deep(ol) {
    margin: 0.5em 0;
    padding-left: 2em;
    
    li {
      margin: 0.25em 0;
    }
  }
  
  :deep(ul) {
    list-style-type: disc;
  }
  
  :deep(ol) {
    list-style-type: decimal;
  }
  
  :deep(blockquote) {
    border-left: 4px solid #ddd;
    padding-left: 1em;
    margin: 1em 0;
    color: #666;
    font-style: italic;
  }
  
  :deep(hr) {
    border: none;
    border-top: 2px solid #eee;
    margin: 2em 0;
  }
  
  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 1em 0;
  }
  
  :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    
    th, td {
      border: 1px solid #ddd;
      padding: 8px 12px;
      text-align: left;
    }
    
    th {
      background: #f5f7fa;
      font-weight: bold;
    }
    
    tr:hover {
      background: #fafafa;
    }
  }
}

// 暗黑模式支持
@media (prefers-color-scheme: dark) {
  .markdown-renderer {
    color: #e0e0e0;
    
    :deep(h1), :deep(h2) {
      border-bottom-color: #444;
    }
    
    :deep(strong) {
      color: #fff;
    }
    
    :deep(code.inline-code) {
      background: #2d2d2d;
      color: #ff9d00;
    }
    
    :deep(blockquote) {
      border-left-color: #555;
      color: #aaa;
    }
    
    :deep(hr) {
      border-top-color: #444;
    }
    
    :deep(table) {
      th, td {
        border-color: #444;
      }
      
      th {
        background: #2d2d2d;
      }
      
      tr:hover {
        background: #333;
      }
    }
  }
}
</style>


