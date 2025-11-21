# -*- coding: utf-8 -*-
"""AST代码生成核心引擎 - 基于Jinja2模板生成高质量Python代码"""
from typing import List, Dict
from datetime import datetime
from core.logger import get_logger
from generator.service.TemplateManager import TemplateManager
from generator.model.GenTable import GenTable
from generator.model.GenTableColumn import GenTableColumn

logger = get_logger(__name__)


class ASTCodeGenerator:
    """基于Jinja2模板的智能代码生成器"""
    
    def __init__(self):
        """初始化代码生成器"""
        self.template_manager = TemplateManager()
    
    def generate_code(self, gen_table: GenTable, columns: List[GenTableColumn], db_service=None) -> Dict[str, str]:
        """生成完整代码(Model/Schema/Controller/README)
        
        Args:
            gen_table: 表配置对象
            columns: 字段配置列表
            db_service: 数据库服务对象，用于查询关联关系
        
        Returns:
            Dict[str, str]: 文件类型->代码内容的映射字典
        """
        try:
            context = self._build_template_context(gen_table, columns, db_service) # 构建模板上下文
            
            code_files = {}
            
            # 如果是纯中间表，只生成Model
            if gen_table.tpl_category == 'link_table':
                code_files["model"] = self.template_manager.render_template("model.jinja2", context)
            else:
                # 正常生成所有文件
                code_files = {
                    "model": self.template_manager.render_template("model.jinja2", context),
                    "schema": self.template_manager.render_template("schema.jinja2", context),
                    "controller": self.template_manager.render_template("controller.jinja2", context)
                }
            
            logger.info(f"代码生成成功: {gen_table.table_name} -> {len(code_files)}个文件")
            return code_files
        except Exception as e:
            logger.error(f"代码生成失败 [{gen_table.table_name}]: {e}", exc_info=True)
            return {}
    
    def _build_template_context(self, gen_table: GenTable, columns: List[GenTableColumn], db_service=None) -> Dict:
        """构建Jinja2模板渲染所需的上下文数据"""
        
        # 获取关联关系
        relationships = []
        if db_service:
            relationships = db_service.get_relationships(gen_table.table_name)

        column_data = [] # 转换字段数据为模板所需格式
        for col in columns:
            column_data.append({
                "column_name": col.column_name,
                "column_comment": col.column_comment or col.column_name,
                "column_type": col.column_type,
                "column_length": col.column_length,
                "python_field": col.python_field,
                "python_type": col.python_type,
                "is_pk": col.is_pk,
                "is_required": col.is_required,
                "is_insert": col.is_insert,
                "is_edit": col.is_edit,
                "is_list": col.is_list,
                "is_query": col.is_query,
                "query_type": col.query_type or "EQ"
            })
        
        return {
            "table_name": gen_table.table_name,
            "table_comment": gen_table.table_comment or gen_table.table_name,
            "class_name": gen_table.class_name,
            "module_name": gen_table.module_name,
            "business_name": gen_table.business_name,
            "function_name": gen_table.function_name or gen_table.table_comment or gen_table.table_name,
            "columns": column_data,
            "tpl_category": gen_table.tpl_category,
            "tree_code": gen_table.tree_code,
            "tree_parent_code": gen_table.tree_parent_code,
            "tree_name": gen_table.tree_name,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "relationships": relationships,
            "has_relations": len(relationships) > 0
        }
