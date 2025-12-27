"""
接口目录Service - 已重构为静态方法模式
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select, and_
from core.logger import get_logger

from ..model.ApiFolderModel import ApiFolder
from ..model.ApiInfoModel import ApiInfo
from ..schemas.ApiFolderSchema import ApiFolderQuery, ApiFolderCreate, ApiFolderUpdate

logger = get_logger(__name__)


class ApiFolderService:
    """接口目录服务类 - 使用静态方法模式"""

    @staticmethod
    def query_tree(session: Session, project_id: int) -> List[Dict[str, Any]]:
        """查询项目的目录树结构（包含接口）"""
        folder_statement = select(ApiFolder).where(
            ApiFolder.project_id == project_id
        ).order_by(ApiFolder.sort_order, ApiFolder.id)
        folders = session.exec(folder_statement).all()

        api_statement = select(ApiInfo).where(
            ApiInfo.project_id == project_id
        ).order_by(ApiInfo.id)
        apis = session.exec(api_statement).all()

        return ApiFolderService._build_folder_tree(list(folders), list(apis))

    @staticmethod
    def query_list(session: Session, project_id: int, parent_id: Optional[int] = None) -> List[ApiFolder]:
        """查询指定目录下的子目录列表"""
        statement = select(ApiFolder).where(ApiFolder.project_id == project_id)

        if parent_id is not None:
            statement = statement.where(ApiFolder.parent_id == parent_id)

        statement = statement.order_by(ApiFolder.sort_order, ApiFolder.id)
        return list(session.exec(statement).all())

    @staticmethod
    def query_by_id(session: Session, folder_id: int) -> Optional[ApiFolder]:
        """根据ID查询目录"""
        return session.get(ApiFolder, folder_id)

    @staticmethod
    def create(session: Session, folder: ApiFolderCreate) -> Optional[ApiFolder]:
        """新增目录"""
        # 验证父目录
        if folder.parent_id > 0:
            parent = session.get(ApiFolder, folder.parent_id)
            if not parent or parent.project_id != folder.project_id:
                return None

        # 获取排序号
        sort_order = folder.sort_order if hasattr(folder, 'sort_order') else 0
        if sort_order == 0:
            statement = select(ApiFolder).where(
                and_(
                    ApiFolder.project_id == folder.project_id,
                    ApiFolder.parent_id == folder.parent_id
                )
            ).order_by(ApiFolder.sort_order.desc())
            last_folder = session.exec(statement).first()
            if last_folder:
                sort_order = last_folder.sort_order + 1

        data = ApiFolder(
            **folder.model_dump(exclude={'sort_order'}),
            sort_order=sort_order,
            create_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, folder: ApiFolderUpdate) -> Optional[ApiFolder]:
        """更新目录"""
        statement = select(ApiFolder).where(ApiFolder.id == folder.id)
        db_folder = session.exec(statement).first()
        if not db_folder:
            return None

        update_data = folder.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_folder, key, value)
        session.commit()
        return db_folder

    @staticmethod
    def delete(session: Session, folder_id: int, move_to_parent: bool = True) -> bool:
        """删除目录"""
        folder = session.get(ApiFolder, folder_id)
        if not folder:
            return False

        # 处理子目录
        child_folders = session.exec(
            select(ApiFolder).where(ApiFolder.parent_id == folder_id)
        ).all()

        if child_folders and not move_to_parent:
            return False

        if move_to_parent:
            for child in child_folders:
                child.parent_id = folder.parent_id
                session.add(child)

        # 处理接口
        apis = session.exec(
            select(ApiInfo).where(ApiInfo.folder_id == folder_id)
        ).all()

        if move_to_parent:
            for api in apis:
                api.folder_id = folder.parent_id
                session.add(api)

        session.delete(folder)
        session.commit()
        return True

    @staticmethod
    def move(session: Session, folder_id: int, target_parent_id: int, target_sort_order: int = 0) -> bool:
        """移动目录到新的父目录"""
        folder = session.get(ApiFolder, folder_id)
        if not folder:
            return False

        # 验证目标父目录
        if target_parent_id > 0:
            parent = session.get(ApiFolder, target_parent_id)
            if not parent or parent.project_id != folder.project_id:
                return False

            # 检查是否会形成循环引用
            if ApiFolderService._is_ancestor(session, folder_id, target_parent_id):
                return False

        folder.parent_id = target_parent_id
        if target_sort_order > 0:
            folder.sort_order = target_sort_order
        session.commit()
        return True

    @staticmethod
    def move_apis(session: Session, folder_id: int, api_ids: List[int]) -> int:
        """批量移动接口到指定目录"""
        folder = session.get(ApiFolder, folder_id)
        if not folder:
            return 0

        moved_count = 0
        for api_id in api_ids:
            api = session.get(ApiInfo, api_id)
            if api:
                api.folder_id = folder_id
                session.add(api)
                moved_count += 1

        if moved_count > 0:
            session.commit()

        return moved_count

    @staticmethod
    def batch_sort(session: Session, folder_sorts: List[Dict[str, int]]) -> bool:
        """批量更新目录排序"""
        for item in folder_sorts:
            folder_id = item.get('id')
            sort_order = item.get('sort_order')
            if folder_id and sort_order is not None:
                folder = session.get(ApiFolder, folder_id)
                if folder:
                    folder.sort_order = sort_order

        session.commit()
        return True

    @staticmethod
    def get_path(session: Session, folder_id: int) -> List[Dict[str, Any]]:
        """获取目录的完整路径（面包屑）"""
        path = []
        current = session.get(ApiFolder, folder_id)

        while current:
            path.insert(0, {
                "id": current.id,
                "folder_name": current.folder_name,
                "parent_id": current.parent_id
            })
            if current.parent_id > 0:
                current = session.get(ApiFolder, current.parent_id)
            else:
                break

        return path

    @staticmethod
    def _build_folder_tree(folders: List[ApiFolder], apis: List[ApiInfo]) -> List[Dict[str, Any]]:
        """构建目录树"""
        folder_map = {f.id: {
            "id": f.id,
            "folder_name": f.folder_name,
            "parent_id": f.parent_id,
            "sort_order": f.sort_order,
            "children": [],
            "apis": []
        } for f in folders}

        for api in apis:
            if api.folder_id and api.folder_id in folder_map:
                folder_map[api.folder_id]["apis"].append({
                    "id": api.id,
                    "api_name": api.api_name,
                    "request_url": getattr(api, 'request_url', getattr(api, 'api_path', '')),
                    "request_method": getattr(api, 'request_method', getattr(api, 'method', ''))
                })

        tree = []
        for folder in folders:
            if folder.parent_id == 0:
                tree.append(folder_map[folder.id])
            elif folder.parent_id in folder_map:
                folder_map[folder.parent_id]["children"].append(folder_map[folder.id])

        return tree

    @staticmethod
    def _is_ancestor(session: Session, ancestor_id: int, descendant_id: int) -> bool:
        """检查ancestor_id是否是descendant_id的祖先"""
        current = session.get(ApiFolder, descendant_id)
        while current and current.parent_id > 0:
            if current.parent_id == ancestor_id:
                return True
            current = session.get(ApiFolder, current.parent_id)
        return False
