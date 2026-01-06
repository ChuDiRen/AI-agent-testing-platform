"""
Web元素Service层
"""
from datetime import datetime
from typing import Tuple, List, Optional

from core.logger import get_logger
from sqlmodel import Session, select, func

from ..model.WebElementModel import WebElement
from ..schemas.WebElementSchema import (
    WebElementCreate, WebElementUpdate, WebElementQuery, ModuleElementList
)

logger = get_logger(__name__)


class WebElementService:
    """Web元素服务类"""
    
    @staticmethod
    def create_element(session: Session, element_data: WebElementCreate) -> WebElement:
        """创建Web元素"""
        try:
            element = WebElement(**element_data.dict())
            session.add(element)
            session.commit()
            session.refresh(element)
            logger.info(f"创建Web元素成功，ID: {element.id}, 名称: {element.name}")
            return element
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web元素失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update_element(session: Session, element_id: int, element_data: WebElementUpdate) -> Optional[WebElement]:
        """更新Web元素"""
        try:
            element = session.get(WebElement, element_id)
            if not element:
                return None
            
            # 更新字段
            update_data = element_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(element, field, value)
            
            element.update_time = datetime.now()
            session.commit()
            session.refresh(element)
            logger.info(f"更新Web元素成功，ID: {element.id}")
            return element
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web元素失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_element(session: Session, element_id: int) -> bool:
        """删除Web元素"""
        try:
            element = session.get(WebElement, element_id)
            if not element:
                return False
            
            session.delete(element)
            session.commit()
            logger.info(f"删除Web元素成功，ID: {element_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web元素失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete_elements(session: Session, element_ids: List[int]) -> int:
        """批量删除Web元素"""
        try:
            count = 0
            for element_id in element_ids:
                if WebElementService.delete_element(session, element_id):
                    count += 1
            logger.info(f"批量删除Web元素成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web元素失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_element_by_id(session: Session, element_id: int) -> Optional[WebElement]:
        """根据ID获取Web元素"""
        try:
            return session.get(WebElement, element_id)
        except Exception as e:
            logger.error(f"查询Web元素失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_elements_by_page(session: Session, query: WebElementQuery) -> Tuple[List[WebElement], int]:
        """分页查询Web元素"""
        try:
            # 构建查询条件
            statement = select(WebElement)
            
            # 添加过滤条件
            if query.project_id:
                statement = statement.where(WebElement.project_id == query.project_id)
            if query.module:
                statement = statement.where(WebElement.module == query.module)
            if query.name:
                statement = statement.where(WebElement.name.contains(query.name))
            if query.locator_type:
                statement = statement.where(WebElement.locator_type == query.locator_type)
            if query.status:
                statement = statement.where(WebElement.status == query.status)
            
            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = statement.offset((query.page - 1) * query.pageSize).limit(query.pageSize)
            statement = statement.order_by(WebElement.module, WebElement.create_time.desc())
            elements = session.exec(statement).all()
            
            return list(elements), total
        except Exception as e:
            logger.error(f"分页查询Web元素失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def get_elements_by_module(session: Session, project_id: int) -> List[ModuleElementList]:
        """按模块获取元素"""
        try:
            # 获取所有模块
            module_statement = select(WebElement.module).where(
                WebElement.project_id == project_id,
                WebElement.status == 'active'
            ).distinct()
            modules = session.exec(module_statement).all()
            
            result = []
            for module in modules:
                if module:  # 过滤空模块名
                    # 获取该模块下的所有元素
                    element_statement = select(WebElement).where(
                        WebElement.project_id == project_id,
                        WebElement.module == module,
                        WebElement.status == 'active'
                    ).order_by(WebElement.create_time.desc())
                    elements = session.exec(element_statement).all()
                    
                    module_list = ModuleElementList(
                        module=module,
                        elements=list(elements)
                    )
                    result.append(module_list)
            
            return result
        except Exception as e:
            logger.error(f"按模块获取Web元素失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def import_elements(session: Session, project_id: int, elements: List[WebElementCreate], overwrite: bool = False) -> Tuple[int, int]:
        """导入Web元素"""
        try:
            success_count = 0
            error_count = 0
            
            for element_data in elements:
                try:
                    # 检查是否已存在同名元素
                    existing_statement = select(WebElement).where(
                        WebElement.project_id == project_id,
                        WebElement.name == element_data.name
                    )
                    existing = session.exec(existing_statement).first()
                    
                    if existing:
                        if overwrite:
                            # 更新现有元素
                            update_data = element_data.dict()
                            for field, value in update_data.items():
                                setattr(existing, field, value)
                            existing.update_time = datetime.now()
                            success_count += 1
                        else:
                            # 跳过已存在的元素
                            continue
                    else:
                        # 创建新元素
                        element = WebElement(project_id=project_id, **element_data.dict())
                        session.add(element)
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"导入元素失败: {element_data.name}, 错误: {e}")
                    error_count += 1
                    continue
            
            session.commit()
            logger.info(f"导入Web元素完成，成功: {success_count}, 失败: {error_count}")
            return success_count, error_count
        except Exception as e:
            session.rollback()
            logger.error(f"批量导入Web元素失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def export_elements(session: Session, project_id: int, element_ids: Optional[List[int]] = None) -> List[WebElement]:
        """导出Web元素"""
        try:
            statement = select(WebElement).where(WebElement.project_id == project_id)
            
            if element_ids:
                statement = statement.where(WebElement.id.in_(element_ids))
            
            elements = session.exec(statement).all()
            return list(elements)
        except Exception as e:
            logger.error(f"导出Web元素失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def parse_import_file(file_content: bytes, file_format: str) -> List[WebElementCreate]:
        """解析导入文件"""
        try:
            elements = []
            
            if file_format == 'json':
                elements = WebElementService._parse_json_file(file_content)
            elif file_format == 'csv':
                elements = WebElementService._parse_csv_file(file_content)
            elif file_format == 'excel':
                elements = WebElementService._parse_excel_file(file_content)
            else:
                raise ValueError(f"不支持的文件格式: {file_format}")
            
            return elements
        except Exception as e:
            logger.error(f"解析导入文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _parse_json_file(file_content: bytes) -> List[WebElementCreate]:
        """解析JSON文件"""
        try:
            import json
            data = json.loads(file_content.decode('utf-8'))
            
            elements = []
            if isinstance(data, dict) and 'elements' in data:
                data = data['elements']
            
            for item in data:
                try:
                    element = WebElementCreate(
                        name=item.get('name', ''),
                        display_name=item.get('display_name', item.get('name', '')),
                        locator_type=item.get('locator_type', 'css'),
                        locator_value=item.get('locator_value', ''),
                        module=item.get('module', 'default'),
                        page_url=item.get('page_url', ''),
                        description=item.get('description', ''),
                        status=item.get('status', 'active')
                    )
                    elements.append(element)
                except Exception as e:
                    logger.warning(f"解析元素项失败: {item}, 错误: {e}")
                    continue
            
            return elements
        except Exception as e:
            logger.error(f"解析JSON文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _parse_csv_file(file_content: bytes) -> List[WebElementCreate]:
        """解析CSV文件"""
        try:
            import csv
            import io
            
            content = file_content.decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(content))
            
            elements = []
            for row in reader:
                try:
                    element = WebElementCreate(
                        name=row.get('name', '').strip(),
                        display_name=row.get('display_name', row.get('name', '')).strip(),
                        locator_type=row.get('locator_type', 'css').strip(),
                        locator_value=row.get('locator_value', '').strip(),
                        module=row.get('module', 'default').strip(),
                        page_url=row.get('page_url', '').strip(),
                        description=row.get('description', '').strip(),
                        status=row.get('status', 'active').strip()
                    )
                    if element.name:  # 只添加有效的元素
                        elements.append(element)
                except Exception as e:
                    logger.warning(f"解析CSV行失败: {row}, 错误: {e}")
                    continue
            
            return elements
        except Exception as e:
            logger.error(f"解析CSV文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _parse_excel_file(file_content: bytes) -> List[WebElementCreate]:
        """解析Excel文件"""
        try:
            import pandas as pd
            import io
            
            df = pd.read_excel(io.BytesIO(file_content))
            
            elements = []
            for _, row in df.iterrows():
                try:
                    element = WebElementCreate(
                        name=str(row.get('name', '')).strip(),
                        display_name=str(row.get('display_name', row.get('name', ''))).strip(),
                        locator_type=str(row.get('locator_type', 'css')).strip(),
                        locator_value=str(row.get('locator_value', '')).strip(),
                        module=str(row.get('module', 'default')).strip(),
                        page_url=str(row.get('page_url', '')).strip(),
                        description=str(row.get('description', '')).strip(),
                        status=str(row.get('status', 'active')).strip()
                    )
                    if element.name:  # 只添加有效的元素
                        elements.append(element)
                except Exception as e:
                    logger.warning(f"解析Excel行失败: {row}, 错误: {e}")
                    continue
            
            return elements
        except ImportError:
            logger.error("需要安装pandas和openpyxl来支持Excel文件解析")
            raise ValueError("Excel解析功能需要安装pandas和openpyxl")
        except Exception as e:
            logger.error(f"解析Excel文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def generate_export_file(elements: List[WebElement], file_format: str) -> bytes:
        """生成导出文件"""
        try:
            if file_format == 'json':
                return WebElementService._generate_json_file(elements)
            elif file_format == 'csv':
                return WebElementService._generate_csv_file(elements)
            elif file_format == 'excel':
                return WebElementService._generate_excel_file(elements)
            else:
                raise ValueError(f"不支持的导出格式: {file_format}")
        except Exception as e:
            logger.error(f"生成导出文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _generate_json_file(elements: List[WebElement]) -> bytes:
        """生成JSON文件"""
        try:
            import json
            
            data = {
                "elements": [element.dict() for element in elements],
                "total": len(elements),
                "export_time": datetime.now().isoformat(),
                "format": "json"
            }
            
            return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        except Exception as e:
            logger.error(f"生成JSON文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _generate_csv_file(elements: List[WebElement]) -> bytes:
        """生成CSV文件"""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            headers = ['name', 'display_name', 'locator_type', 'locator_value', 
                      'module', 'page_url', 'description', 'status']
            writer.writerow(headers)
            
            # 写入数据
            for element in elements:
                row = [
                    element.name,
                    element.display_name,
                    element.locator_type,
                    element.locator_value,
                    element.module,
                    element.page_url,
                    element.description,
                    element.status
                ]
                writer.writerow(row)
            
            return output.getvalue().encode('utf-8-sig')
        except Exception as e:
            logger.error(f"生成CSV文件失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def _generate_excel_file(elements: List[WebElement]) -> bytes:
        """生成Excel文件"""
        try:
            import pandas as pd
            import io
            
            data = []
            for element in elements:
                data.append({
                    'name': element.name,
                    'display_name': element.display_name,
                    'locator_type': element.locator_type,
                    'locator_value': element.locator_value,
                    'module': element.module,
                    'page_url': element.page_url,
                    'description': element.description,
                    'status': element.status
                })
            
            df = pd.DataFrame(data)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Elements')
                
                # 获取工作表并设置列宽
                worksheet = writer.sheets['Elements']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return output.getvalue()
        except ImportError:
            logger.error("需要安装pandas和openpyxl来支持Excel文件生成")
            raise ValueError("Excel生成功能需要安装pandas和openpyxl")
        except Exception as e:
            logger.error(f"生成Excel文件失败: {e}", exc_info=True)
            raise e
