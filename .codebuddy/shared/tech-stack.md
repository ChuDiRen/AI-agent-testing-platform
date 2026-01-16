# 技术栈说明

## 后端技术栈

| 技术栈 | 框架 | ORM | 数据库 | 适用场景 |
|--------|------|-----|--------|---------|
| Java | Spring Boot 3.x | MyBatis-Plus | PostgreSQL + Redis | 企业系统、电商平台、高并发系统 |
| Python | FastAPI | SQLAlchemy | PostgreSQL + Redis | 数据分析、AI/ML应用、移动H5后端 |

## 前端技术栈

| 项目类型 | 框架 | UI组件库 | 状态管理 | HTTP客户端 |
|---------|------|---------|---------|-----------|
| PC端 | Vue3 + TypeScript | Element Plus | Pinia | Axios |
| 移动端H5 | Vue3 + TypeScript | Vant | Pinia | Axios |

## 技术栈推荐算法

```python
def recommend_tech_stack(project_type: str, scale: int) -> dict:
    """根据项目类型和规模推荐技术栈"""
    
    # 后端推荐
    if "企业" in project_type or "管理" in project_type:
        backend = "Spring Boot 3.x"
        backend_reason = "企业级稳定性、生态成熟"
    elif "数据" in project_type or "AI" in project_type:
        backend = "FastAPI"
        backend_reason = "Python生态、异步高性能"
    elif "移动" in project_type or "H5" in project_type:
        backend = "FastAPI"
        backend_reason = "快速开发、轻量级"
    else:
        backend = "Spring Boot 3.x"
        backend_reason = "通用性强"
    
    # 前端推荐
    if "移动" in project_type or "H5" in project_type:
        frontend = "Vue3 + Vant"
        frontend_reason = "移动端优化、组件丰富"
    else:
        frontend = "Vue3 + Element Plus"
        frontend_reason = "PC端最佳实践"
    
    # 数据库推荐
    if scale > 10000:
        database = "PostgreSQL + Redis"
        db_reason = "高并发支持"
    else:
        database = "PostgreSQL"
        db_reason = "功能完整、标准SQL"
    
    return {
        "backend": backend,
        "frontend": frontend,
        "database": database,
        "reasons": {
            "backend": backend_reason,
            "frontend": frontend_reason,
            "database": db_reason
        }
    }
```

## 关联Skill

- **Java后端**：`skills/development/java-springboot-dev/SKILL.md`
- **Python后端**：`skills/development/python-fastapi-dev/SKILL.md`
- **Vue3前端**：`skills/development/vue3-frontend-dev/SKILL.md`
