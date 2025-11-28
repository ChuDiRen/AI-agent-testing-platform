const MockData = {
    rules: [
        {
            id: 1,
            title: "代码规范检查",
            desc: "强制执行统一的代码风格，包括缩进、命名规范、注释要求等。适用于所有前端项目，确保代码可读性和可维护性。",
            author: "官方",
            date: "2025-11-11",
            tags: ["官方", "代码规范"],
            color: "#E0F2FE",
            textColor: "#0284C7"
        },
        {
            id: 2,
            title: "安全漏洞扫描",
            desc: "自动扫描常见的安全漏洞，如 SQL 注入、XSS 攻击、越权访问等。建议在每次发布前运行此规则。",
            author: "官方",
            date: "2025-11-12",
            tags: ["官方", "安全"],
            color: "#F0FDF4",
            textColor: "#16A34A"
        },
        {
            id: 3,
            title: "性能测试优化",
            desc: "监控页面加载时间、网络请求数量、内存占用等指标，并提供性能优化建议。",
            author: "社区",
            date: "2025-11-20",
            tags: ["社区热门", "性能"],
            color: "#F3E8FF",
            textColor: "#9333EA"
        },
        {
            id: 4,
            title: "UI自动化检测",
            desc: "基于 Puppeteer 自动化测试UI界面，检测交互流程是否流畅，验证各种设备上的兼容性。",
            author: "社区",
            date: "2025-11-18",
            tags: ["UI测试", "自动化"],
            color: "#FFF7ED",
            textColor: "#EA580C"
        },
        {
            id: 5,
            title: "API接口测试",
            desc: "对所有 API 接口执行自动化测试，覆盖正常情况与异常边界，并生成详细的测试报告。",
            author: "官方",
            date: "2025-11-15",
            tags: ["官方", "API测试"],
            color: "#FEF2F2",
            textColor: "#DC2626"
        }
    ],
    knowledge: [
        { id: 1, title: "测试规范文档", desc: "包含所有测试流程、最佳实践和团队协作规范，适合新成员快速上手。", author: "官方", date: "2025-11-10", icon: "book-open", color: "#E0F2FE", textColor: "#0284C7" },
        { id: 2, title: "前端测试指南", desc: "深入剖析前端测试工具和框架，包括 Jest、Mocha、Cypress 等主流工具的使用技巧。", author: "官方", date: "2025-11-08", icon: "code", color: "#F0FDF4", textColor: "#16A34A" },
        { id: 3, title: "后端架构方案", desc: "详细描述微服务架构、数据库设计、API 设计等后端核心知识。", author: "社区", date: "2025-11-06", icon: "database", color: "#F3E8FF", textColor: "#9333EA" },
        { id: 4, title: "测试用例库", desc: "包含大量通用测试用例模板，覆盖各类常见场景和边界情况。", author: "官方", date: "2025-11-04", icon: "check-square", color: "#FFF7ED", textColor: "#EA580C" }
    ],
    plugins: [
        { id: 1, title: "Mock Server", desc: "快速搭建 Mock 服务器，模拟后端接口，支持动态数据生成。", author: "官方", date: "2025-11-05", type: "工具", icon: "globe", color: "#E0F2FE", textColor: "#0284C7" },
        { id: 2, title: "数据生成器", desc: "自动生成测试数据，支持多种数据类型和自定义规则。", author: "社区", date: "2025-11-03", type: "数据生成", icon: "database", color: "#F0FDF4", textColor: "#16A34A" },
        { id: 3, title: "API 校验插件", desc: "自动校验 API 返回数据格式，确保接口契约一致性。", author: "社区", date: "2025-11-07", type: "校验", icon: "shield-check", color: "#F3E8FF", textColor: "#9333EA" },
        { id: 4, title: "日志分析器", desc: "快速分析和过滤系统日志", author: "社区", date: "2025-11-04", type: "插件", icon: "magnifying-glass", color: "#F3E8FF", textColor: "#9333EA" }
    ],
    agents: [
        { id: 1, title: "自动化测试助手", desc: "基于 Selenium/Playwright 自动生成 UI 测试脚本，支持多浏览器兼容性测试。", author: "官方", date: "2025-11-25", type: "自动化", icon: "robot", color: "#E0F2FE", textColor: "#0284C7" },
        { id: 2, title: "API 压力测试专家", desc: "模拟高并发场景，生成 JMeter/K6 脚本，分析系统瓶颈。", author: "官方", date: "2025-11-22", type: "性能", icon: "gauge", color: "#F0FDF4", textColor: "#16A34A" },
        { id: 3, title: "安全审计员", desc: "自动扫描代码中的安全漏洞，提供修复建议，符合 OWASP 标准。", author: "社区", date: "2025-11-20", type: "安全", icon: "shield-check", color: "#FEF2F2", textColor: "#DC2626" },
        { id: 4, title: "文档生成助手", desc: "根据代码注释和接口定义自动生成 Swagger/OpenAPI 文档。", author: "社区", date: "2025-11-18", type: "文档", icon: "file-doc", color: "#FFF7ED", textColor: "#EA580C" },
        { id: 5, title: "SQL 优化顾问", desc: "分析慢查询日志，提供索引优化建议和 SQL 重写方案。", author: "官方", date: "2025-11-15", type: "数据库", icon: "database", color: "#F3E8FF", textColor: "#9333EA" },
        { id: 6, title: "移动端测试机器人", desc: "自动遍历 App 界面，检测崩溃和 UI 异常，支持 iOS 和 Android。", author: "官方", date: "2025-11-10", type: "移动端", icon: "device-mobile", color: "#ECFEFF", textColor: "#0891B2" }
    ],
    mcp: [
        { id: 1, title: "Filesystem", desc: "提供对本地文件系统的访问权限，用于读取和写入文件。", author: "官方", date: "2025-11-20", status: "Connected", icon: "folder", color: "#E0F2FE", textColor: "#0284C7" },
        { id: 2, title: "PostgreSQL", desc: "启用对 PostgreSQL 数据库的读写访问权限，支持架构检查。", author: "官方", date: "2025-11-18", status: "Connected", icon: "database", color: "#F0FDF4", textColor: "#16A34A" },
        { id: 3, title: "GitHub", desc: "集成 GitHub API，用于仓库管理和问题跟踪。", author: "社区", date: "2025-11-15", status: "Disconnected", icon: "github-logo", color: "#F3E8FF", textColor: "#9333EA" },
        { id: 4, title: "Sentry", desc: "从 Sentry 项目中检索错误报告和性能指标。", author: "社区", date: "2025-11-10", status: "Connected", icon: "bug", color: "#FFF7ED", textColor: "#EA580C" },
        { id: 5, title: "Slack", desc: "通过 Slack API 发送消息并读取频道历史记录。", author: "官方", date: "2025-11-05", status: "Disconnected", icon: "slack-logo", color: "#FEF2F2", textColor: "#DC2626" },
        { id: 6, title: "Google Drive", desc: "访问和管理存储在 Google Drive 中的文件。", author: "官方", date: "2025-11-01", status: "Connected", icon: "google-drive-logo", color: "#ECFEFF", textColor: "#0891B2" }
    ],
    prompts: [
        { id: 1, title: "生成单元测试", desc: "为选定的函数或类生成覆盖率高的单元测试代码。", author: "官方", date: "2025-11-25", tags: ["测试", "代码生成"], icon: "test-tube", color: "#E0F2FE", textColor: "#0284C7" },
        { id: 2, title: "解释复杂代码", desc: "用通俗易懂的语言解释复杂的算法或逻辑。", author: "官方", date: "2025-11-22", tags: ["解释", "学习"], icon: "lightbulb", color: "#F0FDF4", textColor: "#16A34A" },
        { id: 3, title: "代码重构建议", desc: "分析代码结构,提供重构建议以提高可读性和性能。", author: "社区", date: "2025-11-20", tags: ["重构", "优化"], icon: "arrows-clockwise", color: "#F3E8FF", textColor: "#9333EA" },
        { id: 4, title: "生成 API 文档", desc: "根据代码自动生成标准的 API 接口文档。", author: "社区", date: "2025-11-18", tags: ["文档", "API"], icon: "file-text", color: "#FFF7ED", textColor: "#EA580C" },
        { id: 5, title: "查找潜在 Bug", desc: "扫描代码，指出可能导致运行时错误的逻辑漏洞。", author: "官方", date: "2025-11-15", tags: ["调试", "Bug"], icon: "bug", color: "#FEF2F2", textColor: "#DC2626" },
        { id: 6, title: "SQL 查询优化", desc: "优化复杂的 SQL 查询语句，提高执行效率。", author: "社区", date: "2025-11-10", tags: ["数据库", "SQL"], icon: "database", color: "#ECFEFF", textColor: "#0891B2" }
    ]
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MockData;
}
