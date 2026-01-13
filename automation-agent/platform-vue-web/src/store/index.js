// src/store/index.js
import { createStore } from 'vuex'

// 定义状态类型（使用JSDoc注释）
/**
 * @typedef {Object} State
 * @property {string} asideWidth
 */

// 创建 store 实例
const store = createStore({
  state: {
    asideWidth: '250px'
    // 其他初始状态
  },
  mutations: {
    handleAsideWidth(state) {
      state.asideWidth = state.asideWidth === '250px' ? '20px' : '250px'
    }
    // 其他 mutations
  },
  actions: {
    // actions
  },
  modules: {
    // modules
  }
})

export default store