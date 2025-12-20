"""
API测试集合详情Service
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from core.logger import get_logger

from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep

logger = get_logger(__name__)


class ApiCollectionDetailService:
    """API测试集合详情服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_collection_id(self, collection_info_id: int) -> List[ApiCollectionDetail]:
        """根据集合ID查询所有关联用例"""
        statement = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == collection_info_id
        ).order_by(ApiCollectionDetail.run_order)
        return self.session.exec(statement).all()
    
    def get_by_id(self, detail_id: int) -> Optional[ApiCollectionDetail]:
        """根据ID查询集合详情"""
        return self.session.get(ApiCollectionDetail, detail_id)
    
    def create(self, collection_info_id: int, case_info_id: int, run_order: int, 
               ddt_data: Optional[Dict] = None) -> ApiCollectionDetail:
        """新增集合详情"""
        ddt_data_str = json.dumps(ddt_data, ensure_ascii=False) if ddt_data else None
        detail = ApiCollectionDetail(
            collection_info_id=collection_info_id,
            case_info_id=case_info_id,
            run_order=run_order,
            ddt_data=ddt_data_str,
            create_time=datetime.now()
        )
        self.session.add(detail)
        self.session.commit()
        self.session.refresh(detail)
        return detail
    
    def update(self, detail_id: int, update_data: Dict[str, Any]) -> Optional[ApiCollectionDetail]:
        """更新集合详情"""
        detail = self.get_by_id(detail_id)
        if not detail:
            return None
        
        if 'ddt_data' in update_data and update_data['ddt_data']:
            update_data['ddt_data'] = json.dumps(update_data['ddt_data'], ensure_ascii=False)
        
        for key, value in update_data.items():
            if value is not None:
                setattr(detail, key, value)
        
        self.session.commit()
        self.session.refresh(detail)
        return detail
    
    def delete(self, detail_id: int) -> bool:
        """删除集合详情"""
        detail = self.get_by_id(detail_id)
        if not detail:
            return False
        
        self.session.delete(detail)
        self.session.commit()
        return True
    
    def batch_add_cases(self, collection_info_id: int, case_ids: List[int]) -> int:
        """批量添加用例到集合，自动提取数据驱动配置"""
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_ddt_from_case(case_id: int) -> Optional[str]:
            """从用例步骤中提取数据驱动配置"""
            variables = {}
            
            def extract_all_fields(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key in skip_fields:
                            continue
                        if isinstance(value, dict):
                            extract_all_fields(value)
                        elif isinstance(value, list):
                            extract_all_fields(value)
                        elif isinstance(value, (str, int, float, bool)):
                            variables[key] = value if isinstance(value, str) else str(value)
                elif isinstance(data, list):
                    for item in data:
                        extract_all_fields(item)
            
            steps = self.session.exec(
                select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_id)
            ).all()
            
            for step in steps:
                if step.step_data:
                    try:
                        step_dict = json.loads(step.step_data)
                        extract_all_fields(step_dict)
                    except:
                        pass
            
            case_info = self.session.get(ApiInfoCase, case_id)
            case_name = case_info.case_name if case_info else f"用例{case_id}"
            
            if variables:
                template = [{"desc": f"{case_name}_数据1", **variables}]
                return json.dumps(template, ensure_ascii=False)
            return None
        
        statement = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == collection_info_id
        )
        existing = self.session.exec(statement).all()
        max_order = max([d.run_order for d in existing], default=0)
        
        added_count = 0
        for idx, case_id in enumerate(case_ids, 1):
            ddt_data = extract_ddt_from_case(case_id)
            detail = ApiCollectionDetail(
                collection_info_id=collection_info_id,
                case_info_id=case_id,
                run_order=max_order + idx,
                ddt_data=ddt_data,
                create_time=datetime.now()
            )
            self.session.add(detail)
            added_count += 1
        
        self.session.commit()
        return added_count
    
    def batch_update_order(self, details: List[Dict[str, Any]]) -> bool:
        """批量更新执行顺序"""
        for detail_data in details:
            detail_id = detail_data.get('id')
            run_order = detail_data.get('run_order')
            if detail_id and run_order is not None:
                detail = self.get_by_id(detail_id)
                if detail:
                    detail.run_order = run_order
        
        self.session.commit()
        return True
    
    def get_ddt_template(self, case_info_id: int) -> Dict[str, Any]:
        """根据用例步骤数据提取变量，生成数据驱动模板"""
        import re
        
        case_info = self.session.get(ApiInfoCase, case_info_id)
        if not case_info:
            raise ValueError("用例不存在")
        
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_info_id
        ).order_by(ApiInfoCaseStep.run_order)
        steps = self.session.exec(statement).all()
        
        variables = {}
        variable_pattern = re.compile(r'\$\{?(\w+)\}?')
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_all_fields(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in skip_fields:
                        continue
                    if isinstance(value, dict):
                        extract_all_fields(value)
                    elif isinstance(value, list):
                        extract_all_fields(value)
                    elif isinstance(value, (str, int, float, bool)):
                        variables[key] = value if isinstance(value, str) else str(value)
            elif isinstance(data, list):
                for item in data:
                    extract_all_fields(item)
        
        for step in steps:
            if step.step_data:
                try:
                    step_dict = json.loads(step.step_data)
                    extract_all_fields(step_dict)
                except Exception as parse_err:
                    logger.warning(f"解析步骤数据失败: {parse_err}")
                
                matches = variable_pattern.findall(step.step_data)
                for var in matches:
                    if var not in variables:
                        variables[var] = f"<{var}的值>"
        
        template_item = {"desc": f"{case_info.case_name}_数据1"}
        for var, value in variables.items():
            template_item[var] = value
        
        if len(template_item) == 1:
            template_item["变量名1"] = "值1"
            template_item["变量名2"] = "值2"
        
        template = [template_item]
        
        return {
            "template": template,
            "variables": list(variables.keys()),
            "case_name": case_info.case_name
        }
