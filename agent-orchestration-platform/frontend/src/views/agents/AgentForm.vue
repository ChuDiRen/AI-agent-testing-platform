<template>
  <div class="modal-backdrop" @click="handleClose">
    <!-- Background Decoration (visible if used as page) -->
    <div class="bg-decoration" v-if="!isModal">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <div class="modal-container glass-panel" @click.stop>
      <div class="modal-header">
        <div class="header-text">
          <h2 class="modal-title">{{ isEdit ? 'Edit Agent' : 'Create Agent' }}</h2>
          <p class="modal-subtitle">Configure your AI agent settings</p>
        </div>
        <button class="close-btn" @click="handleClose" aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="close-icon">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body custom-scrollbar">
        <div class="form-section">
          <h3 class="section-title">Basic Information</h3>

          <div class="form-group">
            <label for="name" class="form-label">Agent Name *</label>
            <input
              id="name"
              v-model="agentForm.name"
              type="text"
              class="form-input glass-input"
              :class="{ 'input-error': errors.name }"
              placeholder="e.g. Customer Support Bot"
              required
              aria-required="true"
              aria-invalid="!!errors.name"
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>

          <div class="form-group">
            <label for="model" class="form-label">Model *</label>
            <div class="select-wrapper">
              <select
                id="model"
                v-model="agentForm.model"
                class="form-select glass-input"
                required
                aria-required="true"
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="claude-3-haiku">Claude 3 Haiku</option>
              </select>
              <svg class="select-arrow" viewBox="0 0 24 24" fill="none">
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <div class="form-group">
            <label for="description" class="form-label">Description</label>
            <textarea
              id="description"
              v-model="agentForm.description"
              class="form-textarea glass-input"
              placeholder="Describe what this agent does..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">Model Configuration</h3>

          <div class="form-group">
            <label for="temperature" class="form-label">
              Temperature: {{ agentForm.temperature }}
              <span class="label-hint">Lower for focus, higher for creativity</span>
            </label>
            <div class="range-wrapper">
              <input
                id="temperature"
                v-model="agentForm.temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
                class="form-range"
                aria-valuemin="0"
                aria-valuemax="2"
                :aria-valuenow="agentForm.temperature"
              />
              <div class="range-labels">
                <span>Focused</span>
                <span>Creative</span>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="maxTokens" class="form-label">Max Tokens *</label>
              <div class="input-with-unit">
                <input
                  id="maxTokens"
                  v-model.number="agentForm.max_tokens"
                  type="number"
                  class="form-input glass-input"
                  min="1"
                  max="128000"
                  required
                  aria-required="true"
                />
                <span class="input-unit">tokens</span>
              </div>
            </div>

            <div class="form-group">
              <label for="topP" class="form-label">Top P</label>
              <input
                id="topP"
                v-model="agentForm.top_p"
                type="number"
                step="0.01"
                min="0"
                max="1"
                class="form-input glass-input"
                placeholder="0.9"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="frequencyPenalty" class="form-label">Frequency Penalty</label>
              <input
                id="frequencyPenalty"
                v-model="agentForm.frequency_penalty"
                type="number"
                step="0.1"
                min="-2"
                max="2"
                class="form-input glass-input"
                placeholder="0"
              />
            </div>

            <div class="form-group">
              <label for="presencePenalty" class="form-label">Presence Penalty</label>
              <input
                id="presencePenalty"
                v-model="agentForm.presence_penalty"
                type="number"
                step="0.1"
                min="-2"
                max="2"
                class="form-input glass-input"
                placeholder="0"
              />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">System Prompt</h3>

          <div class="form-group">
            <label for="systemPrompt" class="form-label">
              System Instructions
              <span class="label-hint">Define the agent's behavior and role</span>
            </label>
            <div class="textarea-wrapper">
              <textarea
                id="systemPrompt"
                v-model="agentForm.system_prompt"
                class="form-textarea code-textarea glass-input"
                :class="{ 'input-error': errors.system_prompt }"
                placeholder="You are a helpful AI assistant..."
                rows="8"
              ></textarea>
              <div class="textarea-actions">
                <button type="button" class="action-sm-btn" @click="generateTemplate" title="Use Template">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
                    <path d="M12 6v6m0 0v6m0-6h6m-6 0H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Template
                </button>
                <button type="button" class="action-sm-btn danger" @click="clearPrompt" title="Clear">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
                    <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Clear
                </button>
              </div>
            </div>
            <span v-if="errors.system_prompt" class="error-message">{{ errors.system_prompt }}</span>
          </div>
        </div>
      </form>

      <div class="modal-footer">
        <button type="button" class="btn btn-glass" @click="handleClose">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary-glow" :disabled="saving" @click="handleSubmit">
          <span v-if="saving" class="loading-text">
            <svg class="spinner" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="60" stroke-dashoffset="30"/>
            </svg>
            Saving...
          </span>
          <span v-else>{{ isEdit ? 'Update Agent' : 'Create Agent' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAgentStore } from '@/store/agent'

const props = defineProps({
  visible: Boolean,
  agent: Object
})

const emit = defineEmits(['save', 'close'])

const router = useRouter()
const route = useRoute()
const agentStore = useAgentStore()

const saving = ref(false)
const errors = ref({})

const defaultForm = {
  name: '',
  model: 'gpt-3.5-turbo',
  description: '',
  temperature: 0.7,
  max_tokens: 2048,
  top_p: 0.9,
  frequency_penalty: 0,
  presence_penalty: 0,
  system_prompt: ''
}

const agentForm = reactive({ ...defaultForm })

const isEdit = computed(() => {
  return props.agent && props.agent.id
})

// Check if used as modal or page
const isModal = computed(() => {
  return route.name !== 'AgentCreate' && route.name !== 'AgentEdit'
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (props.agent) {
      Object.assign(agentForm, props.agent)
    } else {
      Object.assign(agentForm, defaultForm)
    }
    errors.value = {}
  }
})

function validateForm() {
  const newErrors = {}

  if (!agentForm.name || agentForm.name.trim().length === 0) {
    newErrors.name = 'Agent name is required'
  } else if (agentForm.name.length < 3) {
    newErrors.name = 'Name must be at least 3 characters'
  } else if (agentForm.name.length > 100) {
    newErrors.name = 'Name must be less than 100 characters'
  }

  if (!agentForm.model) {
    newErrors.model = 'Please select a model'
  }

  if (!agentForm.max_tokens || agentForm.max_tokens < 1) {
    newErrors.max_tokens = 'Max tokens must be at least 1'
  } else if (agentForm.max_tokens > 128000) {
    newErrors.max_tokens = 'Max tokens cannot exceed 128,000'
  }

  if (!agentForm.system_prompt || agentForm.system_prompt.trim().length === 0) {
    newErrors.system_prompt = 'System prompt is required'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

function handleClose() {
  if (route.name === 'AgentCreate' || route.name === 'AgentEdit') {
    router.push('/agents')
  } else {
    emit('close')
  }
}

async function handleSubmit() {
  if (!validateForm()) {
    ElMessage.warning('Please fix the form errors')
    return
  }

  saving.value = true
  try {
    if (route.name === 'AgentCreate' || route.name === 'AgentEdit') {
      const userId = parseInt(localStorage.getItem('userId') || '1')
      const agentData = {
        ...agentForm,
        created_by: userId
      }
      
      await agentStore.createAgent(agentData)
      ElMessage.success('Agent created successfully!')
      
      setTimeout(() => {
        router.push('/agents')
      }, 800)
    } else {
      await emit('save', { ...agentForm })
      ElMessage.success(isEdit.value ? 'Agent updated successfully!' : 'Agent created successfully!')
      setTimeout(() => {
        emit('close')
      }, 500)
    }
  } catch (error) {
    console.error('Save failed:', error)
    const errorMsg = error.response?.data?.msg || error.message || 'Failed to save agent'
    ElMessage.error(errorMsg)
  } finally {
    saving.value = false
  }
}

function generateTemplate() {
  agentForm.system_prompt = `You are a helpful AI assistant with the following characteristics:

**Role:** [Define the agent's role]
**Tone:** [Professional, friendly, formal, etc.]
**Expertise:** [Areas of expertise]
**Goal:** [Primary objective]

**Guidelines:**
- Be concise and clear in responses
- Ask clarifying questions when needed
- Provide helpful, accurate information
- Maintain a consistent personality

**Constraints:**
- [Any limitations or constraints]
- [Topics to avoid]

**Example Response Style:**
[Provide an example of how you want the agent to respond]`
}

function clearPrompt() {
  agentForm.system_prompt = ''
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

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

.modal-container {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  background: var(--color-bg-glass);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modal-pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes modal-pop {
  0% { transform: scale(0.95); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border-glass);
}

.modal-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: var(--space-1);
}

.modal-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  border-radius: var(--radius-lg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-out;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
}

.close-icon {
  width: 20px;
  height: 20px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.form-section {
  margin-bottom: var(--space-8);
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 2px solid var(--color-border-glass);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.label-hint {
  display: block;
  font-size: var(--text-xs);
  font-weight: var(--font-normal);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.glass-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease-out;
}

.glass-input::placeholder {
  color: var(--color-text-disabled);
}

.glass-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.glass-input.input-error {
  border-color: var(--color-error);
}

.glass-input.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.code-textarea {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.6;
}

.select-wrapper {
  position: relative;
}

.form-select {
  appearance: none;
  padding-right: 3rem;
  cursor: pointer;
}

.select-arrow {
  position: absolute;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.range-wrapper {
  padding: var(--space-2) 0;
}

.form-range {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  outline: none;
  cursor: pointer;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
  transition: transform 0.2s ease-out;
}

.form-range::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.input-with-unit {
  position: relative;
}

.input-unit {
  position: absolute;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.textarea-wrapper {
  position: relative;
}

.textarea-actions {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  display: flex;
  gap: var(--space-2);
}

.action-sm-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-sm-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
}

.action-sm-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border-color: rgba(239, 68, 68, 0.3);
}

.error-message {
  display: block;
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-top: var(--space-1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--color-border-glass);
  background: rgba(0, 0, 0, 0.2);
}

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

.loading-text {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 0.6s linear infinite;
}

.spinner circle {
  stroke: currentColor;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes dash {
  0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
  50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
  100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-full);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Responsive */
@media (max-width: var(--breakpoint-sm)) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>