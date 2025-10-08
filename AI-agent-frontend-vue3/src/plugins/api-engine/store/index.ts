/**
 * API引擎插件 - Pinia Store
 */
import { defineStore } from 'pinia'
import { suiteAPI, caseAPI, executionAPI, keywordAPI, type Suite, type Case, type Execution, type Keyword } from '../api'

interface ApiEngineState {
    // 套件相关
    suites: Suite[]
    currentSuite: Suite | null
    suitesTotal: number
    suitesLoading: boolean

    // 用例相关
    cases: Case[]
    currentCase: Case | null
    casesTotal: number
    casesLoading: boolean

    // 执行记录相关
    executions: Execution[]
    currentExecution: Execution | null
    executionsTotal: number
    executionsLoading: boolean

    // 关键字相关
    keywords: Keyword[]
    builtinKeywords: any[]
    keywordsLoading: boolean
}

export const useApiEngineStore = defineStore('apiEngine', {
    state: (): ApiEngineState => ({
        suites: [],
        currentSuite: null,
        suitesTotal: 0,
        suitesLoading: false,

        cases: [],
        currentCase: null,
        casesTotal: 0,
        casesLoading: false,

        executions: [],
        currentExecution: null,
        executionsTotal: 0,
        executionsLoading: false,

        keywords: [],
        builtinKeywords: [],
        keywordsLoading: false
    }),

    getters: {
        // 根据套件ID获取用例列表
        getCasesBySuiteId: (state) => (suiteId: number) => {
            return state.cases.filter(c => c.suite_id === suiteId)
        },

        // 根据用例ID获取执行记录
        getExecutionsByCaseId: (state) => (caseId: number) => {
            return state.executions.filter(e => e.case_id === caseId)
        }
    },

    actions: {
        // ==================== 套件管理 ====================
        async fetchSuites(params?: any) {
            this.suitesLoading = true
            try {
                const res = await suiteAPI.getSuites(params)
                this.suites = res.data.items || []
                this.suitesTotal = res.data.total || 0
                return res.data
            } finally {
                this.suitesLoading = false
            }
        },

        async fetchSuiteById(id: number) {
            const res = await suiteAPI.getSuiteById(id)
            this.currentSuite = res.data
            return res.data
        },

        async createSuite(data: Suite) {
            const res = await suiteAPI.createSuite(data)
            await this.fetchSuites()
            return res.data
        },

        async updateSuite(id: number, data: Suite) {
            const res = await suiteAPI.updateSuite(id, data)
            await this.fetchSuites()
            if (this.currentSuite?.suite_id === id) {
                this.currentSuite = res.data
            }
            return res.data
        },

        async deleteSuite(id: number) {
            await suiteAPI.deleteSuite(id)
            await this.fetchSuites()
            if (this.currentSuite?.suite_id === id) {
                this.currentSuite = null
            }
        },

        // ==================== 用例管理 ====================
        async fetchCases(params?: any) {
            this.casesLoading = true
            try {
                const res = await caseAPI.getCases(params)
                this.cases = res.data.items || []
                this.casesTotal = res.data.total || 0
                return res.data
            } finally {
                this.casesLoading = false
            }
        },

        async fetchCaseById(id: number) {
            const res = await caseAPI.getCaseById(id)
            this.currentCase = res.data
            return res.data
        },

        async createCase(data: Case) {
            const res = await caseAPI.createCase(data)
            await this.fetchCases({ suite_id: data.suite_id })
            return res.data
        },

        async updateCase(id: number, data: Case) {
            const res = await caseAPI.updateCase(id, data)
            await this.fetchCases({ suite_id: data.suite_id })
            if (this.currentCase?.case_id === id) {
                this.currentCase = res.data
            }
            return res.data
        },

        async deleteCase(id: number) {
            const caseItem = this.cases.find(c => c.case_id === id)
            await caseAPI.deleteCase(id)
            if (caseItem) {
                await this.fetchCases({ suite_id: caseItem.suite_id })
            }
            if (this.currentCase?.case_id === id) {
                this.currentCase = null
            }
        },

        async cloneCase(id: number) {
            const res = await caseAPI.cloneCase(id)
            const caseItem = this.cases.find(c => c.case_id === id)
            if (caseItem) {
                await this.fetchCases({ suite_id: caseItem.suite_id })
            }
            return res.data
        },

        async importYaml(data: any) {
            const res = await caseAPI.importYaml(data)
            await this.fetchCases({ suite_id: data.suite_id })
            return res.data
        },

        // ==================== 执行管理 ====================
        async executeCase(caseId: number, context?: any) {
            const res = await executionAPI.executeCase(caseId, context)
            return res.data
        },

        async getExecutionStatus(taskId: string) {
            const res = await executionAPI.getExecutionStatus(taskId)
            this.currentExecution = res.data
            return res.data
        },

        async fetchExecutions(params?: any) {
            this.executionsLoading = true
            try {
                const res = await executionAPI.getExecutions(params)
                this.executions = res.data.items || []
                this.executionsTotal = res.data.total || 0
                return res.data
            } finally {
                this.executionsLoading = false
            }
        },

        async fetchExecutionById(id: number) {
            const res = await executionAPI.getExecutionById(id)
            this.currentExecution = res.data
            return res.data
        },

        async deleteExecution(id: number) {
            await executionAPI.deleteExecution(id)
            // 从列表中移除
            const index = this.executions.findIndex(e => e.execution_id === id)
            if (index !== -1) {
                this.executions.splice(index, 1)
                this.executionsTotal--
            }
        },

        // ==================== 关键字管理 ====================
        async fetchKeywords(params?: any) {
            this.keywordsLoading = true
            try {
                const res = await keywordAPI.getKeywords(params)
                this.keywords = res.data.items || []
                return res.data
            } finally {
                this.keywordsLoading = false
            }
        },

        async fetchBuiltinKeywords() {
            this.keywordsLoading = true
            try {
                const res = await keywordAPI.getBuiltinKeywords()
                this.builtinKeywords = res.data || []
                return res.data
            } finally {
                this.keywordsLoading = false
            }
        },

        async createKeyword(data: Keyword) {
            const res = await keywordAPI.createKeyword(data)
            await this.fetchKeywords()
            return res.data
        },

        async updateKeyword(id: number, data: Keyword) {
            const res = await keywordAPI.updateKeyword(id, data)
            await this.fetchKeywords()
            return res.data
        },

        async deleteKeyword(id: number) {
            await keywordAPI.deleteKeyword(id)
            await this.fetchKeywords()
        },

        async testKeyword(id: number, params: any) {
            const res = await keywordAPI.testKeyword(id, params)
            return res.data
        }
    }
})
