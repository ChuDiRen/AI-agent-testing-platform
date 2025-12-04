# AI Assistant Instructions

## Augment Context Engine (MCP)

**工具名称**: `codebase-retrieval` (auggie-mcp)

### 使用规则
1. 搜索代码时，**优先使用** `codebase-retrieval` 工具
2. 该工具提供语义代码搜索，比 grep 更智能
3. 适用于：查找相关代码、理解代码结构、搜索特定功能实现

### 调用示例
```
使用 codebase-retrieval 搜索 [你的查询]
```

### 配置信息
- **MCP Server**: auggie-mcp
- **Tenant URL**: https://d1.api.augmentcode.com/
- **Scope**: 全局可用
