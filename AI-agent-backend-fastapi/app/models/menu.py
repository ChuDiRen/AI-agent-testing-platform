"""菜单数据库模型 - 完全按照博客 t_menu 表结构设计"""
from sqlalchemy import Column, Integer, String, CHAR, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Menu(Base):
    """菜单表模型 - 对应博客 t_menu 表"""
    __tablename__ = "t_menu"

    menu_id = Column(Integer, primary_key=True, autoincrement=True, comment="菜单/按钮ID")  # SQLite使用INTEGER支持自增
    parent_id = Column(Integer, nullable=False, comment="上级菜单ID")  # SQLite使用INTEGER支持自增
    menu_name = Column(String(50), nullable=False, comment="菜单/按钮名称")
    path = Column(String(255), nullable=True, comment="对应路由path")
    component = Column(String(255), nullable=True, comment="对应路由组件component")
    perms = Column(String(50), nullable=True, comment="权限标识")
    icon = Column(String(50), nullable=True, comment="图标")
    type = Column(CHAR(2), nullable=False, comment="类型 0菜单 1按钮")
    order_num = Column(Float, nullable=True, comment="排序")
    create_time = Column(DateTime, nullable=False, comment="创建时间")
    modify_time = Column(DateTime, nullable=True, comment="修改时间")
    
    # 关联关系
    roles = relationship("Role", secondary="t_role_menu", back_populates="menus")
    
    def __repr__(self):
        return f"<Menu(menu_id={self.menu_id}, menu_name={self.menu_name})>"

