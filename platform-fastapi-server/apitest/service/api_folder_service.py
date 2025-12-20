"""
接口目录Service
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_
from core.logger import get_logger

from ..model.ApiFolderModel import ApiFolder
from ..model.ApiInfoModel import ApiInfo

logger = get_logger(__name__)


class ApiFolderService:
    """接口目录服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_tree(self, project_id: int) -> List[Dict[str, Any]]:
        """查询项目的目录树结构（包含接口）"""
        folder_statement = select(ApiFolder).where(
            ApiFolder.project_id == project_id
        ).order_by(ApiFolder.sort_order, ApiFolder.id)
        folders = self.session.exec(folder_statement).all()
        
        api_statement = select(ApiInfo).where(
            ApiInfo.project_id == project_id
        ).order_by(ApiInfo.id)
        apis = self.session.exec(api_statement).all()
        
        return self._build_folder_tree(list(folders), list(apis))
    
    def query_list(self, project_id: int, parent_id: Optional[int] = None) -> List[ApiFolder]:
        """查询指定目录下的子目录列表"""
        statement = select(ApiFolder).where(ApiFolder.project_id == project_id)
        
        if parent_id is not None:
            statement = statement.where(ApiFolder.parent_id == parent_id)
        
        statement = statement.order_by(ApiFolder.sort_order, ApiFolder.id)
        return list(self.session.exec(statement).all())
    
    def get_by_id(self, folder_id: int) -> Optional[ApiFolder]:
        """根据ID查询目录"""
        return self.session.get(ApiFolder, folder_id)
    
    def create(self, project_id: int, folder_name: str, parent_id: int = 0,
               folder_desc: Optional[str] = None, sort_order: int = 0) -> Optional[ApiFolder]:
        """新增目录"""
        if parent_id > 0:
            parent = self.get_by_id(parent_id)
            if not parent or parent.project_id != project_id:
                return None
        
        statement = select(ApiFolder).where(
            and_(
                ApiFolder.project_id == project_id,
                ApiFolder.parent_id == parent_id
            )
        ).order_by(ApiFolder.sort_order.desc())
        last_folder = self.session.exec(statement).first()
        
        if sort_order == 0 and last_folder:
            sort_order = last_folder.sort_order + 1
        
        folder = ApiFolder(
            project_id=project_id,
            folder_name=folder_name,
            parent_id=parent_id,
            folder_desc=folder_desc,
            sort_order=sort_order,
            create_time=datetime.now()
        )
        self.session.add(folder)
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def update(self, folder_id: int, update_data: Dict[str, Any]) -> Optional[ApiFolder]:
        """更新目录"""
        folder = self.get_by_id(folder_id)
        if not folder:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(folder, key, value)
        
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def delete(self, folder_id: int) -> bool:
        """删除目录"""
        folder = self.get_by_id(folder_id)
        if not folder:
            return False
        
        child_folders = self.session.exec(
            select(ApiFolder).where(ApiFolder.parent_id == folder_id)
        ).all()
        if child_folders:
            return False
        
        apis = self.session.exec(
            select(ApiInfo).where(ApiInfo.folder_id == folder_id)
        ).all()
        if apis:
            return False
        
        self.session.delete(folder)
        self.session.commit()
        return True
    
    def move_folder(self, folder_id: int, target_parent_id: int) -> Optional[ApiFolder]:
        """移动目录到新的父目录"""
        folder = self.get_by_id(folder_id)
        if not folder:
            return None
        
        if target_parent_id > 0:
            parent = self.get_by_id(target_parent_id)
            if not parent or parent.project_id != folder.project_id:
                return None
            
            if self._is_ancestor(folder_id, target_parent_id):
                return None
        
        folder.parent_id = target_parent_id
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def batch_sort(self, folder_sorts: List[Dict[str, int]]) -> bool:
        """批量更新目录排序"""
        for item in folder_sorts:
            folder_id = item.get('id')
            sort_order = item.get('sort_order')
            if folder_id and sort_order is not None:
                folder = self.get_by_id(folder_id)
                if folder:
                    folder.sort_order = sort_order
        
        self.session.commit()
        return True
    
    def _build_folder_tree(self, folders: List[ApiFolder], apis: List[ApiInfo]) -> List[Dict[str, Any]]:
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
                    "api_path": api.api_path,
                    "method": api.method
                })
        
        tree = []
        for folder in folders:
            if folder.parent_id == 0:
                tree.append(folder_map[folder.id])
            elif folder.parent_id in folder_map:
                folder_map[folder.parent_id]["children"].append(folder_map[folder.id])
        
        return tree
    
    def _is_ancestor(self, ancestor_id: int, descendant_id: int) -> bool:
        """检查ancestor_id是否是descendant_id的祖先"""
        current = self.get_by_id(descendant_id)
        while current and current.parent_id > 0:
            if current.parent_id == ancestor_id:
                return True
            current = self.get_by_id(current.parent_id)
        return False
