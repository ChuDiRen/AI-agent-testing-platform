# 📦 Fullstack 插件

全栈开发插件，整合了前后端开发相关的所有功能。

## 包含组件

| 类型 | 名称 | 说明 |
|------|------|------|
| Command | `/dev` | 功能开发命令 |
| Command | `/crud` | CRUD 生成命令 |
| Skill | `crud-development` | CRUD 开发技能 |
| Skill | `ui-pc` | PC 端 UI 技能 |
| Agent | `backend-architect` | 后端架构专家 |
| Agent | `frontend-developer` | 前端开发专家 |

## 使用方式

```bash
# 开发新功能
/dev 用户管理模块

# 生成 CRUD
/crud User --fields "name:str,email:str,status:int"

# 仅后端
/dev 用户管理 --scope backend

# 仅前端
/dev 用户管理 --scope frontend
```

## 引用模板

- `templates/code-patterns.md` - 四层架构和 Vue 组件模板
