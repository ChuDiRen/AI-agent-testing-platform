# Copyright (c) 2025 左岚. All rights reserved.
"""提示词模板服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import List, Optional

from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate


class PromptTemplateService:
    """提示词模板服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_template(
        self, 
        template_data: PromptTemplateCreate, 
        created_by: Optional[int] = None
    ) -> PromptTemplate:
        """创建提示词模板"""
        try:
            template = PromptTemplate(
                **template_data.model_dump(),
                created_by=created_by
            )
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            return template
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"创建提示词模板失败: {str(e)}")
    
    async def get_template(self, template_id: int) -> Optional[PromptTemplate]:
        """获取提示词模板"""
        result = await self.db.execute(
            select(PromptTemplate).where(PromptTemplate.template_id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def get_templates(
        self,
        template_type: Optional[str] = None,
        test_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[PromptTemplate]:
        """获取提示词模板列表"""
        conditions = []
        
        if template_type:
            conditions.append(PromptTemplate.template_type == template_type)
        if test_type:
            conditions.append(PromptTemplate.test_type == test_type)
        if is_active is not None:
            conditions.append(PromptTemplate.is_active == is_active)
        
        query = select(PromptTemplate)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(
            PromptTemplate.is_default.desc(),
            PromptTemplate.create_time.desc()
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_default_template(
        self,
        template_type: str = "testcase_generation",
        test_type: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """获取默认提示词模板"""
        conditions = [
            PromptTemplate.template_type == template_type,
            PromptTemplate.is_default == True,
            PromptTemplate.is_active == True
        ]
        
        if test_type:
            conditions.append(PromptTemplate.test_type == test_type)
        
        query = select(PromptTemplate).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_template(
        self,
        template_id: int,
        template_data: PromptTemplateUpdate
    ) -> PromptTemplate:
        """更新提示词模板"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("提示词模板不存在")
        
        try:
            # 更新字段
            for field, value in template_data.model_dump(exclude_unset=True).items():
                setattr(template, field, value)
            
            await self.db.commit()
            await self.db.refresh(template)
            return template
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"更新提示词模板失败: {str(e)}")
    
    async def delete_template(self, template_id: int) -> bool:
        """删除提示词模板"""
        template = await self.get_template(template_id)
        if not template:
            return False
        
        # 不允许删除默认模板
        if template.is_default:
            raise ValueError("不能删除默认模板")
        
        try:
            await self.db.delete(template)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"删除提示词模板失败: {str(e)}")
    
    async def set_default_template(self, template_id: int) -> PromptTemplate:
        """设置为默认模板"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("提示词模板不存在")
        
        try:
            # 取消同类型的其他默认模板
            await self.db.execute(
                update(PromptTemplate)
                .where(
                    and_(
                        PromptTemplate.template_type == template.template_type,
                        PromptTemplate.test_type == template.test_type,
                        PromptTemplate.template_id != template_id
                    )
                )
                .values(is_default=False)
            )
            
            # 设置当前模板为默认
            template.is_default = True
            await self.db.commit()
            await self.db.refresh(template)
            return template
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"设置默认模板失败: {str(e)}")

