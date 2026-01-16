# 10阶段标准化开发流程

## 流程概览

```
阶段1：需求分析 → 阶段2：原型设计 → 阶段3：任务拆分 →
阶段4：API文档 → 阶段5：分端开发 → 阶段6：联调测试 →
阶段7：代码评审 → 阶段8：接口测试 → 阶段9：E2E测试 →
阶段10：部署上线
```

## 阶段详情

| 阶段 | 名称 | 主要负责Agent | 辅助Agent | 产出物 |
|------|------|--------------|----------|-------|
| 1 | 需求分析 | team-orchestrator | product-manager | 技术选型文档 |
| 2 | 原型设计 | frontend-developer | product-manager | HTML原型页面 |
| 3 | 任务拆分 | product-manager | team-orchestrator | 前后端任务清单 |
| 4 | API文档 | backend-developer | product-manager | OpenAPI规范文档 |
| 5 | 分端开发 | frontend-developer + backend-developer | debugger（按需） | 前后端代码 |
| 6 | 联调测试 | frontend-developer + backend-developer | debugger（按需） | 联调报告 |
| 7 | 代码评审 | code-reviewer | frontend-developer + backend-developer | 代码审查报告 |
| 8 | 接口测试 | test-automator | backend-developer | 接口测试报告 |
| 9 | E2E测试 | test-automator | frontend-developer | E2E测试报告 |
| 10 | 部署上线 | deployment-specialist | team-orchestrator | 部署清单 |

## 阶段流转规则

1. **顺序执行**：按阶段顺序依次执行
2. **用户确认**：每个阶段完成后需用户确认
3. **可回退**：用户可输入"修改"回退到上一阶段
4. **按需调试**：任何阶段出现问题可调用 debugger

## 阶段调度代码

```python
STAGE_AGENT_MAP = {
    1: {"primary": "team-orchestrator", "secondary": "product-manager"},
    2: {"primary": "frontend-developer", "secondary": "product-manager"},
    3: {"primary": "product-manager", "secondary": "team-orchestrator"},
    4: {"primary": "backend-developer", "secondary": "product-manager"},
    5: {"primary": ["frontend-developer", "backend-developer"], "secondary": None},
    6: {"primary": ["frontend-developer", "backend-developer"], "secondary": None},
    7: {"primary": "code-reviewer", "secondary": ["frontend-developer", "backend-developer"]},
    8: {"primary": "test-automator", "secondary": "backend-developer"},
    9: {"primary": "test-automator", "secondary": "frontend-developer"},
    10: {"primary": "deployment-specialist", "secondary": "team-orchestrator"},
}

def dispatch_stage(stage: int):
    """根据阶段调度对应的Agent"""
    agents = STAGE_AGENT_MAP.get(stage)
    if agents:
        call_agent(agents["primary"])
        if agents["secondary"]:
            call_agent(agents["secondary"], assist=True)
```
