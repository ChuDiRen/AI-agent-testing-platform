"""
添加个人资料菜单到现有数据库
不会删除任何现有数据,只是添加profile菜单并分配给所有角色
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 先导入所有实体以避免关系映射问题
from app.entity.user import User  # noqa
from app.entity.role import Role  # noqa
from app.entity.menu import Menu  # noqa
from app.entity.department import Department  # noqa
from app.entity.user_role import UserRole  # noqa
from app.entity.role_menu import RoleMenu  # noqa
from app.entity.api_endpoint import ApiEndpoint  # noqa
from app.entity.role_api import RoleApi  # noqa

from app.db.session import SessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)


def add_profile_menu():
    """
    添加个人资料菜单到数据库
    """
    db = SessionLocal()
    try:
        # 检查profile菜单是否已存在
        existing_menu = db.query(Menu).filter(Menu.path == "/profile").first()
        if existing_menu:
            logger.info("Profile menu already exists, skipping...")
            print("✅ 个人资料菜单已存在,无需添加")
            return

        # 创建profile菜单
        profile_menu = Menu(
            parent_id=0,
            menu_name="个人资料",
            menu_type="0",
            path="/profile",
            component="/profile",
            icon="User",
            order_num=99  # 排在最后
        )
        db.add(profile_menu)
        db.flush()
        
        logger.info(f"Profile menu created with id: {profile_menu.id}")
        print(f"✅ 个人资料菜单创建成功 (ID: {profile_menu.id})")

        # 获取所有角色
        roles = db.query(Role).all()
        
        if not roles:
            logger.warning("No roles found in database")
            print("⚠️  数据库中没有找到角色")
            db.commit()
            return

        # 为所有角色分配profile菜单权限
        added_count = 0
        for role in roles:
            # 检查是否已经分配
            existing_rel = db.query(RoleMenu).filter(
                RoleMenu.role_id == role.id,
                RoleMenu.menu_id == profile_menu.id
            ).first()
            
            if not existing_rel:
                role_menu_rel = RoleMenu(role_id=role.id, menu_id=profile_menu.id)
                db.add(role_menu_rel)
                added_count += 1
                logger.info(f"Assigned profile menu to role: {role.role_name}")
                print(f"  ✓ 已分配给角色: {role.role_name}")

        db.commit()
        
        logger.info(f"Profile menu added successfully and assigned to {added_count} roles")
        print(f"\n✅ 个人资料菜单添加完成,已分配给 {added_count} 个角色")
        print("\n请重启后端服务或刷新前端页面以查看更改")

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding profile menu: {str(e)}")
        print(f"\n❌ 添加个人资料菜单失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("添加个人资料菜单到数据库")
    print("=" * 60)
    print()
    
    try:
        add_profile_menu()
    except Exception as e:
        print(f"\n执行失败: {str(e)}")
        sys.exit(1)

