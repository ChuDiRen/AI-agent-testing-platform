# CodeBuddy Skills

本目录包含项目级别的 Skills（技能），用于扩展 AI 助手的专业能力。

## 目录结构

```
skills/
├── design/              # 设计类技能
│   ├── api-documentation/   # API 文档生成
│   ├── database-design/     # 数据库设计
│   └── frontend-design/     # 前端界面设计
│
├── development/         # 开发类技能
│   └── mcp-builder/         # MCP 服务器开发
│
├── testing/             # 测试类技能
│   ├── api-testing/         # API 接口测试 ⭐
│   └── webapp-testing/      # Web 应用测试 ⭐
│
└── workflows/           # 工作流类技能
    ├── project-bootstrap/   # 项目启动
    └── skill-creator/       # 技能创建
```

## Skills 清单（8 个）

| 分类 | Skill | 描述 |
|------|-------|------|
| **design** | api-documentation | API 文档生成工具 |
| | database-design | 数据库表结构设计 |
| | frontend-design | 高质量前端界面设计与原型设计 |
| **development** | mcp-builder | MCP 服务器开发指南 |
| **testing** | api-testing | pytest + httpx API 测试 ⭐ |
| | webapp-testing | Playwright Web 测试 ⭐ |
| **workflows** | project-bootstrap | 项目启动工作流 |
| | skill-creator | 技能创建指南 |

## Skill 文件结构

每个 Skill 必须遵循以下结构：

```
skill-name/
├── SKILL.md              # 必需：核心指令文件
│   ├── YAML 前置元数据
│   │   ├── name: 技能名称（必需）
│   │   └── description: 描述（必需）
│   └── Markdown 指令正文
└── 可选资源/
    ├── scripts/          # 可执行脚本
    ├── examples/         # 示例代码
    └── assets/           # 模板、图标等
```

## 相关 Rules

以下规则已从 Skills 转换而来，位于 `.codebuddy/rules/` 目录：

| Rule | 类型 | 描述 |
|------|------|------|
| code-reuse-check | always | 代码复用检查（生成代码前自动检查） |
| task-splitting | requested | 任务拆分规则（按需使用） |
