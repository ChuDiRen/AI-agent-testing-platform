<template>
  <div class="workflow-editor-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <div class="editor-layout">
      <!-- Toolbar -->
      <div class="toolbar glass-panel">
        <div class="toolbar-left">
          <button class="btn-icon-text" @click="handleBack">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back
          </button>
          <div class="divider"></div>
          <h2 class="workflow-name">{{ workflowData.name || 'Untitled Workflow' }}</h2>
        </div>
        
        <div class="toolbar-center">
          <button class="btn-icon" @click="zoomIn" title="Zoom In">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="btn-icon" @click="zoomOut" title="Zoom Out">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="btn-icon" @click="fitView" title="Fit View">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 8V4h4M20 8V4h-4M4 16v4h4M20 16v4h-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <div class="toolbar-right">
          <button class="btn btn-glass" @click="handleClear">Clear</button>
          <button class="btn btn-glass" @click="handlePublish" :disabled="!workflowData.id">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-svg">
              <path d="M7 11l5 5m0 0l5-5m-5 5V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Publish
          </button>
          <button class="btn btn-primary-glow" @click="handleSave">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-svg">
              <path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Save
          </button>
        </div>
      </div>

      <div class="editor-workspace">
        <!-- Palette -->
        <div class="node-palette glass-panel">
          <div class="palette-header">
            <h3>Nodes</h3>
          </div>
          <div class="palette-items">
            <div
              v-for="nodeType in nodeTypes"
              :key="nodeType.type"
              class="palette-item"
              :class="`palette-${nodeType.type}`"
              draggable="true"
              @dragstart="onDragStart($event, nodeType)"
            >
              <div class="palette-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" v-html="nodeType.svg"></svg>
              </div>
              <span>{{ nodeType.label }}</span>
            </div>
          </div>
        </div>

        <!-- Canvas -->
        <div class="canvas-wrapper glass-card" @drop="onDrop" @dragover.prevent>
          <VueFlow
            v-model:nodes="nodes"
            v-model:edges="edges"
            :default-zoom="1"
            :min-zoom="0.2"
            :max-zoom="4"
            class="flow-container"
            @node-click="onNodeClick"
            @edge-click="onEdgeClick"
            @connect="onConnect"
            @nodes-change="onNodesChange"
            @edges-change="onEdgesChange"
            @pane-ready="onPaneReady"
          >
            <Background pattern-color="#444" :gap="20" />
            <Controls />
            <MiniMap />
            
            <template #node-custom="data">
              <div class="custom-node" :class="`node-${data.type}`">
                <div class="node-header">
                  <div class="node-icon">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" v-html="getNodeIcon(data.type)"></svg>
                  </div>
                  <span class="node-title">{{ data.label }}</span>
                </div>
                <div class="node-body" v-if="data.description">{{ data.description }}</div>
                <Handle type="target" :position="Position.Left" class="custom-handle" />
                <Handle type="source" :position="Position.Right" class="custom-handle" />
              </div>
            </template>
          </VueFlow>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VueFlow, useVueFlow, Handle, Position } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '@/api'

const route = useRoute()
const router = useRouter()
const { fitView: fitViewAction, zoomIn: zoomInAction, zoomOut: zoomOutAction } = useVueFlow()

const nodes = ref([])
const edges = ref([])
const workflowData = ref({})

const nodeTypes = [
  { 
    type: 'agent', 
    label: 'Agent', 
    color: 'var(--color-primary)',
    svg: '<path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  { 
    type: 'tool', 
    label: 'Tool', 
    color: 'var(--color-warning)',
    svg: '<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3L6.91 6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  { 
    type: 'condition', 
    label: 'Condition', 
    color: 'var(--color-success)',
    svg: '<path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  { 
    type: 'input', 
    label: 'Input', 
    color: '#d8b4fe',
    svg: '<path d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  { 
    type: 'output', 
    label: 'Output', 
    color: '#f9a8d4',
    svg: '<path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  }
]

function getNodeIcon(type) {
  const typeObj = nodeTypes.find(t => t.type === type)
  return typeObj ? typeObj.svg : ''
}

// VueFlow Actions
function fitView() { fitViewAction() }
function zoomIn() { zoomInAction() }
function zoomOut() { zoomOutAction() }

function handleBack() {
  router.push('/workflows')
}

// Load Workflow Data
async function loadWorkflow(id) {
  try {
    const response = await axios.get(`/v1/Workflow/${id}`)
    if (response.data.code === 200) {
      workflowData.value = response.data.data
      const graphData = JSON.parse(response.data.data.graph_data || '{"nodes":[], "edges":[]}')
      nodes.value = graphData.nodes || []
      edges.value = graphData.edges || []
    }
  } catch (error) {
    console.error('Load failed:', error)
    ElMessage.error('Failed to load workflow')
  }
}

// Save
async function handleSave() {
  const graphData = {
    nodes: nodes.value,
    edges: edges.value
  }

  const data = {
    name: workflowData.value.name || 'Untitled Workflow',
    description: workflowData.value.description,
    graph_data: JSON.stringify(graphData),
    created_by: 1 // TODO: Get from auth
  }

  try {
    if (workflowData.value.id) {
      await axios.put(`/v1/Workflow/${workflowData.value.id}`, data)
      ElMessage.success('Workflow saved')
    } else {
      const response = await axios.post('/v1/Workflow/', data)
      workflowData.value.id = response.data.data.id
      ElMessage.success('Workflow created')
      router.replace(`/workflows/${response.data.data.id}/edit`)
    }
  } catch (error) {
    console.error('Save failed:', error)
    ElMessage.error('Failed to save workflow')
  }
}

// Publish
async function handlePublish() {
  try {
    await axios.post(`/v1/Workflow/${workflowData.value.id}/publish`)
    ElMessage.success('Workflow published')
  } catch (error) {
    ElMessage.error('Failed to publish')
  }
}

// Drag & Drop
function onDragStart(event, nodeType) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', JSON.stringify(nodeType))
    event.dataTransfer.effectAllowed = 'move'
  }
}

function onDrop(event) {
  const data = event.dataTransfer?.getData('application/vueflow')
  if (!data) return

  const nodeType = JSON.parse(data)
  
  // Calculate position
  // In a real app, use project() from VueFlow to convert screen coords to flow coords
  // For now, simpler approximation or just center
  const newNode = {
    id: `node-${Date.now()}`,
    type: 'custom', // Use custom type for all to use our template
    label: nodeType.label,
    data: { 
      type: nodeType.type,
      label: nodeType.label,
      description: 'Click to configure'
    },
    position: { x: event.offsetX, y: event.offsetY }
  }
  
  nodes.value.push(newNode)
}

// Connect
function onConnect(params) {
  const newEdge = {
    id: `edge-${Date.now()}`,
    source: params.source,
    target: params.target,
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'var(--color-primary)', strokeWidth: 2 }
  }
  edges.value.push(newEdge)
}

// Clear
function handleClear() {
  nodes.value = []
  edges.value = []
}

function onPaneReady(instance) {
  instance.fitView()
}

onMounted(() => {
  const id = route.params.id
  if (id) {
    loadWorkflow(id)
  }
})
</script>

<style scoped>
.workflow-editor-container {
  height: calc(100vh - 80px); /* Adjust for header if needed */
  position: relative;
  overflow: hidden;
  padding: var(--space-4);
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

.editor-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-4);
}

/* Toolbar */
.toolbar {
  padding: var(--space-3) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--radius-xl);
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
}

.toolbar-left, .toolbar-center, .toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.workflow-name {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--color-border-light);
}

.btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
}

.btn-icon svg {
  width: 20px;
  height: 20px;
}

.btn-icon-text {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: color 0.2s ease;
}

.btn-icon-text:hover {
  color: var(--color-text-primary);
}

.btn-icon-text svg {
  width: 18px;
  height: 18px;
}

.btn-glass {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-weight: var(--font-medium);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  transition: all 0.2s ease;
}

.btn-glass:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-primary-glow {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border: none;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
  transition: all 0.3s ease;
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
}

.btn-svg {
  width: 16px;
  height: 16px;
}

/* Workspace */
.editor-workspace {
  display: flex;
  flex: 1;
  gap: var(--space-4);
  overflow: hidden;
}

/* Palette */
.node-palette {
  width: 240px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
}

.palette-header h3 {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-4);
}

.palette-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  overflow-y: auto;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: grab;
  transition: all 0.2s ease;
}

.palette-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
  border-color: var(--color-primary);
}

.palette-icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-primary);
}

.palette-agent .palette-icon { color: var(--color-primary); }
.palette-tool .palette-icon { color: var(--color-warning); }
.palette-condition .palette-icon { color: var(--color-success); }
.palette-input .palette-icon { color: #d8b4fe; }
.palette-output .palette-icon { color: #f9a8d4; }

/* Canvas */
.canvas-wrapper {
  flex: 1;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-glass);
}

.flow-container {
  height: 100%;
  width: 100%;
}

/* Custom Node */
.custom-node {
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  background: rgba(30, 30, 40, 0.9);
  border: 1px solid var(--color-border);
  min-width: 180px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.custom-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.node-agent { border-color: var(--color-primary); box-shadow: 0 0 15px rgba(124, 58, 237, 0.2); }
.node-tool { border-color: var(--color-warning); box-shadow: 0 0 15px rgba(245, 158, 11, 0.2); }
.node-condition { border-color: var(--color-success); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
.node-input { border-color: #d8b4fe; box-shadow: 0 0 15px rgba(216, 180, 254, 0.2); }
.node-output { border-color: #f9a8d4; box-shadow: 0 0 15px rgba(249, 168, 212, 0.2); }

.node-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.node-icon {
  width: 20px;
  height: 20px;
}

.node-agent .node-icon { color: var(--color-primary); }
.node-tool .node-icon { color: var(--color-warning); }
.node-condition .node-icon { color: var(--color-success); }
.node-input .node-icon { color: #d8b4fe; }
.node-output .node-icon { color: #f9a8d4; }

.node-title {
  font-weight: var(--font-bold);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.node-body {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.custom-handle {
  width: 10px;
  height: 10px;
  background: var(--color-text-secondary);
  border: 2px solid var(--color-bg-primary);
}

.custom-handle:hover {
  background: var(--color-primary);
  width: 12px;
  height: 12px;
}
</style>