<template>
  <div class="code-editor-wrapper">
    <textarea ref="textareaRef"></textarea>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import CodeMirror from 'codemirror'
import 'codemirror/lib/codemirror.css'
import 'codemirror/mode/python/python.js'
import 'codemirror/mode/javascript/javascript.js'
import 'codemirror/addon/edit/matchbrackets.js'
import 'codemirror/addon/edit/closebrackets.js'
import 'codemirror/addon/selection/active-line.js'
import 'codemirror/addon/fold/foldcode.js'
import 'codemirror/addon/fold/foldgutter.js'
import 'codemirror/addon/fold/brace-fold.js'
import 'codemirror/addon/fold/indent-fold.js'
import 'codemirror/addon/fold/foldgutter.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  mode: {
    type: String,
    default: 'python'
  },
  theme: {
    type: String,
    default: 'default'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: '400px'
  },
  placeholder: {
    type: String,
    default: '请输入代码...'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const textareaRef = ref(null)
let editor = null

onMounted(() => {
  if (!textareaRef.value) return

  editor = CodeMirror.fromTextArea(textareaRef.value, {
    mode: props.mode,
    theme: props.theme,
    lineNumbers: true,
    lineWrapping: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    styleActiveLine: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    readOnly: props.readonly,
    foldGutter: true,
    gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
    extraKeys: {
      'Tab': (cm) => {
        if (cm.somethingSelected()) {
          cm.indentSelection('add')
        } else {
          cm.replaceSelection('    ', 'end')
        }
      }
    }
  })

  // 设置高度
  editor.setSize(null, props.height)

  // 设置初始值
  if (props.modelValue) {
    editor.setValue(props.modelValue)
  }

  // 监听编辑器内容变化
  editor.on('change', (cm) => {
    const value = cm.getValue()
    emit('update:modelValue', value)
    emit('change', value)
  })

  // 设置占位符
  if (!props.modelValue && props.placeholder) {
    const placeholderElement = document.createElement('div')
    placeholderElement.className = 'CodeMirror-placeholder'
    placeholderElement.textContent = props.placeholder
    placeholderElement.style.cssText = `
      position: absolute;
      color: #999;
      padding: 4px 0 0 10px;
      pointer-events: none;
      z-index: 1;
    `
    editor.getWrapperElement().appendChild(placeholderElement)

    editor.on('change', () => {
      if (editor.getValue()) {
        placeholderElement.style.display = 'none'
      } else {
        placeholderElement.style.display = 'block'
      }
    })
  }
})

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (editor && editor.getValue() !== newValue) {
    const cursor = editor.getCursor()
    editor.setValue(newValue || '')
    editor.setCursor(cursor)
  }
})

// 监听模式变化
watch(() => props.mode, (newMode) => {
  if (editor) {
    editor.setOption('mode', newMode)
  }
})

// 监听只读状态变化
watch(() => props.readonly, (newReadonly) => {
  if (editor) {
    editor.setOption('readOnly', newReadonly)
  }
})

// 组件销毁时清理
onBeforeUnmount(() => {
  if (editor) {
    editor.toTextArea()
    editor = null
  }
})

// 暴露编辑器实例方法
defineExpose({
  getEditor: () => editor,
  setValue: (value) => {
    if (editor) {
      editor.setValue(value || '')
    }
  },
  getValue: () => {
    return editor ? editor.getValue() : ''
  },
  refresh: () => {
    if (editor) {
      editor.refresh()
    }
  }
})
</script>

<style scoped>
.code-editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
}

.code-editor-wrapper :deep(.CodeMirror) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  background-color: #fff;
  color: #303133;
}

.code-editor-wrapper :deep(.CodeMirror-scroll) {
  min-height: 100px;
}

.code-editor-wrapper :deep(.CodeMirror-gutters) {
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
}

.code-editor-wrapper :deep(.CodeMirror-linenumber) {
  color: #909399;
}

.code-editor-wrapper :deep(.CodeMirror-cursor) {
  border-left: 1px solid #303133;
}

.code-editor-wrapper :deep(.CodeMirror-selected) {
  background-color: #e6f7ff;
}

.code-editor-wrapper :deep(.CodeMirror-activeline-background) {
  background-color: #f5f7fa;
}
</style>

