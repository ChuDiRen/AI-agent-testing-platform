"""
部门闭包表模型
用于实现部门树形结构的快速查询
"""
from sqlalchemy import Column, BigInteger, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase


class _Base(_DeclarativeBase):
    """自定义Base类，不包含公共字段"""
    __allow_unmapped__ = True
    pass


class DeptClosure(_Base):
    """
    部门闭包表
    
    用于存储部门之间的所有路径关系，支持快速查询：
    - 查找某个部门的所有子孙部门
    - 查找某个部门的所有祖先部门
    - 计算部门的层级深度
    
    例如：
    - 部门树：总公司 -> 研发部 -> 测试组
    - 闭包表记录：
      * (总公司, 总公司, 0)
      * (研发部, 研发部, 0)
      * (研发部, 总公司, 1)
      * (测试组, 测试组, 0)
      * (测试组, 研发部, 1)
      * (测试组, 总公司, 2)
    """
    __tablename__ = "t_dept_closure"
    
    # 祖先部门ID
    ancestor_id = Column(BigInteger, primary_key=True, comment="祖先部门ID")
    
    # 后代部门ID
    descendant_id = Column(BigInteger, primary_key=True, comment="后代部门ID")
    
    # 层级（距离：0表示自己，1表示父子，2表示祖孙）
    level = Column(BigInteger, nullable=False, comment="层级距离")
    
    # 创建索引以提升查询性能
    __table_args__ = (
        Index("idx_ancestor", "ancestor_id"),
        Index("idx_descendant", "descendant_id"),
        Index("idx_level", "level"),
        {"comment": "部门闭包表"}
    )
