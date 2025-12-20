"""
API测试计划Service
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from core.logger import get_logger
from core.time_utils import TimeFormatter

from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..model.ApiPlanRobotModel import ApiPlanRobot

logger = get_logger(__name__)


class ApiCollectionInfoService:
    """API测试计划服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None, 
                      plan_name: Optional[str] = None) -> tuple[List[Dict], int]:
        """分页查询测试计划"""
        statement = select(ApiCollectionInfo)
        
        if project_id:
            statement = statement.where(ApiCollectionInfo.project_id == project_id)
        if plan_name:
            statement = statement.where(ApiCollectionInfo.plan_name.like(f"%{plan_name}%"))
        
        offset = (page - 1) * page_size
        datas = self.session.exec(
            statement.order_by(ApiCollectionInfo.create_time.desc())
            .limit(page_size).offset(offset)
        ).all()
        total = len(self.session.exec(statement).all())
        
        result_list = []
        for data in datas:
            case_count_stmt = select(ApiCollectionDetail).where(
                ApiCollectionDetail.collection_info_id == data.id
            )
            case_count = len(self.session.exec(case_count_stmt).all())
            
            result_list.append({
                "id": data.id,
                "project_id": data.project_id,
                "plan_name": data.plan_name,
                "plan_desc": data.plan_desc,
                "case_count": case_count,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "modify_time": TimeFormatter.format_datetime(data.modify_time)
            })
        
        return result_list, total
    
    def get_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询测试计划（含关联用例）"""
        plan = self.session.get(ApiCollectionInfo, plan_id)
        if not plan:
            return None
        
        case_stmt = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == plan_id
        ).order_by(ApiCollectionDetail.run_order)
        plan_cases = self.session.exec(case_stmt).all()
        
        cases = []
        for pc in plan_cases:
            case_info = self.session.get(ApiInfoCase, pc.case_info_id)
            cases.append({
                "id": pc.id,
                "plan_id": pc.collection_info_id,
                "case_info_id": pc.case_info_id,
                "case_name": case_info.case_name if case_info else "",
                "case_desc": case_info.case_desc if case_info else "",
                "run_order": pc.run_order,
                "ddt_data": pc.ddt_data,
                "create_time": TimeFormatter.format_datetime(pc.create_time)
            })
        
        return {
            "id": plan.id,
            "project_id": plan.project_id,
            "plan_name": plan.plan_name,
            "plan_desc": plan.plan_desc,
            "create_time": TimeFormatter.format_datetime(plan.create_time),
            "modify_time": TimeFormatter.format_datetime(plan.modify_time),
            "cases": cases
        }
    
    def create(self, project_id: int, plan_name: str, plan_desc: Optional[str] = None) -> ApiCollectionInfo:
        """新增测试计划"""
        plan = ApiCollectionInfo(
            project_id=project_id,
            plan_name=plan_name,
            plan_desc=plan_desc,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan
    
    def update(self, plan_id: int, update_data: Dict[str, Any]) -> Optional[ApiCollectionInfo]:
        """更新测试计划"""
        plan = self.session.get(ApiCollectionInfo, plan_id)
        if not plan:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(plan, key, value)
        
        plan.modify_time = datetime.now()
        self.session.commit()
        self.session.refresh(plan)
        return plan
    
    def delete(self, plan_id: int) -> bool:
        """删除测试计划"""
        plan = self.session.get(ApiCollectionInfo, plan_id)
        if not plan:
            return False
        
        self.session.delete(plan)
        self.session.commit()
        return True
    
    def add_case(self, plan_id: int, case_info_id: int, run_order: int, 
                 ddt_data: Optional[Dict] = None) -> Optional[ApiCollectionDetail]:
        """添加用例到测试计划"""
        check_stmt = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == plan_id,
            ApiCollectionDetail.case_info_id == case_info_id
        )
        existing = self.session.exec(check_stmt).first()
        if existing:
            return None
        
        plan_case = ApiCollectionDetail(
            collection_info_id=plan_id,
            case_info_id=case_info_id,
            run_order=run_order,
            ddt_data=json.dumps(ddt_data, ensure_ascii=False) if ddt_data else None,
            create_time=datetime.now()
        )
        self.session.add(plan_case)
        self.session.commit()
        self.session.refresh(plan_case)
        return plan_case
    
    def batch_add_cases(self, plan_id: int, case_ids: List[int]) -> int:
        """批量添加用例到测试计划，自动提取数据驱动配置"""
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_ddt_from_case(case_id: int) -> Optional[str]:
            variables = {}
            
            def extract_all_fields(data_dict):
                if isinstance(data_dict, dict):
                    for key, value in data_dict.items():
                        if key in skip_fields:
                            continue
                        if isinstance(value, dict):
                            extract_all_fields(value)
                        elif isinstance(value, list):
                            for item in value:
                                extract_all_fields(item)
                        elif isinstance(value, (str, int, float, bool)):
                            variables[key] = value if isinstance(value, str) else str(value)
                elif isinstance(data_dict, list):
                    for item in data_dict:
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
        
        added_count = 0
        for idx, case_id in enumerate(case_ids):
            check_stmt = select(ApiCollectionDetail).where(
                ApiCollectionDetail.collection_info_id == plan_id,
                ApiCollectionDetail.case_info_id == case_id
            )
            existing = self.session.exec(check_stmt).first()
            if not existing:
                ddt_data = extract_ddt_from_case(case_id)
                plan_case = ApiCollectionDetail(
                    collection_info_id=plan_id,
                    case_info_id=case_id,
                    run_order=idx + 1,
                    ddt_data=ddt_data,
                    create_time=datetime.now()
                )
                self.session.add(plan_case)
                added_count += 1
        
        self.session.commit()
        return added_count
    
    def remove_case(self, plan_case_id: int) -> bool:
        """从测试计划移除用例"""
        plan_case = self.session.get(ApiCollectionDetail, plan_case_id)
        if not plan_case:
            return False
        
        self.session.delete(plan_case)
        self.session.commit()
        return True
    
    def update_ddt_data(self, plan_case_id: int, ddt_data: Optional[Dict]) -> Optional[ApiCollectionDetail]:
        """更新测试计划的数据驱动信息"""
        plan_case = self.session.get(ApiCollectionDetail, plan_case_id)
        if not plan_case:
            return None
        
        plan_case.ddt_data = json.dumps(ddt_data, ensure_ascii=False) if ddt_data else None
        self.session.commit()
        self.session.refresh(plan_case)
        return plan_case
    
    def copy_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """复制测试计划及其关联的用例"""
        original_plan = self.session.get(ApiCollectionInfo, plan_id)
        if not original_plan:
            return None
        
        new_plan = ApiCollectionInfo(
            project_id=original_plan.project_id,
            plan_name=f"{original_plan.plan_name}_副本",
            plan_desc=original_plan.plan_desc,
            plugin_code=original_plan.plugin_code,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        self.session.add(new_plan)
        self.session.flush()
        
        statement = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == plan_id
        ).order_by(ApiCollectionDetail.run_order)
        original_details = self.session.exec(statement).all()
        
        copied_count = 0
        for detail in original_details:
            new_detail = ApiCollectionDetail(
                collection_info_id=new_plan.id,
                case_info_id=detail.case_info_id,
                ddt_data=detail.ddt_data,
                run_order=detail.run_order,
                create_time=datetime.now()
            )
            self.session.add(new_detail)
            copied_count += 1
        
        self.session.commit()
        
        return {
            "new_plan_id": new_plan.id,
            "copied_cases": copied_count
        }
    
    def get_jenkins_config(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """获取测试计划的Jenkins CI/CD集成配置信息"""
        plan = self.session.get(ApiCollectionInfo, plan_id)
        if not plan:
            return None
        
        statement = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == plan_id
        )
        details = self.session.exec(statement).all()
        
        jenkins_config = {
            "plan_id": plan.id,
            "plan_name": plan.plan_name,
            "project_id": plan.project_id,
            "case_count": len(details),
            "api_endpoint": f"/api/ApiInfoCase/executeCase",
            "request_method": "POST",
            "request_body": {
                "plan_id": plan.id,
                "executor_code": "api-engine"
            },
            "curl_command": f'curl -X POST "{{BASE_URL}}/api/ApiInfoCase/executeCase" -H "Content-Type: application/json" -H "Authorization: Bearer {{TOKEN}}" -d \'{{"plan_id": {plan.id}}}\'',
            "pipeline_script": f'''pipeline {{
    agent any
    environment {{
        BASE_URL = 'http://your-server:5000'
        TOKEN = credentials('api-test-token')
    }}
    stages {{
        stage('Execute Test Plan') {{
            steps {{
                script {{
                    def response = httpRequest(
                        url: "${{BASE_URL}}/api/ApiInfoCase/executeCase",
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        customHeaders: [[name: 'Authorization', value: "Bearer ${{TOKEN}}"]],
                        requestBody: '{{"plan_id": {plan.id}}}'
                    )
                    echo "Response: ${{response.content}}"
                }}
            }}
        }}
    }}
}}'''
        }
        
        return jenkins_config
    
    def get_robots(self, plan_id: int) -> List[Dict[str, Any]]:
        """获取测试计划关联的所有机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        statement = select(ApiPlanRobot).where(ApiPlanRobot.plan_id == plan_id)
        plan_robots = self.session.exec(statement).all()
        
        result = []
        for pr in plan_robots:
            robot = self.session.get(RobotConfig, pr.robot_id)
            if robot:
                result.append({
                    "id": pr.id,
                    "plan_id": pr.plan_id,
                    "robot_id": pr.robot_id,
                    "robot_name": robot.robot_name,
                    "robot_type": robot.robot_type,
                    "is_enabled": pr.is_enabled,
                    "notify_on_success": pr.notify_on_success,
                    "notify_on_failure": pr.notify_on_failure,
                    "create_time": TimeFormatter.format_datetime(pr.create_time)
                })
        
        return result
    
    def add_robot(self, plan_id: int, robot_id: int, is_enabled: bool = True,
                  notify_on_success: bool = True, notify_on_failure: bool = True) -> Optional[ApiPlanRobot]:
        """为测试计划添加机器人通知配置"""
        check_stmt = select(ApiPlanRobot).where(
            ApiPlanRobot.plan_id == plan_id,
            ApiPlanRobot.robot_id == robot_id
        )
        existing = self.session.exec(check_stmt).first()
        if existing:
            return None
        
        plan_robot = ApiPlanRobot(
            plan_id=plan_id,
            robot_id=robot_id,
            is_enabled=is_enabled,
            notify_on_success=notify_on_success,
            notify_on_failure=notify_on_failure,
            create_time=datetime.now()
        )
        self.session.add(plan_robot)
        self.session.commit()
        self.session.refresh(plan_robot)
        return plan_robot
    
    def update_robot(self, robot_config_id: int, update_data: Dict[str, Any]) -> Optional[ApiPlanRobot]:
        """更新测试计划机器人通知配置"""
        plan_robot = self.session.get(ApiPlanRobot, robot_config_id)
        if not plan_robot:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(plan_robot, key, value)
        
        self.session.commit()
        self.session.refresh(plan_robot)
        return plan_robot
    
    def remove_robot(self, robot_config_id: int) -> bool:
        """移除测试计划的机器人关联"""
        plan_robot = self.session.get(ApiPlanRobot, robot_config_id)
        if not plan_robot:
            return False
        
        self.session.delete(plan_robot)
        self.session.commit()
        return True
