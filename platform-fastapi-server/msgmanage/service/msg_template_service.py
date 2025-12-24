"""
消息模板 Service
"""
import json
import re
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, col
from msgmanage.model.msg_template import MsgTemplate
from msgmanage.schemas.msg_template_schema import (
    MsgTemplateInsert,
    MsgTemplateUpdate,
    MsgTemplateQuery,
    TemplateVariable
)
from core.logger import get_logger

logger = get_logger(__name__)


class MsgTemplateService:
    """消息模板服务"""

    def __init__(self, session: Session):
        self.session = session

    # ========== CRUD 操作 ==========

    def query_by_page(self, query: MsgTemplateQuery) -> Dict[str, Any]:
        """分页查询模板"""
        try:
            # 构建查询
            stmt = select(MsgTemplate)

            # 添加过滤条件
            if query.template_code:
                stmt = stmt.where(MsgTemplate.template_code.like(f"%{query.template_code}%"))
            if query.template_name:
                stmt = stmt.where(MsgTemplate.template_name.like(f"%{query.template_name}%"))
            if query.template_type:
                stmt = stmt.where(MsgTemplate.template_type == query.template_type)
            if query.channel_type:
                stmt = stmt.where(MsgTemplate.channel_type == query.channel_type)
            if query.status is not None:
                stmt = stmt.where(MsgTemplate.status == query.status)

            # 获取总数
            total_stmt = select(MsgTemplate.id)
            if query.template_code:
                total_stmt = total_stmt.where(MsgTemplate.template_code.like(f"%{query.template_code}%"))
            if query.template_name:
                total_stmt = total_stmt.where(MsgTemplate.template_name.like(f"%{query.template_name}%"))
            if query.template_type:
                total_stmt = total_stmt.where(MsgTemplate.template_type == query.template_type)
            if query.channel_type:
                total_stmt = total_stmt.where(MsgTemplate.channel_type == query.channel_type)
            if query.status is not None:
                total_stmt = total_stmt.where(MsgTemplate.status == query.status)

            total = len(self.session.exec(total_stmt).all())

            # 分页
            offset = (query.page - 1) * query.page_size
            stmt = stmt.offset(offset).limit(query.page_size).order_by(MsgTemplate.created_time.desc())

            # 执行查询
            templates = self.session.exec(stmt).all()

            # 转换为响应格式
            result_list = []
            for template in templates:
                result_list.append(self._to_dict(template))

            return {
                "list": result_list,
                "total": total
            }
        except Exception as e:
            logger.error(f"分页查询模板失败: {e}")
            raise

    def get_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询模板"""
        try:
            stmt = select(MsgTemplate).where(MsgTemplate.id == template_id)
            template = self.session.exec(stmt).first()
            if template:
                return self._to_dict(template)
            return None
        except Exception as e:
            logger.error(f"查询模板失败: {e}")
            raise

    def get_by_code(self, template_code: str) -> Optional[MsgTemplate]:
        """根据模板编码查询"""
        try:
            stmt = select(MsgTemplate).where(
                MsgTemplate.template_code == template_code,
                MsgTemplate.status == 1
            )
            return self.session.exec(stmt).first()
        except Exception as e:
            logger.error(f"根据编码查询模板失败: {e}")
            raise

    def create(self, template_data: MsgTemplateInsert, creator: str = "") -> Dict[str, Any]:
        """创建模板"""
        try:
            # 检查编码是否已存在
            existing = self.get_by_code(template_data.template_code)
            if existing:
                raise ValueError(f"模板编码 '{template_data.template_code}' 已存在")

            # 转换变量列表为JSON
            variables_json = json.dumps([v.model_dump() for v in template_data.variables], ensure_ascii=False)
            example_params_json = json.dumps(template_data.example_params, ensure_ascii=False)

            # 创建模板对象
            template = MsgTemplate(
                template_code=template_data.template_code,
                template_name=template_data.template_name,
                template_type=template_data.template_type,
                channel_type=template_data.channel_type,
                title=template_data.title or "",
                content=template_data.content,
                variables=variables_json,
                example_params=example_params_json,
                status=template_data.status,
                remark=template_data.remark or "",
                created_by=creator
            )

            self.session.add(template)
            self.session.commit()
            self.session.refresh(template)

            logger.info(f"创建模板成功: {template.template_code}")
            return self._to_dict(template)
        except Exception as e:
            self.session.rollback()
            logger.error(f"创建模板失败: {e}")
            raise

    def update(self, template_data: MsgTemplateUpdate) -> Dict[str, Any]:
        """更新模板"""
        try:
            stmt = select(MsgTemplate).where(MsgTemplate.id == template_data.id)
            template = self.session.exec(stmt).first()
            if not template:
                raise ValueError(f"模板ID {template_data.id} 不存在")

            # 更新字段
            if template_data.template_name is not None:
                template.template_name = template_data.template_name
            if template_data.template_type is not None:
                template.template_type = template_data.template_type
            if template_data.channel_type is not None:
                template.channel_type = template_data.channel_type
            if template_data.title is not None:
                template.title = template_data.title
            if template_data.content is not None:
                template.content = template_data.content
            if template_data.variables is not None:
                template.variables = json.dumps([v.model_dump() for v in template_data.variables], ensure_ascii=False)
            if template_data.example_params is not None:
                template.example_params = json.dumps(template_data.example_params, ensure_ascii=False)
            if template_data.status is not None:
                template.status = template_data.status
            if template_data.remark is not None:
                template.remark = template_data.remark

            from datetime import datetime
            template.updated_time = datetime.now()

            self.session.commit()
            self.session.refresh(template)

            logger.info(f"更新模板成功: {template.template_code}")
            return self._to_dict(template)
        except Exception as e:
            self.session.rollback()
            logger.error(f"更新模板失败: {e}")
            raise

    def delete(self, template_id: int) -> bool:
        """删除模板"""
        try:
            stmt = select(MsgTemplate).where(MsgTemplate.id == template_id)
            template = self.session.exec(stmt).first()
            if not template:
                raise ValueError(f"模板ID {template_id} 不存在")

            self.session.delete(template)
            self.session.commit()

            logger.info(f"删除模板成功: {template.template_code}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"删除模板失败: {e}")
            raise

    # ========== 模板渲染 ==========

    def render_template(self, template_code: str, params: Dict[str, Any]) -> Dict[str, str]:
        """
        渲染模板（替换变量）

        Args:
            template_code: 模板编码
            params: 替换参数

        Returns:
            {"title": "替换后的标题", "content": "替换后的内容"}
        """
        template = self.get_by_code(template_code)
        if not template:
            raise ValueError(f"模板 '{template_code}' 不存在或已禁用")

        # 提取模板中的变量
        variables = self._extract_variables(template.content + " " + (template.title or ""))

        # 验证必需参数
        missing_vars = [v for v in variables if v not in params]
        if missing_vars:
            logger.warning(f"模板 '{template_code}' 缺少参数: {missing_vars}")

        # 执行替换
        title = self._replace_variables(template.title or "", params)
        content = self._replace_variables(template.content, params)

        return {
            "title": title,
            "content": content
        }

    def preview_template(self, template_code: str, params: Dict[str, Any]) -> Dict[str, str]:
        """预览模板（使用示例参数或传入参数）"""
        template = self.get_by_code(template_code)
        if not template:
            raise ValueError(f"模板 '{template_code}' 不存在或已禁用")

        # 如果没有传入参数，使用示例参数
        if not params:
            try:
                params = json.loads(template.example_params or "{}")
            except:
                params = {}

        # 执行替换
        title = self._replace_variables(template.title or "", params)
        content = self._replace_variables(template.content, params)

        return {
            "title": title,
            "content": content
        }

    # ========== 私有方法 ==========

    def _to_dict(self, template: MsgTemplate) -> Dict[str, Any]:
        """转换为字典格式"""
        try:
            variables = json.loads(template.variables) if template.variables else []
            example_params = json.loads(template.example_params) if template.example_params else {}
        except:
            variables = []
            example_params = {}

        return {
            "id": template.id,
            "template_code": template.template_code,
            "template_name": template.template_name,
            "template_type": template.template_type,
            "channel_type": template.channel_type,
            "title": template.title or "",
            "content": template.content,
            "variables": variables,
            "example_params": example_params,
            "status": template.status,
            "remark": template.remark or "",
            "created_by": template.created_by or "",
            "created_time": template.created_time,
            "updated_time": template.updated_time
        }

    def _extract_variables(self, content: str) -> List[str]:
        """提取模板中的变量名"""
        pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(pattern, content)
        return list(set(variables))

    def _replace_variables(self, content: str, params: Dict[str, Any]) -> str:
        """替换模板中的变量"""
        if not content:
            return ""

        def replacer(match):
            var_name = match.group(1)
            return str(params.get(var_name, match.group(0)))

        pattern = r'\{\{(\w+)\}\}'
        return re.sub(pattern, replacer, content)


# 便捷函数
def get_template_service(session: Session) -> MsgTemplateService:
    """获取模板服务实例"""
    return MsgTemplateService(session)
