---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [output-format] | --markdown 
description: 自动生成 API 参考文档，支持多种输出格式和自动化部署
---

# 自动化 API 文档生成器

自动生成 API 参考文档: $ARGUMENTS

## 任务

使用现代化工具设置自动化 API 文档生成：

1. **API 文档策略分析**
   - 分析当前 API 结构和端点（tRPC/HTTP）
   - 识别文档需求（tRPC、RESTful HTTP 等）
   - 评估现有的 proto 文件注释和 Go 代码文档
   - 检查 tRPC-Go 服务的接口定义和注释规范

2. **Mermaid 图表自动生成**
   - 自动生成系统架构图（graph TD）：基于 proto 文件识别服务组件和依赖关系
   - 自动生成 API 调用流程图（flowchart TD）：基于 RPC 方法生成包含认证、验证、业务处理、错误处理的流程
   - 自动生成服务交互时序图（sequenceDiagram）：为每个 RPC 方法生成请求-响应交互序列
   - 图表以 Mermaid 代码块形式自动嵌入到文档的对应章节

3. **代码注释和 Schema 定义**
   - 为 protobuf 文件添加全面的注释
     - service 和 rpc 方法注释
     - message 和 field 注释
     - 添加示例值和验证规则说明
   - 为 Go 代码添加标准注释
     - 函数和方法的 godoc 注释
     - 结构体和字段说明
     - 示例代码（Example tests）
   - 文档化认证和授权要求
   - 添加请求/响应示例
   - 定义错误码和错误信息

4. **API 规范生成**
   - 设置从代码自动生成 API 规范
   - 设置 schema 验证和一致性检查
   - 配置 API 版本控制和变更日志生成
   - 设置规范文件管理和版本控制

5. **文档内容增强**
   - 添加全面的 API 指南和教程
   - 添加错误处理和状态码文档（tRPC 错误码规范）
   - 添加限流和使用指南
   - 文档化 tRPC 拦截器和插件使用
   - 提供快速开始指南和最佳实践

## Mermaid 图表模板示例

自动生成三类图表并以 Mermaid 代码块嵌入文档：
- **架构图**（graph TD）：`Client --> Gateway --> Service --> DB`
- **流程图**（flowchart TD）：`Start --> Auth{认证} --> Process --> Response --> End`
- **时序图**（sequenceDiagram）：`Client->>Gateway->>Service->>DB-->>Client`
