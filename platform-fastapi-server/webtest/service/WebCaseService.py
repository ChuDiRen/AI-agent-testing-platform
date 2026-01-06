"""
Web用例Service层
"""
import json
import uuid
from datetime import datetime
from typing import Tuple, List, Optional

from core.logger import get_logger
from sqlmodel import Session, select, func

from ..model.WebCaseModel import WebCase, WebCaseFolder
from ..schemas.WebCaseSchema import (
    WebCaseCreate, WebCaseUpdate, WebCaseQuery, WebCaseFolderCreate, 
    WebCaseFolderUpdate, WebCaseTreeNode, WebCaseStep
)

logger = get_logger(__name__)


class WebCaseService:
    """Web用例服务类"""
    
    @staticmethod
    def create_case(session: Session, case_data: WebCaseCreate) -> WebCase:
        """创建Web用例"""
        try:
            # 将步骤转换为JSON
            steps_json = json.dumps([step.dict() for step in case_data.steps], ensure_ascii=False)
            
            case = WebCase(
                name=case_data.name,
                description=case_data.description,
                project_id=case_data.project_id,
                folder_id=case_data.folder_id,
                priority=case_data.priority,
                status=case_data.status,
                tags=case_data.tags,
                pre_condition=case_data.pre_condition,
                post_condition=case_data.post_condition,
                steps=steps_json,
                content=case_data.content,
                file_type=case_data.file_type,
                expected_result=case_data.expected_result,
                author=case_data.author,
                sort_order=case_data.sort_order
            )
            
            session.add(case)
            session.commit()
            session.refresh(case)
            logger.info(f"创建Web用例成功，ID: {case.id}, 名称: {case.name}")
            return case
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update_case(session: Session, case_id: int, case_data: WebCaseUpdate) -> Optional[WebCase]:
        """更新Web用例"""
        try:
            case = session.get(WebCase, case_id)
            if not case:
                return None
            
            # 更新字段
            update_data = case_data.dict(exclude_unset=True)
            
            # 处理步骤更新
            if 'steps' in update_data:
                steps_json = json.dumps([step.dict() for step in update_data['steps']], ensure_ascii=False)
                update_data['steps'] = steps_json
            
            for field, value in update_data.items():
                setattr(case, field, value)
            
            case.update_time = datetime.now()
            session.commit()
            session.refresh(case)
            logger.info(f"更新Web用例成功，ID: {case.id}")
            return case
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_case(session: Session, case_id: int) -> bool:
        """删除Web用例"""
        try:
            case = session.get(WebCase, case_id)
            if not case:
                return False
            
            session.delete(case)
            session.commit()
            logger.info(f"删除Web用例成功，ID: {case_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete_cases(session: Session, case_ids: List[int]) -> int:
        """批量删除Web用例"""
        try:
            count = 0
            for case_id in case_ids:
                if WebCaseService.delete_case(session, case_id):
                    count += 1
            logger.info(f"批量删除Web用例成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_case_by_id(session: Session, case_id: int) -> Optional[WebCase]:
        """根据ID获取Web用例"""
        try:
            return session.get(WebCase, case_id)
        except Exception as e:
            logger.error(f"查询Web用例失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_cases_by_page(session: Session, query: WebCaseQuery) -> Tuple[List[WebCase], int]:
        """分页查询Web用例"""
        try:
            # 构建查询条件
            statement = select(WebCase)
            
            # 添加过滤条件
            if query.project_id:
                statement = statement.where(WebCase.project_id == query.project_id)
            if query.folder_id:
                statement = statement.where(WebCase.folder_id == query.folder_id)
            if query.name:
                statement = statement.where(WebCase.name.contains(query.name))
            if query.status:
                statement = statement.where(WebCase.status == query.status)
            if query.priority:
                statement = statement.where(WebCase.priority == query.priority)
            if query.author:
                statement = statement.where(WebCase.author.contains(query.author))
            if query.tags:
                statement = statement.where(WebCase.tags.contains(query.tags))
            
            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = statement.offset((query.page - 1) * query.pageSize).limit(query.pageSize)
            statement = statement.order_by(WebCase.sort_order, WebCase.create_time.desc())
            cases = session.exec(statement).all()
            
            return list(cases), total
        except Exception as e:
            logger.error(f"分页查询Web用例失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def create_folder(session: Session, folder_data: WebCaseFolderCreate) -> WebCaseFolder:
        """创建用例目录"""
        try:
            # 计算层级和路径
            level = 1
            path = folder_data.name
            
            if folder_data.parent_id:
                parent = session.get(WebCaseFolder, folder_data.parent_id)
                if parent:
                    level = parent.level + 1
                    path = f"{parent.path}/{folder_data.name}"
            
            folder = WebCaseFolder(
                name=folder_data.name,
                project_id=folder_data.project_id,
                parent_id=folder_data.parent_id,
                level=level,
                path=path,
                description=folder_data.description,
                sort_order=folder_data.sort_order
            )
            
            session.add(folder)
            session.commit()
            session.refresh(folder)
            logger.info(f"创建用例目录成功，ID: {folder.id}, 名称: {folder.name}")
            return folder
        except Exception as e:
            session.rollback()
            logger.error(f"创建用例目录失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update_folder(session: Session, folder_id: int, folder_data: WebCaseFolderUpdate) -> Optional[WebCaseFolder]:
        """更新用例目录"""
        try:
            folder = session.get(WebCaseFolder, folder_id)
            if not folder:
                return None
            
            # 更新字段
            update_data = folder_data.dict(exclude_unset=True)
            
            # 如果更新了父目录或名称，需要重新计算路径
            if 'parent_id' in update_data or 'name' in update_data:
                parent_id = update_data.get('parent_id', folder.parent_id)
                name = update_data.get('name', folder.name)
                
                level = 1
                path = name
                
                if parent_id:
                    parent = session.get(WebCaseFolder, parent_id)
                    if parent:
                        level = parent.level + 1
                        path = f"{parent.path}/{name}"
                
                update_data['level'] = level
                update_data['path'] = path
                
                # TODO: 更新所有子目录的路径
                # WebCaseService._update_children_paths(session, folder_id, path)
            
            for field, value in update_data.items():
                setattr(folder, field, value)
            
            folder.update_time = datetime.now()
            session.commit()
            session.refresh(folder)
            logger.info(f"更新用例目录成功，ID: {folder.id}")
            return folder
        except Exception as e:
            session.rollback()
            logger.error(f"更新用例目录失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_folder(session: Session, folder_id: int) -> bool:
        """删除用例目录"""
        try:
            folder = session.get(WebCaseFolder, folder_id)
            if not folder:
                return False
            
            # 检查是否有子目录
            children_statement = select(WebCaseFolder).where(WebCaseFolder.parent_id == folder_id)
            children = session.exec(children_statement).all()
            if children:
                raise ValueError("目录下还有子目录，无法删除")
            
            # 检查是否有用例
            case_statement = select(WebCase).where(WebCase.folder_id == folder_id)
            cases = session.exec(case_statement).all()
            if cases:
                raise ValueError("目录下还有用例，无法删除")
            
            session.delete(folder)
            session.commit()
            logger.info(f"删除用例目录成功，ID: {folder_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除用例目录失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_case_tree(session: Session, project_id: int) -> List[WebCaseTreeNode]:
        """获取用例目录树"""
        try:
            tree_nodes = []
            
            # 获取所有目录
            folder_statement = select(WebCaseFolder).where(
                WebCaseFolder.project_id == project_id
            ).order_by(WebCaseFolder.level, WebCaseFolder.sort_order)
            folders = session.exec(folder_statement).all()
            
            # 获取所有用例
            case_statement = select(WebCase).where(
                WebCase.project_id == project_id
            ).order_by(WebCase.sort_order, WebCase.create_time)
            cases = session.exec(case_statement).all()
            
            # 构建目录树
            folder_dict = {folder.id: folder for folder in folders}
            
            for folder in folders:
                node = WebCaseTreeNode(
                    id=folder.id,
                    name=folder.name,
                    type='folder',
                    parent_id=folder.parent_id,
                    level=folder.level,
                    project_id=folder.project_id,
                    children=[]
                )
                tree_nodes.append(node)
            
            # 添加用例到目录树
            for case in cases:
                # 解析步骤
                steps = []
                if case.steps:
                    try:
                        steps_data = json.loads(case.steps)
                        steps = [WebCaseStep(**step) for step in steps_data]
                    except json.JSONDecodeError:
                        pass
                
                node = WebCaseTreeNode(
                    id=case.id,
                    name=case.name,
                    type='case',
                    parent_id=case.folder_id,
                    level=1,  # 用例层级设为1
                    project_id=case.project_id,
                    children=[],
                    case_info=case
                )
                tree_nodes.append(node)
            
            return tree_nodes
        except Exception as e:
            logger.error(f"获取用例目录树失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def copy_case(session: Session, case_id: int, new_name: Optional[str] = None) -> Optional[WebCase]:
        """复制用例"""
        try:
            original_case = session.get(WebCase, case_id)
            if not original_case:
                return None
            
            # 创建新用例
            new_case = WebCase(
                name=new_name or f"{original_case.name}_copy",
                description=original_case.description,
                project_id=original_case.project_id,
                folder_id=original_case.folder_id,
                priority=original_case.priority,
                status=original_case.status,
                tags=original_case.tags,
                pre_condition=original_case.pre_condition,
                post_condition=original_case.post_condition,
                steps=original_case.steps,
                content=original_case.content,
                file_type=original_case.file_type,
                expected_result=original_case.expected_result,
                author=original_case.author,
                sort_order=original_case.sort_order + 1
            )
            
            session.add(new_case)
            session.commit()
            session.refresh(new_case)
            logger.info(f"复制Web用例成功，原ID: {case_id}, 新ID: {new_case.id}")
            return new_case
        except Exception as e:
            session.rollback()
            logger.error(f"复制Web用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def parse_xmind_file(file_content: bytes) -> List[dict]:
        """解析XMind文件"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            import json
            from io import BytesIO
            
            # XMind文件实际上是ZIP文件
            with zipfile.ZipFile(BytesIO(file_content)) as zip_file:
                # 读取content.xml文件
                if 'content.xml' not in zip_file.namelist():
                    raise ValueError("无效的XMind文件格式")
                
                content_xml = zip_file.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # XMind命名空间
                ns = {'xmind': 'http://www.xmind.net/schema/2008/xmind'}
                
                # 解析主题
                cases = []
                
                def parse_topic(topic, parent_path=""):
                    """递归解析主题"""
                    title = topic.get('text', '')
                    current_path = f"{parent_path}/{title}" if parent_path else title
                    
                    # 检查是否为用例（包含测试步骤）
                    children = topic.findall('.//xmind:topics/xmind:topic', ns)
                    
                    if children and any(child.get('text', '').strip() for child in children):
                        # 这是一个用例
                        case_data = {
                            'name': title,
                            'description': f"从XMind导入: {current_path}",
                            'steps': [],
                            'expected_result': '',
                            'priority': 'medium',
                            'status': 'active',
                            'tags': 'xmind-import',
                            'pre_condition': '',
                            'post_condition': ''
                        }
                        
                        # 解析测试步骤
                        for i, child in enumerate(children):
                            step_text = child.get('text', '').strip()
                            if step_text:
                                # 判断是否为预期结果
                                if step_text.startswith(('预期:', '期望:', '结果:', '应该:')):
                                    case_data['expected_result'] = step_text
                                else:
                                    step = {
                                        'step_number': i + 1,
                                        'action': step_text,
                                        'expected': '',
                                        'keyword': 'manual',
                                        'locator_type': '',
                                        'locator_value': '',
                                        'input_data': '',
                                        'wait_time': 0
                                    }
                                    case_data['steps'].append(step)
                        
                        cases.append(case_data)
                    
                    # 递归处理子主题
                    for child in children:
                        parse_topic(child, current_path)
                
                # 从根主题开始解析
                root_topics = root.findall('.//xmind:topic', ns)
                for topic in root_topics:
                    parse_topic(topic)
                
                return cases
                
        except ImportError:
            logger.error("需要安装标准库来解析XMind文件")
            raise ValueError("XMind解析功能需要标准库支持")
        except Exception as e:
            logger.error(f"解析XMind文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def import_cases_from_xmind(session: Session, project_id: int, folder_id: Optional[int], 
                               import_cases: List[dict], overwrite: bool = False) -> dict:
        """从XMind导入用例"""
        try:
            from ..schemas.WebCaseSchema import WebCaseCreate
            
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for case_data in import_cases:
                try:
                    # 检查是否已存在同名用例
                    existing_statement = select(WebCase).where(
                        WebCase.project_id == project_id,
                        WebCase.name == case_data['name']
                    )
                    existing = session.exec(existing_statement).first()
                    
                    if existing:
                        if overwrite:
                            # 更新现有用例
                            existing.description = case_data['description']
                            existing.priority = case_data['priority']
                            existing.status = case_data['status']
                            existing.tags = case_data['tags']
                            existing.pre_condition = case_data['pre_condition']
                            existing.post_condition = case_data['post_condition']
                            existing.expected_result = case_data['expected_result']
                            existing.steps = json.dumps(case_data['steps'], ensure_ascii=False)
                            existing.update_time = datetime.now()
                            success_count += 1
                        else:
                            # 跳过已存在的用例
                            skipped_count += 1
                            continue
                    else:
                        # 创建新用例
                        case_create = WebCaseCreate(
                            name=case_data['name'],
                            description=case_data['description'],
                            project_id=project_id,
                            folder_id=folder_id,
                            priority=case_data['priority'],
                            status=case_data['status'],
                            tags=case_data['tags'],
                            pre_condition=case_data['pre_condition'],
                            post_condition=case_data['post_condition'],
                            steps=case_data['steps'],
                            expected_result=case_data['expected_result'],
                            author='xmind-import'
                        )
                        
                        new_case = WebCase(**case_create.dict())
                        session.add(new_case)
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"导入用例失败: {case_data.get('name', 'unknown')}, 错误: {e}")
                    error_count += 1
                    continue
            
            session.commit()
            
            result = {
                "total_cases": len(import_cases),
                "imported_cases": success_count,
                "skipped_cases": skipped_count,
                "error_cases": error_count
            }
            
            logger.info(f"XMind用例导入完成，成功: {success_count}, 跳过: {skipped_count}, 错误: {error_count}")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"XMind用例导入失败: {e}", exc_info=True)
            raise e
