# Copyright (c) 2025 左岚. All rights reserved.
"""
多智能体协作的AI服务层
实现基于AutoGen框架的智能测试用例生成
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from app.core.logger import get_logger
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class AgentRole(str, Enum):
    """智能体角色枚举"""
    REQUIREMENTS_ANALYST = "requirements_analyst"
    TEST_CASE_DESIGNER = "test_case_designer"
    TEST_REVIEWER = "test_reviewer"
    TEST_ORGANIZER = "test_organizer"


class GenerationStatus(str, Enum):
    """生成状态枚举"""
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    DESIGNING = "designing"
    REVIEWING = "reviewing"
    ORGANIZING = "organizing"
    COMPLETED = "completed"
    FAILED = "failed"


class MultiAgentTestCaseGenerator:
    """多智能体测试用例生成器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.generation_id = None
        self.status = GenerationStatus.INITIALIZING
        self.agents = {}
        self.conversation_history = []
        self.generated_cases = []
        self.warnings = []
        self.errors = []
        
    async def generate_test_cases(self, requirements_document: str, 
                                generation_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成测试用例的主要方法
        
        Args:
            requirements_document: 需求文档内容
            generation_config: 生成配置
            
        Returns:
            生成结果字典
        """
        try:
            self.generation_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = datetime.now()
            
            logger.info(f"Starting test case generation {self.generation_id}")
            
            # 1. 初始化智能体
            await self._initialize_agents()
            
            # 2. 需求分析阶段
            test_points = await self._analyze_requirements(requirements_document)
            
            # 3. 测试用例设计阶段
            test_cases = await self._design_test_cases(requirements_document, test_points)
            
            # 4. 测试用例审核阶段
            reviewed_cases = await self._review_test_cases(requirements_document, test_cases)
            
            # 5. 编程式整理阶段
            final_cases = await self._organize_test_cases(reviewed_cases)
            
            # 6. 完成生成
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            self.status = GenerationStatus.COMPLETED
            self.generated_cases = final_cases
            
            result = {
                "generation_id": self.generation_id,
                "status": self.status.value,
                "total_generated": len(final_cases),
                "generated_cases": final_cases,
                "generation_time": generation_time,
                "agent_used": "multi_agent_system",
                "warnings": self.warnings,
                "errors": self.errors,
                "conversation_history": self.conversation_history
            }
            
            logger.info(f"Test case generation {self.generation_id} completed successfully")
            return result
            
        except Exception as e:
            self.status = GenerationStatus.FAILED
            self.errors.append(str(e))
            logger.error(f"Test case generation {self.generation_id} failed: {str(e)}")
            raise BusinessException(f"测试用例生成失败: {str(e)}")
    
    async def _initialize_agents(self):
        """初始化智能体"""
        self.status = GenerationStatus.INITIALIZING
        
        # 需求分析师
        self.agents[AgentRole.REQUIREMENTS_ANALYST] = {
            "role": "需求分析师",
            "prompt": self._get_requirements_analyst_prompt(),
            "capabilities": ["需求理解", "测试点提取", "场景分析"]
        }
        
        # 测试用例设计师
        self.agents[AgentRole.TEST_CASE_DESIGNER] = {
            "role": "测试用例设计师",
            "prompt": self._get_test_case_designer_prompt(),
            "capabilities": ["用例设计", "步骤编写", "结果定义"]
        }
        
        # 测试用例审核员
        self.agents[AgentRole.TEST_REVIEWER] = {
            "role": "测试用例审核员", 
            "prompt": self._get_test_reviewer_prompt(),
            "capabilities": ["质量审核", "覆盖度检查", "标准验证"]
        }
        
        # 编程式整理器
        self.agents[AgentRole.TEST_ORGANIZER] = {
            "role": "编程式整理器",
            "prompt": self._get_test_organizer_prompt(),
            "capabilities": ["去重处理", "格式标准化", "结构优化"]
        }
        
        logger.info("Agents initialized successfully")
    
    async def _analyze_requirements(self, requirements_document: str) -> List[Dict[str, Any]]:
        """需求分析阶段"""
        self.status = GenerationStatus.ANALYZING
        
        analyst = self.agents[AgentRole.REQUIREMENTS_ANALYST]
        
        # 模拟需求分析师的工作
        analysis_prompt = f"""
        {analyst['prompt']}
        
        需求文档内容：
        {requirements_document}
        
        请分析需求文档并提取测试点：
        """
        
        # 这里应该调用实际的AI模型API
        # 为了演示，我们生成模拟的测试点
        test_points = self._simulate_requirements_analysis(requirements_document)
        
        self.conversation_history.append({
            "agent": AgentRole.REQUIREMENTS_ANALYST.value,
            "action": "需求分析",
            "input": requirements_document[:200] + "...",
            "output": f"提取了 {len(test_points)} 个测试点",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Requirements analysis completed, found {len(test_points)} test points")
        return test_points
    
    async def _design_test_cases(self, requirements_document: str, 
                               test_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """测试用例设计阶段"""
        self.status = GenerationStatus.DESIGNING
        
        designer = self.agents[AgentRole.TEST_CASE_DESIGNER]
        
        # 模拟测试用例设计师的工作
        design_prompt = f"""
        {designer['prompt']}
        
        需求文档：
        {requirements_document}
        
        测试点：
        {json.dumps(test_points, ensure_ascii=False, indent=2)}
        
        请基于测试点设计具体的测试用例：
        """
        
        # 模拟测试用例设计
        test_cases = self._simulate_test_case_design(requirements_document, test_points)
        
        self.conversation_history.append({
            "agent": AgentRole.TEST_CASE_DESIGNER.value,
            "action": "测试用例设计",
            "input": f"{len(test_points)} 个测试点",
            "output": f"设计了 {len(test_cases)} 个测试用例",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Test case design completed, designed {len(test_cases)} test cases")
        return test_cases
    
    async def _review_test_cases(self, requirements_document: str,
                               test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """测试用例审核阶段"""
        self.status = GenerationStatus.REVIEWING
        
        reviewer = self.agents[AgentRole.TEST_REVIEWER]
        
        # 模拟审核过程
        reviewed_cases = []
        review_issues = []
        
        for test_case in test_cases:
            # 模拟审核逻辑
            if self._validate_test_case(test_case):
                reviewed_cases.append(test_case)
            else:
                review_issues.append(f"用例 {test_case.get('ID', 'unknown')} 存在问题")
        
        if review_issues:
            self.warnings.extend(review_issues)
        
        self.conversation_history.append({
            "agent": AgentRole.TEST_REVIEWER.value,
            "action": "测试用例审核",
            "input": f"{len(test_cases)} 个测试用例",
            "output": f"通过审核 {len(reviewed_cases)} 个，发现 {len(review_issues)} 个问题",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Test case review completed, {len(reviewed_cases)} cases passed review")
        return reviewed_cases
    
    async def _organize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """编程式整理阶段"""
        self.status = GenerationStatus.ORGANIZING
        
        # 1. 去重处理
        unique_cases = self._deduplicate_test_cases(test_cases)
        
        # 2. 格式标准化
        standardized_cases = self._standardize_test_cases(unique_cases)
        
        # 3. 排序优化
        organized_cases = self._sort_test_cases(standardized_cases)
        
        self.conversation_history.append({
            "agent": AgentRole.TEST_ORGANIZER.value,
            "action": "编程式整理",
            "input": f"{len(test_cases)} 个测试用例",
            "output": f"整理后 {len(organized_cases)} 个唯一测试用例",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Test case organization completed, {len(organized_cases)} final cases")
        return organized_cases
    
    def _simulate_requirements_analysis(self, requirements_document: str) -> List[Dict[str, Any]]:
        """模拟需求分析结果"""
        # 这里应该是实际的AI分析逻辑
        return [
            {
                "module": "用户登录",
                "test_points": [
                    {"id": 1, "name": "正常登录验证", "type": "正常流程"},
                    {"id": 2, "name": "错误密码验证", "type": "异常场景"},
                    {"id": 3, "name": "空用户名验证", "type": "边界值"}
                ]
            },
            {
                "module": "数据管理",
                "test_points": [
                    {"id": 4, "name": "数据新增功能", "type": "正常流程"},
                    {"id": 5, "name": "数据查询功能", "type": "正常流程"},
                    {"id": 6, "name": "数据删除权限", "type": "权限验证"}
                ]
            }
        ]
    
    def _simulate_test_case_design(self, requirements_document: str, 
                                 test_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """模拟测试用例设计结果"""
        test_cases = []
        case_id = 1
        
        for module in test_points:
            module_name = module.get("module", "未知模块")
            for point in module.get("test_points", []):
                test_case = {
                    "ID": f"TC_{case_id:03d}",
                    "用例名称": point.get("name", ""),
                    "所属模块": module_name,
                    "前置条件": "系统正常运行，用户已准备测试数据",
                    "备注": f"基于需求文档自动生成的{point.get('type', '')}测试用例",
                    "步骤描述": f"1. 执行{point.get('name', '')}相关操作\n2. 验证操作结果\n3. 检查系统状态",
                    "预期结果": f"1. 操作成功执行\n2. 结果符合预期\n3. 系统状态正常",
                    "编辑模式": "创建",
                    "标签": "功能测试",
                    "用例等级": "P2",
                    "用例状态": "待执行"
                }
                test_cases.append(test_case)
                case_id += 1
        
        return test_cases
    
    def _validate_test_case(self, test_case: Dict[str, Any]) -> bool:
        """验证测试用例质量"""
        required_fields = ["用例名称", "步骤描述", "预期结果"]
        
        for field in required_fields:
            if not test_case.get(field):
                return False
        
        # 检查步骤描述长度
        if len(test_case.get("步骤描述", "")) < 10:
            return False
        
        return True
    
    def _deduplicate_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重处理"""
        unique_cases = []
        seen_names = set()
        
        for case in test_cases:
            case_name = case.get("用例名称", "")
            if case_name not in seen_names:
                unique_cases.append(case)
                seen_names.add(case_name)
        
        return unique_cases
    
    def _standardize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式标准化"""
        standardized = []
        
        for case in test_cases:
            # 确保所有必需字段存在
            standardized_case = {
                "ID": case.get("ID", ""),
                "用例名称": case.get("用例名称", ""),
                "所属模块": case.get("所属模块", ""),
                "前置条件": case.get("前置条件", ""),
                "备注": case.get("备注", ""),
                "步骤描述": case.get("步骤描述", ""),
                "预期结果": case.get("预期结果", ""),
                "编辑模式": case.get("编辑模式", "创建"),
                "标签": case.get("标签", "功能测试"),
                "用例等级": case.get("用例等级", "P3"),
                "用例状态": case.get("用例状态", "待执行")
            }
            standardized.append(standardized_case)
        
        return standardized
    
    def _sort_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序优化"""
        # 按模块和用例等级排序
        priority_order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5}
        
        return sorted(test_cases, key=lambda x: (
            x.get("所属模块", ""),
            priority_order.get(x.get("用例等级", "P3"), 3)
        ))
    
    def _get_requirements_analyst_prompt(self) -> str:
        """获取需求分析师提示词"""
        return """
        你是一位资深的需求分析师，负责深度分析需求文档并提取全面的测试点清单。
        
        工作职责：
        1. 深度阅读需求文档，理解业务功能、操作流程、界面交互
        2. 识别功能模块，按业务逻辑进行合理划分
        3. 提取测试点，为每个功能模块识别关键测试点
        4. 分析测试场景，考虑正常、异常、边界等各种情况
        
        输出要求：
        - 按功能模块组织测试点
        - 明确区分正常流程、异常场景、边界值测试
        - 测试点描述清晰、具体、可操作
        """
    
    def _get_test_case_designer_prompt(self) -> str:
        """获取测试用例设计师提示词"""
        return """
        你是一位专业的测试用例设计师，负责基于需求文档和测试点设计具体可执行的测试用例。
        
        工作流程：
        1. 仔细阅读原始需求文档，深入理解功能细节
        2. 逐一列出需求分析师的所有测试点，确保无遗漏
        3. 按照测试点顺序逐一编写测试用例，一对一对应
        4. 基于需求文档编写具体测试步骤，确保可追溯性
        
        设计原则：
        - 每个测试点对应一个测试用例
        - 测试步骤具体可操作，包含详细的操作描述
        - 预期结果明确具体，能够清晰判断通过/失败
        - 前置条件完整，测试数据准备充分
        """
    
    def _get_test_reviewer_prompt(self) -> str:
        """获取测试用例审核员提示词"""
        return """
        你是一位资深的测试用例审核员，负责审核和优化测试用例质量。
        
        审核重点：
        1. 需求文档依据性检查 - 确保每个测试步骤都能在需求文档中找到对应功能描述
        2. 测试点覆盖度检查 - 确保所有测试点都有对应的测试用例
        3. 测试质量标准审查 - 检查步骤具体性、结果可验证性等
        
        审核决策：
        - 审核通过：测试用例完全基于需求文档，覆盖所有测试点
        - 需要重新设计：存在脱离需求、遗漏测试点等问题
        """
    
    def _get_test_organizer_prompt(self) -> str:
        """获取编程式整理器提示词"""
        return """
        你是编程式整理器，使用确定性算法进行测试用例的去重和规范化整理。
        
        整理流程：
        1. 智能去重 - 识别并合并重复的测试用例
        2. 格式标准化 - 统一测试用例的字段格式和内容结构
        3. 排序优化 - 按模块和优先级进行合理排序
        4. 质量检查 - 确保最终结果的完整性和一致性
        
        算法特点：
        - 使用编程逻辑确保处理的准确性
        - 保留更完整、更详细的测试用例版本
        - 维护测试用例间的逻辑关系
        """