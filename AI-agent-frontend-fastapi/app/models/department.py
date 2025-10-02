"""部门数据库模型 - 完全按照博客 t_dept 表结构设计"""
from sqlalchemy import Column, BigInteger, String, Float, DateTime
from app.core.database import Base


class Department(Base):
    """部门表模型 - 对应博客 t_dept 表"""
    __tablename__ = "t_dept"
    
    dept_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="部门ID")
    parent_id = Column(BigInteger, nullable=False, comment="上级部门ID")
    dept_name = Column(String(100), nullable=False, comment="部门名称")
    order_num = Column(Float, nullable=True, comment="排序")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    modify_time = Column(DateTime, nullable=True, comment="修改时间")
    
    def __repr__(self):
        return f"<Department(dept_id={self.dept_id}, dept_name={self.dept_name})>"

