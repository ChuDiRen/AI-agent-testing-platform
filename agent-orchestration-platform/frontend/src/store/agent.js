import { createPinia } from 'pinia'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref([])
  const currentAgent = ref(null)
  const loading = ref(false)

  // 获取 Agent 列表
  async function fetchAgents(params = {}) {
    loading.value = true
    try {
      const response = await axios.get('/v1/Agent/', { params })
      
      if (response.data && response.data.code === 200) {
        agents.value = response.data.data || []
        return {
          data: response.data.data || [],
          total: response.data.total || 0
        }
      }
      return { data: [], total: 0 }
    } catch (error) {
      return { data: [], total: 0 }
    } finally {
      loading.value = false
    }
  }

  // 获取单个 Agent
  async function fetchAgent(id) {
    try {
      const response = await axios.get(`/v1/Agent/${id}`)
      if (response.data.code === 200) {
        currentAgent.value = response.data.data
      }
    } catch (error) {
      console.error('Failed to fetch agent:', error)
    }
  }

  // 创建 Agent
  async function createAgent(agentData) {
    loading.value = true
    try {
      const response = await axios.post('/v1/Agent/', agentData)
      if (response.data.code === 200) {
        // 创建成功后，重新加载列表
        await fetchAgents({ skip: 0, limit: 1000 })
        return response.data.data
      } else {
        throw new Error(response.data.msg || '创建失败')
      }
    } catch (error) {
      console.error('Failed to create agent:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新 Agent
  async function updateAgent(id, agentData) {
    loading.value = true
    try {
      const response = await axios.put(`/v1/Agent/${id}`, agentData)
      if (response.data.code === 200) {
        await fetchAgents()
        return response.data.data
      }
    } catch (error) {
      console.error('Failed to update agent:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除 Agent
  async function deleteAgent(id) {
    try {
      const response = await axios.delete(`/v1/Agent/${id}`)
      if (response.data.code === 200) {
        await fetchAgents()
      }
    } catch (error) {
      console.error('Failed to delete agent:', error)
      throw error
    }
  }

  return {
    agents,
    currentAgent,
    loading,
    fetchAgents,
    fetchAgent,
    createAgent,
    updateAgent,
    deleteAgent
  }
})
