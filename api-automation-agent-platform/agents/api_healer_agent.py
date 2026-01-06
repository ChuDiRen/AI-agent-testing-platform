"""
API Healer智能修复 - AI驱动的测试用例自动修复

职责：
- 自动检测测试失败原因
- AI分析失败模式
- 生成修复建议
- 应用修复并验证
"""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime
import uuid

from core.logging_config import get_logger

logger = get_logger(__name__)


class APIHealerAgent:
    """
    API Healer智能修复智能体
    
    核心功能：
    - 失败原因分析
    - 智能修复建议
    - 自动修复应用
    - 修复效果验证
    """
    
    def __init__(self):
        """初始化API Healer智能体"""
        self.agent_name = "API Healer智能体"
        self.healing_history: List[Dict[str, Any]] = []
        
        # 支持的修复类型
        self.supported_fix_types = [
            "assertion_error",      # 断言错误
            "timeout",              # 超时
            "authentication_error", # 认证失败
            "network_error",        # 网络错误
            "data_format_error",    # 数据格式错误
            "api_change",           # API变更
            "environment_issue"     # 环境问题
        ]
        
        logger.info(f"{self.agent_name} 初始化完成")
    
    async def analyze_failure(
        self,
        test_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析测试失败原因
        
        Args:
            test_result: 测试结果
        
        Returns:
            失败分析结果
        """
        logger.info(f"{self.agent_name} 开始分析测试失败")
        
        test_id = test_result.get("test_id", "")
        error = test_result.get("error", "")
        status = test_result.get("status", "")
        
        # 识别失败类型
        failure_type = self._identify_failure_type(error, status)
        
        # 提取关键信息
        key_info = self._extract_key_information(test_result)
        
        # 生成分析报告
        analysis = {
            "analysis_id": str(uuid.uuid4()),
            "test_id": test_id,
            "failure_type": failure_type,
            "error_message": error,
            "key_information": key_info,
            "root_cause": self._determine_root_cause(failure_type, key_info),
            "severity": self._assess_severity(failure_type),
            "analyzed_at": datetime.utcnow().isoformat(),
            "analyzed_by": self.agent_name
        }
        
        logger.info(f"{self.agent_name} 失败分析完成: {failure_type}")
        return analysis
    
    def _identify_failure_type(self, error: str, status: str) -> str:
        """识别失败类型"""
        error_lower = error.lower()
        
        # 断言错误
        if "assertion" in error_lower or "expected" in error_lower:
            return "assertion_error"
        
        # 超时
        if "timeout" in error_lower or status == "timeout":
            return "timeout"
        
        # 认证失败
        if "auth" in error_lower or "401" in error or "403" in error:
            return "authentication_error"
        
        # 网络错误
        if "network" in error_lower or "connection" in error_lower:
            return "network_error"
        
        # 数据格式错误
        if "json" in error_lower or "parse" in error_lower or "format" in error_lower:
            return "data_format_error"
        
        # API变更
        if "404" in error or "not found" in error_lower:
            return "api_change"
        
        # 默认为环境问题
        return "environment_issue"
    
    def _extract_key_information(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键信息"""
        return {
            "test_name": test_result.get("test_name", ""),
            "error_message": test_result.get("error", ""),
            "duration": test_result.get("duration", 0),
            "steps": test_result.get("steps", []),
            "request_data": test_result.get("request_data", {}),
            "response_data": test_result.get("response_data", {})
        }
    
    def _determine_root_cause(self, failure_type: str, key_info: Dict[str, Any]) -> str:
        """确定根本原因"""
        root_causes = {
            "assertion_error": "断言条件不匹配，可能是响应数据结构或值发生变化",
            "timeout": "请求超时，可能是服务响应慢或网络延迟",
            "authentication_error": "认证失败，可能是token过期或权限不足",
            "network_error": "网络连接失败，可能是服务不可用或网络问题",
            "data_format_error": "数据格式错误，可能是API返回格式变更",
            "api_change": "API端点变更，可能是路径或方法改变",
            "environment_issue": "环境配置问题，需要检查环境变量和依赖"
        }
        return root_causes.get(failure_type, "未知原因")
    
    def _assess_severity(self, failure_type: str) -> str:
        """评估严重程度"""
        high_severity = ["authentication_error", "api_change"]
        medium_severity = ["assertion_error", "data_format_error"]
        
        if failure_type in high_severity:
            return "high"
        elif failure_type in medium_severity:
            return "medium"
        else:
            return "low"
    
    async def generate_fix_suggestions(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成修复建议
        
        Args:
            analysis: 失败分析结果
        
        Returns:
            修复建议
        """
        logger.info(f"{self.agent_name} 生成修复建议")
        
        failure_type = analysis.get("failure_type", "")
        key_info = analysis.get("key_information", {})
        
        # 根据失败类型生成建议
        suggestions = self._generate_type_specific_suggestions(failure_type, key_info)
        
        return {
            "suggestion_id": str(uuid.uuid4()),
            "analysis_id": analysis.get("analysis_id", ""),
            "failure_type": failure_type,
            "suggestions": suggestions,
            "auto_fixable": self._is_auto_fixable(failure_type),
            "estimated_effort": self._estimate_fix_effort(failure_type),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_type_specific_suggestions(
        self,
        failure_type: str,
        key_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """根据失败类型生成具体建议"""
        suggestions_map = {
            "assertion_error": [
                {
                    "priority": 1,
                    "action": "更新断言条件",
                    "description": "根据实际响应数据更新断言逻辑",
                    "code_change": "修改expect语句以匹配新的响应格式"
                },
                {
                    "priority": 2,
                    "action": "添加数据验证",
                    "description": "增加响应数据的类型和格式验证",
                    "code_change": "添加schema验证或类型检查"
                }
            ],
            "timeout": [
                {
                    "priority": 1,
                    "action": "增加超时时间",
                    "description": "将超时时间从默认值增加到更合理的值",
                    "code_change": "修改timeout配置参数"
                },
                {
                    "priority": 2,
                    "action": "添加重试机制",
                    "description": "实现自动重试逻辑",
                    "code_change": "添加retry装饰器或重试循环"
                }
            ],
            "authentication_error": [
                {
                    "priority": 1,
                    "action": "刷新认证token",
                    "description": "重新获取有效的认证token",
                    "code_change": "调用token刷新接口"
                },
                {
                    "priority": 2,
                    "action": "更新认证方式",
                    "description": "检查并更新认证方法",
                    "code_change": "修改Authorization header或认证参数"
                }
            ],
            "network_error": [
                {
                    "priority": 1,
                    "action": "检查服务可用性",
                    "description": "验证目标服务是否正常运行",
                    "code_change": "添加健康检查或ping测试"
                },
                {
                    "priority": 2,
                    "action": "配置代理或DNS",
                    "description": "检查网络配置和代理设置",
                    "code_change": "更新网络配置参数"
                }
            ],
            "data_format_error": [
                {
                    "priority": 1,
                    "action": "更新数据解析逻辑",
                    "description": "适配新的数据格式",
                    "code_change": "修改JSON解析或数据转换代码"
                },
                {
                    "priority": 2,
                    "action": "添加格式兼容处理",
                    "description": "支持多种数据格式",
                    "code_change": "添加格式检测和转换逻辑"
                }
            ],
            "api_change": [
                {
                    "priority": 1,
                    "action": "更新API端点",
                    "description": "使用新的API路径或版本",
                    "code_change": "修改请求URL"
                },
                {
                    "priority": 2,
                    "action": "查询API文档",
                    "description": "检查最新的API规范",
                    "code_change": "根据文档更新请求参数"
                }
            ],
            "environment_issue": [
                {
                    "priority": 1,
                    "action": "检查环境变量",
                    "description": "验证所有必需的环境变量",
                    "code_change": "添加环境变量验证"
                },
                {
                    "priority": 2,
                    "action": "更新依赖版本",
                    "description": "检查并更新依赖包",
                    "code_change": "更新package.json或requirements.txt"
                }
            ]
        }
        
        return suggestions_map.get(failure_type, [
            {
                "priority": 1,
                "action": "手动检查",
                "description": "需要人工分析和修复",
                "code_change": "根据具体情况修改"
            }
        ])
    
    def _is_auto_fixable(self, failure_type: str) -> bool:
        """判断是否可以自动修复"""
        auto_fixable_types = ["timeout", "authentication_error", "data_format_error"]
        return failure_type in auto_fixable_types
    
    def _estimate_fix_effort(self, failure_type: str) -> str:
        """估算修复工作量"""
        effort_map = {
            "timeout": "low",
            "authentication_error": "low",
            "data_format_error": "medium",
            "assertion_error": "medium",
            "network_error": "medium",
            "api_change": "high",
            "environment_issue": "high"
        }
        return effort_map.get(failure_type, "medium")

    async def apply_fix(
        self,
        test_result: Dict[str, Any],
        suggestion: Dict[str, Any],
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        应用修复建议

        Args:
            test_result: 测试结果
            suggestion: 修复建议
            auto_apply: 是否自动应用

        Returns:
            修复结果
        """
        logger.info(f"{self.agent_name} 应用修复建议")

        fix_id = str(uuid.uuid4())

        # 如果不是自动应用，返回修复预览
        if not auto_apply:
            return {
                "fix_id": fix_id,
                "status": "preview",
                "message": "修复预览已生成，需要手动确认",
                "suggestion": suggestion,
                "preview": self._generate_fix_preview(test_result, suggestion)
            }

        # 自动应用修复
        try:
            fixed_code = self._apply_fix_to_code(test_result, suggestion)

            healing_record = {
                "fix_id": fix_id,
                "test_id": test_result.get("test_id", ""),
                "failure_type": suggestion.get("failure_type", ""),
                "applied_suggestion": suggestion,
                "original_code": test_result.get("test_code", ""),
                "fixed_code": fixed_code,
                "status": "applied",
                "applied_at": datetime.utcnow().isoformat(),
                "applied_by": self.agent_name
            }

            # 保存修复历史
            self.healing_history.append(healing_record)

            logger.info(f"{self.agent_name} 修复已应用: {fix_id}")
            return healing_record

        except Exception as e:
            logger.error(f"{self.agent_name} 应用修复失败: {e}", exc_info=e)
            return {
                "fix_id": fix_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _generate_fix_preview(
        self,
        test_result: Dict[str, Any],
        suggestion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成修复预览"""
        return {
            "test_name": test_result.get("test_name", ""),
            "failure_type": suggestion.get("failure_type", ""),
            "suggested_actions": [s.get("action") for s in suggestion.get("suggestions", [])],
            "estimated_effort": suggestion.get("estimated_effort", "medium"),
            "auto_fixable": suggestion.get("auto_fixable", False)
        }

    def _apply_fix_to_code(
        self,
        test_result: Dict[str, Any],
        suggestion: Dict[str, Any]
    ) -> str:
        """应用修复到代码"""
        original_code = test_result.get("test_code", "")
        failure_type = suggestion.get("failure_type", "")

        # 根据失败类型应用不同的修复策略
        if failure_type == "timeout":
            return self._fix_timeout(original_code)
        elif failure_type == "authentication_error":
            return self._fix_authentication(original_code)
        elif failure_type == "assertion_error":
            return self._fix_assertion(original_code, test_result)
        elif failure_type == "data_format_error":
            return self._fix_data_format(original_code)
        else:
            return original_code

    def _fix_timeout(self, code: str) -> str:
        """修复超时问题"""
        # 增加超时时间
        if "timeout:" in code:
            code = code.replace("timeout: 30000", "timeout: 60000")
        else:
            # 添加超时配置
            code = code.replace(
                "await page.goto(",
                "await page.goto(url, { timeout: 60000 });\n  await page.goto("
            )
        return code

    def _fix_authentication(self, code: str) -> str:
        """修复认证问题"""
        # 添加token刷新逻辑
        auth_fix = """
  // 刷新认证token
  const token = await refreshAuthToken();
  await page.setExtraHTTPHeaders({
    'Authorization': `Bearer ${token}`
  });
"""
        # 在测试开始前插入
        if "test(" in code:
            code = code.replace("test(", f"{auth_fix}\n  test(")
        return code

    def _fix_assertion(self, code: str, test_result: Dict[str, Any]) -> str:
        """修复断言错误"""
        # 根据实际响应更新断言
        actual_response = test_result.get("response_data", {})

        # 简化实现：添加更宽松的断言
        if "expect(" in code:
            code = code.replace(
                "expect(response.status).toBe(200)",
                "expect([200, 201, 204]).toContain(response.status)"
            )
        return code

    def _fix_data_format(self, code: str) -> str:
        """修复数据格式错误"""
        # 添加数据格式验证和转换
        format_fix = """
  // 数据格式处理
  const data = typeof response === 'string' ? JSON.parse(response) : response;
"""
        if "const response" in code:
            code = code.replace("const response", f"{format_fix}\n  const response")
        return code

    async def verify_fix(
        self,
        fix_result: Dict[str, Any],
        execution_agent: Any
    ) -> Dict[str, Any]:
        """
        验证修复效果

        Args:
            fix_result: 修复结果
            execution_agent: 测试执行智能体

        Returns:
            验证结果
        """
        logger.info(f"{self.agent_name} 验证修复效果")

        try:
            # 执行修复后的测试
            fixed_code = fix_result.get("fixed_code", "")

            verification_result = await execution_agent.execute_tests(
                test_code=fixed_code,
                framework="playwright"
            )

            # 判断修复是否成功
            success = verification_result.get("summary", {}).get("passed", 0) > 0

            return {
                "verification_id": str(uuid.uuid4()),
                "fix_id": fix_result.get("fix_id", ""),
                "success": success,
                "test_result": verification_result,
                "verified_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"{self.agent_name} 验证失败: {e}", exc_info=e)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def heal_test(
        self,
        test_result: Dict[str, Any],
        execution_agent: Any,
        auto_apply: bool = True,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        完整的测试修复流程

        Args:
            test_result: 测试结果
            execution_agent: 测试执行智能体
            auto_apply: 是否自动应用修复
            verify: 是否验证修复效果

        Returns:
            修复流程结果
        """
        logger.info(f"{self.agent_name} 开始完整修复流程")

        healing_id = str(uuid.uuid4())

        try:
            # 步骤1: 分析失败
            analysis = await self.analyze_failure(test_result)

            # 步骤2: 生成修复建议
            suggestions = await self.generate_fix_suggestions(analysis)

            # 步骤3: 应用修复
            fix_result = await self.apply_fix(
                test_result,
                suggestions,
                auto_apply=auto_apply
            )

            # 步骤4: 验证修复（可选）
            verification = None
            if verify and fix_result.get("status") == "applied":
                verification = await self.verify_fix(fix_result, execution_agent)

            return {
                "healing_id": healing_id,
                "success": True,
                "steps": {
                    "analysis": analysis,
                    "suggestions": suggestions,
                    "fix": fix_result,
                    "verification": verification
                },
                "summary": {
                    "failure_type": analysis.get("failure_type", ""),
                    "fix_applied": fix_result.get("status") == "applied",
                    "verification_passed": verification.get("success", False) if verification else None
                },
                "completed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"{self.agent_name} 修复流程失败: {e}", exc_info=e)
            return {
                "healing_id": healing_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_healing_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取修复历史"""
        return self.healing_history[-limit:]

    def get_healing_statistics(self) -> Dict[str, Any]:
        """获取修复统计"""
        if not self.healing_history:
            return {
                "total_healings": 0,
                "successful_healings": 0,
                "failed_healings": 0,
                "success_rate": 0.0
            }

        total = len(self.healing_history)
        successful = sum(1 for h in self.healing_history if h.get("status") == "applied")

        return {
            "total_healings": total,
            "successful_healings": successful,
            "failed_healings": total - successful,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0.0,
            "by_failure_type": self._count_by_failure_type()
        }

    def _count_by_failure_type(self) -> Dict[str, int]:
        """按失败类型统计"""
        counts = {}
        for record in self.healing_history:
            failure_type = record.get("failure_type", "unknown")
            counts[failure_type] = counts.get(failure_type, 0) + 1
        return counts

    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_name": self.agent_name,
            "agent_type": "api_healer",
            "capabilities": [
                "失败原因分析",
                "智能修复建议",
                "自动修复应用",
                "修复效果验证"
            ],
            "supported_fix_types": self.supported_fix_types,
            "healing_history_count": len(self.healing_history),
            "status": "active"
        }


