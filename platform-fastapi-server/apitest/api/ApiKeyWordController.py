"""
关键字Controller - 已重构为使用Service层
"""
import json
import os
from datetime import datetime

from apitest.service.ApiKeywordService import ApiKeywordService
from config.dev_settings import settings
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiOperationTypeModel import OperationType
from plugin.model.PluginModel import Plugin
from ..schemas.ApiKeywordSchema import ApiKeyWordQuery, ApiKeyWordCreate, ApiKeyWordUpdate, KeywordFileRequest

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiKeyWord"
module_model = ApiKeyWord
module_route = APIRouter(prefix=f"/{module_name}", tags=["API关键字管理"])

# ==================== 路由处理函数 ====================

@module_route.get("/queryAll", summary="查询所有关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有关键字"""
    try:
        service = ApiKeywordService(session)
        datas = service.query_all()
        return respModel.ok_resp_list(lst=datas, msg="查询成功")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/queryByPage", summary="分页查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryByPage(query: ApiKeyWordQuery, session: Session = Depends(get_session)):
    """分页查询关键字"""
    try:
        service = ApiKeywordService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            keyword_name=query.name
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/queryById", summary="根据ID查询关键字")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.error_resp("关键字不存在")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/insert", summary="新增关键字", dependencies=[Depends(check_permission("apitest:keyword:add"))])
async def insert(keyword: ApiKeyWordCreate, session: Session = Depends(get_session)):
    """新增关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.create(**keyword.model_dump())
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新关键字", dependencies=[Depends(check_permission("apitest:keyword:edit"))]) # 更新关键字
async def update(keyword: ApiKeyWordUpdate, session: Session = Depends(get_session)):
    try:
        # 检查关键字方法名是否与其他记录重复
        if keyword.keyword_fun_name:
            check_statement = select(module_model).where(module_model.keyword_fun_name == keyword.keyword_fun_name)
            existing = session.exec(check_statement).first()
            if existing and existing.id != keyword.id:
                return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")
        statement = select(module_model).where(module_model.id == keyword.id)
        db_data = session.exec(statement).first()
        if db_data:
            update_data = keyword.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_data, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除关键字", dependencies=[Depends(check_permission("apitest:keyword:delete"))]) # 删除关键字
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.post("/keywordFile", summary="生成关键字文件", dependencies=[Depends(check_permission("apitest:keyword:generate"))]) # 生成关键字文件
async def keywordFile(request: KeywordFileRequest):
    try:
        file_name = request.keyword_fun_name
        keyword_value = request.keyword_value
        keywords_dir = str(settings.KEYWORDS_DIR)
        os.makedirs(keywords_dir, exist_ok=True)
        with open(f'{keywords_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
            f.write(keyword_value)
        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.get("/queryByOperationType", summary="根据操作类型查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 根据操作类型ID查询关键字列表
async def queryByOperationType(operation_type_id: int = Query(...), session: Session = Depends(get_session)):
    """根据操作类型ID查询关键字列表"""
    try:
        statement = select(module_model).where(module_model.operation_type_id == operation_type_id)
        datas = session.exec(statement).all()
        result = [
            {
                "id": data.id,
                "name": data.name,
                "keyword_fun_name": data.keyword_fun_name,
                "keyword_desc": data.keyword_desc,
                "operation_type_id": data.operation_type_id,
                "is_enabled": data.is_enabled
            } for data in datas
        ]
        return respModel.ok_resp_list(lst=result, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getKeywordFields", summary="获取关键字字段描述", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 获取关键字的字段描述
async def getKeywordFields(keyword_id: int = Query(...), session: Session = Depends(get_session)):
    """获取关键字的字段描述（解析keyword_desc或从代码中提取）"""
    try:
        import json
        import re
        
        # 查询关键字
        keyword = session.get(module_model, keyword_id)
        if not keyword:
            return respModel.error_resp("关键字不存在")
        
        # 尝试解析keyword_desc为JSON
        try:
            if keyword.keyword_desc:
                fields = json.loads(keyword.keyword_desc)
                # 这里 keyword_desc 本身就是字段定义列表，直接以数组形式返回
                if isinstance(fields, list):
                    return respModel.ok_resp_simple(lst=fields, msg="查询成功")
                else:
                    return respModel.ok_resp_simple(lst=[fields], msg="查询成功")
        except json.JSONDecodeError:
            # 不是JSON格式，尝试从代码中提取
            pass
        
        # 从keyword_value（函数代码）中提取参数
        fields = []
        if keyword.keyword_value:
            # 匹配 kwargs.get("PARAM_NAME", default) 模式
            pattern = r'kwargs\.get\s*\(\s*["\'](\w+)["\']\s*(?:,\s*([^)]+))?\)'
            matches = re.findall(pattern, keyword.keyword_value)
            
            for param_name, default_value in matches:
                field = {
                    "name": param_name,
                    "type": "string",
                    "required": default_value.strip() == "None" if default_value else True,
                    "description": f"参数: {param_name}",
                    "default": "" if not default_value or default_value.strip() == "None" else default_value.strip().strip("'\"")
                }
                fields.append(field)
        
        # 最终返回字段定义数组
        if fields:
            return respModel.ok_resp_simple(lst=fields, msg="查询成功")
        else:
            return respModel.ok_resp_simple(lst=[], msg="该关键字没有字段描述")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/syncFromPlugin", summary="从执行引擎同步关键字", dependencies=[Depends(check_permission("apitest:keyword:add"))])
async def syncFromPlugin(
    plugin_id: int = Query(..., description="执行引擎插件ID"),
    session: Session = Depends(get_session)
):
    """
    从执行引擎插件同步关键字到关键字表
    - 读取插件的 keywords 字段
    - 根据分类自动匹配或创建操作类型
    - 自动创建或更新关键字记录
    """
    try:
        # 查询插件
        plugin = session.get(Plugin, plugin_id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        if not plugin.keywords:
            return respModel.error_resp(msg="该插件没有关键字定义，请先上传包含 keywords.yaml 的插件")
        
        # 解析关键字
        try:
            keywords_data = json.loads(plugin.keywords) if isinstance(plugin.keywords, str) else plugin.keywords
        except json.JSONDecodeError:
            return respModel.error_resp(msg="关键字数据格式错误")
        
        # 分类名称到操作类型的映射（自动匹配或创建）
        category_to_operation_type = {}
        
        # 查询现有操作类型
        existing_op_types = session.exec(select(OperationType)).all()
        op_type_name_map = {op.operation_type_name: op.id for op in existing_op_types}
        
        def normalize_category(cat: str) -> str:
            """标准化分类名称：去除后缀、简化名称"""
            # 去除 (待实现) 等后缀
            cat = cat.replace(" (待实现)", "").replace("(待实现)", "").strip()
            # 去除 "类关键字" 后缀
            cat = cat.replace("类关键字", "").replace("关键字", "").strip()
            return cat
        
        def find_matching_op_type(category: str) -> int | None:
            """查找匹配的操作类型ID"""
            normalized = normalize_category(category)
            # 直接匹配
            if normalized in op_type_name_map:
                return op_type_name_map[normalized]
            # 模糊匹配：检查是否包含关键词
            for op_name, op_id in op_type_name_map.items():
                if normalized in op_name or op_name in normalized:
                    return op_id
            return None
        
        # 分类名称简化映射（用于创建新类型时的标准名称）
        category_mapping = {
            "HTTP请求": "HTTP请求",
            "数据提取": "数据提取",
            "断言验证": "断言验证",
            "数据库操作": "数据库操作",
            "工具": "工具方法",
            "文件操作": "文件操作",
            "Python方法": "Python方法",
            "未分类": "其他"
        }
        
        created_count = 0
        updated_count = 0
        new_op_types = []
        
        for keyword_name, keyword_info in keywords_data.items():
            params = keyword_info.get("params", [])
            category = keyword_info.get("category", "未分类")
            description = keyword_info.get("description", "")
            keyword_code = keyword_info.get("code", "")  # 获取关键字方法代码
            
            # 获取或创建操作类型
            if category not in category_to_operation_type:
                # 先尝试匹配现有操作类型
                matched_op_id = find_matching_op_type(category)
                
                if matched_op_id:
                    category_to_operation_type[category] = matched_op_id
                else:
                    # 标准化分类名称后创建新类型
                    normalized = normalize_category(category)
                    simple_name = category_mapping.get(normalized, normalized)
                    
                    # 再次检查标准化后的名称是否存在
                    if simple_name in op_type_name_map:
                        category_to_operation_type[category] = op_type_name_map[simple_name]
                    else:
                        # 创建新操作类型
                        new_op_type = OperationType(
                            operation_type_name=simple_name,
                            ex_fun_name=simple_name.lower().replace(" ", "_"),
                            create_time=datetime.now()
                        )
                        session.add(new_op_type)
                        session.flush()  # 获取 ID
                        category_to_operation_type[category] = new_op_type.id
                        op_type_name_map[simple_name] = new_op_type.id
                        new_op_types.append(simple_name)
            
            operation_type_id = category_to_operation_type[category]
            
            # 构建字段描述 JSON
            fields_desc = []
            for param in params:
                fields_desc.append({
                    "name": param,
                    "type": "string",
                    "required": True,
                    "description": f"参数: {param}"
                })
            
            # 检查是否已存在
            existing = session.exec(
                select(module_model).where(module_model.keyword_fun_name == keyword_name)
            ).first()
            
            if existing:
                # 更新现有记录
                existing.plugin_id = plugin.id
                existing.plugin_code = plugin.plugin_code
                existing.category = category
                existing.operation_type_id = operation_type_id
                existing.keyword_desc = json.dumps(fields_desc, ensure_ascii=False)
                # 更新方法体代码（如果有）
                if keyword_code:
                    existing.keyword_value = keyword_code
                session.add(existing)
                updated_count += 1
            else:
                # 创建新记录
                new_keyword = module_model(
                    name=keyword_name,
                    keyword_fun_name=keyword_name,
                    keyword_desc=json.dumps(fields_desc, ensure_ascii=False),
                    keyword_value=keyword_code,  # 存入方法体代码
                    operation_type_id=operation_type_id,
                    is_enabled="1",
                    plugin_id=plugin.id,
                    plugin_code=plugin.plugin_code,
                    category=category,
                    create_time=datetime.now()
                )
                session.add(new_keyword)
                created_count += 1
        
        session.commit()
        
        msg = f"同步成功：新增 {created_count} 个，更新 {updated_count} 个关键字"
        if new_op_types:
            msg += f"，新建操作类型：{', '.join(new_op_types)}"
        
        return respModel.ok_resp(
            msg=msg,
            dic_t={
                "created": created_count,
                "updated": updated_count,
                "total": len(keywords_data),
                "new_operation_types": new_op_types
            }
        )
    except Exception as e:
        session.rollback()
        logger.error(f"同步关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"同步失败: {str(e)}")


@module_route.get("/queryByPlugin", summary="根据插件查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryByPlugin(
    plugin_id: int = Query(None, description="插件ID"),
    plugin_code: str = Query(None, description="插件代码"),
    session: Session = Depends(get_session)
):
    """根据执行引擎插件查询关联的关键字"""
    try:
        statement = select(module_model)
        if plugin_id:
            statement = statement.where(module_model.plugin_id == plugin_id)
        elif plugin_code:
            statement = statement.where(module_model.plugin_code == plugin_code)
        else:
            return respModel.error_resp(msg="请提供 plugin_id 或 plugin_code")
        
        datas = session.exec(statement).all()
        
        # 按分类组织
        categories = {}
        for data in datas:
            cat = data.category or "未分类"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "id": data.id,
                "name": data.name,
                "keyword_fun_name": data.keyword_fun_name,
                "keyword_desc": data.keyword_desc,
                "is_enabled": data.is_enabled
            })
        
        return respModel.ok_resp(obj={
            "total": len(datas),
            "categories": categories,
            "keywords": [
                {
                    "id": d.id,
                    "name": d.name,
                    "keyword_fun_name": d.keyword_fun_name,
                    "category": d.category,
                    "is_enabled": d.is_enabled
                } for d in datas
            ]
        })
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/queryGroupedByEngine", summary="按执行引擎分组查询所有关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryGroupedByEngine(session: Session = Depends(get_session)):
    """
    按执行引擎分组查询所有关键字
    返回格式：
    {
        "engines": [
            {
                "plugin_code": "api_engine",
                "plugin_name": "API引擎",
                "plugin_id": 1,
                "keywords": [
                    {"id": 1, "name": "send_request", "keyword_desc": "...", "category": "HTTP请求"},
                    ...
                ]
            },
            ...
        ]
    }
    """
    try:
        # 查询所有启用的关键字
        statement = select(module_model).where(module_model.is_enabled == "1")
        keywords = session.exec(statement).all()
        
        # 查询所有插件
        plugins = session.exec(select(Plugin).where(Plugin.is_enabled == 1)).all()
        plugin_map = {p.plugin_code: {"id": p.id, "name": p.plugin_name, "code": p.plugin_code} for p in plugins}
        
        # 按引擎分组
        engine_keywords = {}
        uncategorized = []
        
        for kw in keywords:
            plugin_code = kw.plugin_code or "uncategorized"
            
            if plugin_code not in engine_keywords:
                if plugin_code in plugin_map:
                    engine_keywords[plugin_code] = {
                        "plugin_code": plugin_code,
                        "plugin_name": plugin_map[plugin_code]["name"],
                        "plugin_id": plugin_map[plugin_code]["id"],
                        "keywords": []
                    }
                elif plugin_code == "uncategorized":
                    engine_keywords[plugin_code] = {
                        "plugin_code": "uncategorized",
                        "plugin_name": "未分类",
                        "plugin_id": None,
                        "keywords": []
                    }
                else:
                    # 插件不存在但有关键字关联
                    engine_keywords[plugin_code] = {
                        "plugin_code": plugin_code,
                        "plugin_name": plugin_code,
                        "plugin_id": kw.plugin_id,
                        "keywords": []
                    }
            
            # 解析关键字描述
            try:
                keyword_desc = json.loads(kw.keyword_desc) if kw.keyword_desc else []
            except:
                keyword_desc = []
            
            engine_keywords[plugin_code]["keywords"].append({
                "id": kw.id,
                "name": kw.name,
                "keyword_fun_name": kw.keyword_fun_name,
                "keyword_desc": keyword_desc,
                "category": kw.category or "未分类",
                "operation_type_id": kw.operation_type_id
            })
        
        # 转换为列表并排序
        engines = list(engine_keywords.values())
        # 按插件名称排序，未分类放最后
        engines.sort(key=lambda x: (x["plugin_code"] == "uncategorized", x["plugin_name"]))
        
        return respModel.ok_resp(obj={
            "engines": engines,
            "total_keywords": len(keywords),
            "total_engines": len(engines)
        })
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")