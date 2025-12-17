# AI测试助手模块

"""
aiassistant - AI测试助手模块

基于 LangGraph Server 提供AI能力:
- text2case: 自然语言生成测试用例
- text2sql: 自然语言转SQL查询  
- text2api: 自然语言生成API请求

架构说明:
- langgraph/graphs/: LangGraph 图定义
- langgraph.json: LangGraph Server 配置

启动方式:
- langgraph dev   # 开发模式 (端口 2024)
- langgraph up    # 生产模式

前端调用:
- 使用 @langchain/langgraph-sdk 直接连接 LangGraph Server
"""

