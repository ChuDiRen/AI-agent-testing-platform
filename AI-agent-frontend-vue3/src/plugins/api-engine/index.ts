/**
 * API引擎插件 - 入口文件
 */
import type { PluginModule } from '../types'
import routes from './routes'
import { useApiEngineStore } from './store'

const apiEnginePlugin: PluginModule = {
    name: 'api-engine',
    version: '1.0.0',
    description: 'API自动化测试引擎插件',
    enabled: true,
    routes,
    store: useApiEngineStore,
    menuItems: [
        {
            title: 'API引擎',
            icon: 'ApiOutlined',
            path: '/plugin/api-engine',
            children: [
                {
                    title: '测试套件',
                    icon: 'FolderOutlined',
                    path: '/plugin/api-engine/suites'
                },
                {
                    title: '用例管理',
                    icon: 'FileTextOutlined',
                    path: '/plugin/api-engine/cases'
                },
                {
                    title: '执行历史',
                    icon: 'HistoryOutlined',
                    path: '/plugin/api-engine/executions'
                },
                {
                    title: '关键字管理',
                    icon: 'CodeOutlined',
                    path: '/plugin/api-engine/keywords'
                }
            ]
        }
    ]
}

export default apiEnginePlugin
