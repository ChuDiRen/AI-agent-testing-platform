<template>
  <div class="workflow-create-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Create Workflow</h1>
          <p class="page-description">Design your automated agent pipeline</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-glass" @click="handleCancel">
            Cancel
          </button>
          <button class="btn btn-primary-glow" @click="handleSave" :disabled="!isValid">
            <span v-if="saving" class="loading-text">
              <svg class="spinner-sm" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="60" stroke-dashoffset="30"/>
              </svg>
              Saving...
            </span>
            <span v-else>Save Workflow</span>
          </button>
        </div>
      </div>
    </div>

    <div class="workflow-editor">
      <!-- Toolbar -->
      <div class="editor-toolbar glass-panel">
        <div class="toolbar-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="section-icon">
              <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Workflow Info
          </h3>
          <div class="form-group">
            <label for="workflow-name" class="form-label">Name</label>
            <input
              id="workflow-name"
              v-model="workflow.name"
              type="text"
              class="form-input glass-input"
              placeholder="e.g. Customer Support Bot"
              required
            />
          </div>
          <div class="form-group">
            <label for="workflow-description" class="form-label">Description</label>
            <textarea
              id="workflow-description"
              v-model="workflow.description"
              class="form-textarea glass-input"
              placeholder="Describe what this workflow does..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="toolbar-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="section-icon">
              <path d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Nodes
          </h3>
          <div class="node-palette">
            <div 
              v-for="nodeType in nodeTypes" 
              :key="nodeType.type"
              class="node-type-item glass-card-sm"
              @click="addNode(nodeType)"
              draggable="true"
              @dragstart="onDragStart($event, nodeType)"
            >
              <div class="node-icon" :class="nodeType.colorClass">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" v-html="nodeType.svg"></svg>
              </div>
              <span>{{ nodeType.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Canvas -->
      <div class="canvas-container glass-card" @dragover.prevent @drop="onDrop">
        <div class="workflow-canvas">
          <!-- Grid Background -->
          <div class="grid-pattern"></div>
          
          <div class="canvas-placeholder">
            <div class="placeholder-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="placeholder-icon">
                <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3L6.91 6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>Start Building</h3>
            <p>Drag and drop nodes from the left panel to begin</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const saving = ref(false)

const workflow = ref({
  name: '',
  description: '',
  graph_data: '{}'
})

const nodeTypes = ref([
  {
    type: 'agent',
    label: 'AI Agent',
    colorClass: 'text-primary',
    svg: '<path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    type: 'tool',
    label: 'Tool',
    colorClass: 'text-warning',
    svg: '<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3L6.91 6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    type: 'condition',
    label: 'Condition',
    colorClass: 'text-success',
    svg: '<path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    type: 'loop',
    label: 'Loop',
    colorClass: 'text-info',
    svg: '<path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    type: 'input',
    label: 'Input',
    colorClass: 'text-purple',
    svg: '<path d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    type: 'output',
    label: 'Output',
    colorClass: 'text-pink',
    svg: '<path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  }
])

const isValid = computed(() => {
  return workflow.value.name.trim() !== ''
})

function handleCancel() {
  router.push('/workflows')
}

function handleSave() {
  if (!isValid.value) {
    ElMessage.warning('Please enter a workflow name')
    return
  }

  saving.value = true
  setTimeout(() => {
    ElMessage.success('Workflow saved successfully!')
    router.push('/workflows')
    saving.value = false
  }, 1000)
}

function addNode(nodeType) {
  ElMessage.info(`Added ${nodeType.label} node`)
}

function onDragStart(event, nodeType) {
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('nodeType', JSON.stringify(nodeType))
}

function onDrop(event) {
  const nodeType = JSON.parse(event.dataTransfer.getData('nodeType'))
  addNode(nodeType)
}
</script>

<style scoped>
.workflow-create-container {
  padding: var(--space-6);
  max-width: 1600px;
  margin: 0 auto;
  position: relative;
  min-height: 80vh;
}

/* Background Decoration */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.orb-1 {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  animation: float 20s infinite ease-in-out;
}

.orb-2 {
  bottom: 10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: var(--color-secondary);
  animation: float 25s infinite ease-in-out reverse;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  50% { transform: translate(30px, 50px); }
  100% { transform: translate(0, 0); }
}

/* Header */
.page-header {
  margin-bottom: var(--space-6);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 var(--space-2);
}

.page-description {
  color: var(--color-text-secondary);
  font-size: var(--text-base);
}

.header-actions {
  display: flex;
  gap: var(--space-4);
}

/* Buttons */
.btn-glass {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-glass:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-text-secondary);
}

.btn-primary-glow {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border: none;
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-primary-glow:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
}

.btn-primary-glow:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  animation: rotate 2s linear infinite;
}

.spinner-sm circle {
  stroke: currentColor;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

/* Editor Layout */
.workflow-editor {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--space-6);
  height: calc(100vh - 200px);
}

/* Toolbar */
.editor-toolbar {
  padding: var(--space-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
  border-radius: var(--radius-xl);
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
}

.toolbar-section h3 {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.section-icon {
  width: 16px;
  height: 16px;
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.glass-input {
  width: 100%;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: var(--text-sm);
  transition: all 0.2s ease;
}

.glass-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Node Palette */
.node-palette {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.node-type-item {
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: grab;
  transition: all 0.2s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.node-type-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.node-type-item:active {
  cursor: grabbing;
}

.node-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-icon svg {
  width: 24px;
  height: 24px;
}

.text-primary { color: var(--color-primary); }
.text-warning { color: var(--color-warning); }
.text-success { color: var(--color-success); }
.text-info { color: var(--color-info); }
.text-purple { color: #d8b4fe; }
.text-pink { color: #f9a8d4; }

.node-type-item span {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.node-type-item:hover span {
  color: var(--color-text-primary);
}

/* Canvas */
.canvas-container {
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
  position: relative;
}

.workflow-canvas {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.canvas-placeholder {
  text-align: center;
  position: relative;
  z-index: 1;
}

.placeholder-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-4);
  border: 1px dashed var(--color-border-light);
}

.placeholder-icon {
  width: 40px;
  height: 40px;
  color: var(--color-text-muted);
}

.canvas-placeholder h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-2);
  color: var(--color-text-primary);
}

.canvas-placeholder p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: var(--breakpoint-lg)) {
  .workflow-editor {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .editor-toolbar {
    max-height: 400px;
  }
  
  .node-palette {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .canvas-container {
    height: 500px;
  }
}

@media (max-width: var(--breakpoint-sm)) {
  .node-palette {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>