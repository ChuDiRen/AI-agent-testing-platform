<template>
  <div class="json-viewer">
    <div class="json-toolbar" v-if="showToolbar">
      <el-button size="small" @click="expandAll">展开全部</el-button>
      <el-button size="small" @click="collapseAll">折叠全部</el-button>
      <el-button size="small" type="primary" @click="copyJson">复制</el-button>
    </div>
    <div class="json-content">
      <json-node 
        :data="parsedData" 
        :depth="0" 
        :path="'root'"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: {
    type: [Object, Array, String],
    default: null
  },
  showToolbar: {
    type: Boolean,
    default: false
  },
  defaultExpanded: {
    type: Boolean,
    default: true
  }
})

const parsedData = computed(() => {
  if (typeof props.data === 'string') {
    try {
      return JSON.parse(props.data)
    } catch {
      return props.data
    }
  }
  return props.data
})

// 全局控制信号：'expand' | 'collapse' | null
const globalSignal = ref(props.defaultExpanded ? 'expand' : 'collapse')

provide('globalSignal', globalSignal)

const expandAll = () => {
  globalSignal.value = 'expand'
  // 强制重置信号以便下次再次触发
  setTimeout(() => { globalSignal.value = null }, 100)
}

const collapseAll = () => {
  globalSignal.value = 'collapse'
  setTimeout(() => { globalSignal.value = null }, 100)
}

const copyJson = () => {
  const text = JSON.stringify(parsedData.value, null, 2)
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<script>
// 递归子组件
import { h, inject, ref, computed, watch } from 'vue'

const JsonNode = {
  name: 'JsonNode',
  props: {
    data: [Object, Array, String, Number, Boolean, null],
    depth: Number,
    path: String,
    keyName: String,
    isLast: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const globalSignal = inject('globalSignal')
    
    const isExpanded = ref(globalSignal.value === 'expand')
    
    // 监听全局信号
    watch(globalSignal, (val) => {
      if (val === 'expand') isExpanded.value = true
      if (val === 'collapse') isExpanded.value = false
    })

    const toggle = () => {
      isExpanded.value = !isExpanded.value
    }

    const isObject = computed(() => props.data !== null && typeof props.data === 'object')
    const isArray = computed(() => Array.isArray(props.data))
    const itemCount = computed(() => {
      if (isArray.value) return props.data.length
      if (isObject.value) return Object.keys(props.data).length
      return 0
    })

    const valueType = computed(() => {
      if (props.data === null) return 'null'
      return typeof props.data
    })

    const formatValue = (val) => {
      if (typeof val === 'string') return `"${val}"`
      if (val === null) return 'null'
      return String(val)
    }

    return () => {
      const { data, depth, keyName, isLast } = props
      const indent = { marginLeft: depth > 0 ? '20px' : '0' }

      // 渲染对象或数组
      if (isObject.value) {
        const openBracket = isArray.value ? '[' : '{'
        const closeBracket = isArray.value ? ']' : '}'
        
        // 展开状态渲染
        if (isExpanded.value) {
          const children = []
          
          if (isArray.value) {
            data.forEach((item, index) => {
              children.push(h(JsonNode, {
                key: index,
                data: item,
                depth: depth + 1,
                path: `${props.path}.${index}`,
                isLast: index === data.length - 1
              }))
            })
          } else {
            Object.keys(data).forEach((key, index, arr) => {
              children.push(h(JsonNode, {
                key: key,
                data: data[key],
                keyName: key,
                depth: depth + 1,
                path: `${props.path}.${key}`,
                isLast: index === arr.length - 1
              }))
            })
          }

          return h('div', { class: 'json-node', style: indent }, [
            h('span', { class: 'json-toggle', onClick: toggle }, '▼'),
            keyName && h('span', { class: 'json-key' }, `"${keyName}": `),
            h('span', { class: 'json-bracket' }, openBracket),
            h('div', { class: 'json-children' }, children),
            h('span', { class: 'json-bracket' }, closeBracket),
            !isLast && h('span', { class: 'json-comma' }, ',')
          ])
        } 
        
        // 折叠状态渲染
        else {
          return h('div', { class: 'json-node', style: indent }, [
            h('span', { class: 'json-toggle', onClick: toggle }, '▶'),
            keyName && h('span', { class: 'json-key' }, `"${keyName}": `),
            h('span', { class: 'json-bracket' }, openBracket),
            h('span', { class: 'json-count', onClick: toggle }, ` ${itemCount.value} ${isArray.value ? 'items' : 'keys'} `),
            h('span', { class: 'json-bracket' }, closeBracket),
            !isLast && h('span', { class: 'json-comma' }, ',')
          ])
        }
      }

      // 渲染基本类型
      return h('div', { class: 'json-node', style: indent }, [
        keyName && h('span', { class: 'json-key' }, `"${keyName}": `),
        h('span', { class: `json-value json-${valueType.value}` }, formatValue(data)),
        !isLast && h('span', { class: 'json-comma' }, ',')
      ])
    }
  }
}
</script>

<style scoped>
.json-viewer {
  background: #1e1e1e;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.json-toolbar {
  padding: 8px 12px;
  background: #2d2d2d;
  border-bottom: 1px solid #3d3d3d;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.json-content {
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow: auto;
  max-height: 500px;
  color: #d4d4d4;
}

:deep(.json-node) {
  white-space: nowrap;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}

:deep(.json-children) {
  width: 100%;
}

:deep(.json-toggle) {
  cursor: pointer;
  color: #858585;
  margin-right: 4px;
  user-select: none;
  font-size: 10px;
  line-height: 1.8;
  width: 12px;
  display: inline-block;
  text-align: center;
}

:deep(.json-toggle:hover) {
  color: #fff;
}

:deep(.json-key) {
  color: #9cdcfe;
}

:deep(.json-colon) {
  color: #d4d4d4;
  margin-right: 4px;
}

:deep(.json-bracket) {
  color: #ffd700;
}

:deep(.json-count) {
  color: #6a9955;
  font-style: italic;
  cursor: pointer;
  background: #2d2d2d;
  border-radius: 4px;
  padding: 0 4px;
  margin: 0 4px;
}

:deep(.json-comma) {
  color: #d4d4d4;
}

:deep(.json-value) {
  margin-left: 4px;
}

:deep(.json-string) {
  color: #ce9178;
}

:deep(.json-number) {
  color: #b5cea8;
}

:deep(.json-boolean) {
  color: #569cd6;
}

:deep(.json-null) {
  color: #569cd6;
  font-style: italic;
}
</style>
