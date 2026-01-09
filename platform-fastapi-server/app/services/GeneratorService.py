"""
代码生成器Service
处理代码生成历史记录
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Session

from app.models.GenHistory import GenHistory


class GeneratorService:
    def __init__(self, session: Session):
        self.session = session

    def create_history(
        self,
        table_id: int,
        table_name: str,
        gen_type: str,
        gen_content: str,
        file_count: int,
        status: str = '1'
    ) -> GenHistory:
        """创建生成历史记录"""
        history = GenHistory(
            table_id=table_id,
            table_name=table_name,
            gen_type=gen_type,
            gen_content=gen_content,
            file_count=file_count,
            status=status,
            create_time=datetime.now()
        )
        self.session.add(history)
        self.session.commit()
        return history

    def get_history_by_table(self, table_id: int) -> list:
        """根据表ID获取生成历史"""
        from sqlmodel import select
        statement = select(GenHistory).where(GenHistory.table_id == table_id)
        return self.session.exec(statement).all()

    def delete_history(self, history_id: int) -> bool:
        """删除生成历史"""
        history = self.session.get(GenHistory, history_id)
        if history:
            self.session.delete(history)
            self.session.commit()
            return True
        return False
