# -*- coding: utf-8 -*-
"""模板管理器"""
import os
from typing import Dict, List

from app.logger.logger import get_logger
from jinja2 import Environment, FileSystemLoader

logger = get_logger(__name__)

class TemplateManager:
    """代码模板管理器 - 支持Jinja2模板渲染"""
    
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # 默认模板目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(os.path.dirname(current_dir), 'templates')
        
        self.template_dir = template_dir
        if os.path.exists(template_dir):
            self.env = Environment(loader=FileSystemLoader(template_dir), auto_reload=True)
            self.env.cache = None  # 禁用模板缓存,确保每次都读取最新模板
        else:
            logger.warning(f"模板目录不存在: {template_dir}")
            self.env = None
    
    def render_template(self, template_name: str, context: Dict) -> str: # 渲染模板
        """使用Jinja2渲染模板"""
        try:
            if self.env:
                template = self.env.get_template(template_name)
                return template.render(**context)
            else:
                logger.error("模板环境未初始化")
                return ""
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            return ""
    
    def get_available_templates(self) -> List[str]: # 获取可用模板列表
        """获取所有可用的模板文件"""
        try:
            if os.path.exists(self.template_dir):
                return [f for f in os.listdir(self.template_dir) if f.endswith('.jinja2')]
            return []
        except Exception as e:
            logger.error(f"获取模板列表失败: {e}")
            return []
